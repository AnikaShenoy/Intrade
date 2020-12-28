import time
import alpaca_trade_api as tradeapi
from config import *

def initialize():
    global alpaca, allStocks
    global long, short
    global qLong, qShort
    global adjustedQLong, adjustedQShort
    global blacklist
    global longAmount, shortAmount
    global timeToClose

    alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, "v2")
    # stock universe - equities that I'm focusing on right now
    stockUniverse = ["DOMO", "TLRY", "SQ", "MRO", "AAPL", "GM", "SNAP", "SHOP", "SPLK",
                     "BA", "AMZN", "SUI", "SUN", "TSLA", "CGC", "SPWR", "NIO", "CAT", "MSFT",
                     "PANW", "OKTA", "TWTR", "TM", "RTN", "ATVI", "GS", "BAC", "MS", "TWLO", "QCOM"]
    # Format the allStocks variable for use in the class
    allStocks = []
    for stock in stockUniverse:
        allStocks.append([stock, 0])

    long = []
    short = []
    qShort = None
    qLong = None
    adjustedQLong = None
    blacklist = set()
    adjustedQShort = None
    longAmount = 0
    shortAmount = 0
    timeToClose = None

def run():
    # Cancel existing orders so they don't impact buying power
    orders = alpaca.list_orders(status="open")
    for order in orders:
        alpaca.cancel_order(order.id)

    # Wait for market to open
    print("Waiting for market to open...")
    awaitMarketOpen()
    print("Market opened.")

    # Rebalance the portfolio every minute making necessary trades
    # Rebalance a portfolio: periodically buying/selling assets to maintain level of asset allocation
    while True:
        #Figure out when market will close to prepare to sell beforehand
        clock = alpaca.get_clock()
        timeToClose = ((clock.next_close - clock.timestamp).total_seconds())

        if (timeToClose < (60*15)):
            # Close all positions when 15 minutes until market close.
            print("Market closing soon. Closing positions")
            positions = alpaca.list_positions()
            for position in positions:
                # if there are open positions, if long -> sell, if short -> buy
                if position.side == "long":
                    orderSide = 'sell'
                else:
                    orderSide = "buy"
                # submit the order with the amount of shares that are either held or sold
                qty = abs(int(float(position.qty)))
                respSO = []
                submitOrder(qty, position.symbol, orderSide, respSO)
            # Run script again after market close for the next trading day.
            print("Sleeping until market close (15 minutes).")
            time.sleep(60*15)
        else:
            rebalance()
            time.sleep(60)

def awaitMarketOpen():
    isOpen = alpaca.get_clock().is_open
    while not isOpen:
        clock = alpaca.get_clock()
        timeToOpen = ((clock.next_open - clock.timestamp).total_seconds())//60
        print(str(timeToOpen) + " minutes until market opens.")
        time.sleep(60)
        isOpen = alpaca.get_clock().is_open

def rebalance():
    global blacklist, long, short, qShort, qLong
    global adjustedQLong, adjustedQShort
    rerank()

    # Clear existing orders again
    orders = alpaca.list_orders(status="open")
    for order in orders:
        alpaca.cancel_order(order.id)
    print("We are taking a long position in: " + str(long))

    # Remove positions that are no longer in the short or long list
    # and make a list of positions that do not need to change.
    # Adjust position quantities if needed
    executed = [[],[]]
    positions = alpaca.list_positions()
    blacklist.clear() # clear the set named blacklist
    for position in positions:
        # Iterate through positions. If it's long -> sell, if it's short -> buy
        if position.symbol not in long:
            # Position is not in the long list
            if position.symbol not in short:
                #position not in short list either. Clear position.
                if position.side == "long":
                    side = "sell"
                else:
                    side = "buy"
                respSO = []
                submitOrder(abs(int(float(position.qty))), position.symbol, side, respSO)
            else:
                # Position in short list
                if position.side == "long":
                    # Position changed from long to short. Clear long position to prepare for short position.
                    side = "sell"
                    respSO = []
                    submitOrder(int(float(position.qty)), position.symbol, side, respSO)
                else:
                    if abs(int(float(position.qty))) == qShort:
                        # Position quantity is equal to the quantity_short (therefore, position is where we want it). Pass for now
                        pass
                    else:
                        # Need to adjust position amount
                        diff = abs(int(float(position.qty))) - qShort
                        if diff > 0:
                            # Too many short positions. Buy some back to rebalance.
                            side = "buy"
                        else:
                            # Too little short positions. Sell some more.
                            side = "sell"
                        respSO = []
                        submitOrder(abs(diff), position.symbol, side, respSO)
                    executed[1].append(position.symbol)
                    blacklist.add(position.symbol) # add to blacklist once stock has been removed
        else:
            # Position in long list
            if position.side == "short":
                # Position changed from short to long. Clear short position to prepare for long position
                respSO = []
                submitOrder(abs(int(float(position.qty))), position.symbol, "buy", respSO)
            else:
                if int(float(position.qty)) == qLong:
                    # Long Position is where we want it. Pass for now.
                    pass
                else:
                    # Need to adjust position amount.
                    diff = abs(int(float(position.qty))) - qLong
                    if diff > 0:
                        # Too many long positions. Sell some to rebalance.
                        side = "sell"
                    else:
                        # Too little long positions. Buy some more.
                        side = "buy"
                    respSO = []
                    submitOrder(abs(diff), position.symbol, side, respSO)
                executed[0].append(position.symbol)
                blacklist.add(position.symbol) # add to blacklist set once stock has been removed

    # Send order to all remaining stocks in the long and short list
    respSendBOLong = []
    sendBatchOrder(qLong, long, "buy", respSendBOLong)
    respSendBOLong[0][0] += executed[0]

    if len(respSendBOLong[0][1]) > 0:
        # Handle rejected or incomplete orders and determined the new quantities to purchase
        respGetTPLong = []
        getTotalPrice(respSendBOLong[0][0], respGetTPLong)
        if respGetTPLong[0] > 0:
            adjustedQLong = longAmount // respGetTPLong[0]
        else:
            adjustedQLong = -1
    else:
        adjustedQLong = -1

    respSendBOShort = []
    sendBatchOrder(qShort, short, "sell", respSendBOShort)
    respSendBOShort[0][0] += executed[1]

    if len(respSendBOShort[0][1]) > 0:
        # Handle rejected or incomplete orders and determine new quantities to purchase.
        respGetTPShort = []
        getTotalPrice(respSendBOShort[0][0], respGetTPShort)
        if respGetTPShort[0] > 0:
            adjustedQShort = shortAmount // respGetTPShort[0]
        else:
            adjustedQShort = -1
    else:
        adjustedQShort = -1

    # Reorder stocks that didn't throw an error so that the equity quota is reached.
    if adjustedQLong > -1:
        qLong = int(adjustedQLong - qLong)
        for stock in respSendBOLong[0][0]:
            respResendBOLong = []
            submitOrder(qLong, stock, "buy", respResendBOLong)
    if adjustedQShort > -1:
        qShort = int(adjustedQShort - qShort)
        for stock in respSendBOShort[0][0]:
            respResendBOShort = []
            submitOrder(qShort, stock, "sell", respResendBOShort)

# Rerank all stocks to adjust longs and shorts
def rerank():
    global long, short, longAmount, shortAmount, qLong, qShort
    rank()

    #Grabs the top and bottom quarter of the sorted stock list to get the long and short lists
    longShortAmount = len(allStocks) // 4
    long = []
    short = []
    for i, stockField in enumerate(allStocks):
        if i < longShortAmount:
            short.append(stockField[0])
        elif i > len(allStocks) - 1 - longShortAmount:
            long.append(stockField[0])
        else:
            continue
    # Determine amount to long/short based on total stock price of each bucket
    equity = int(float(alpaca.get_account().equity))
    shortAmount = equity * 0.30
    longAmount = equity + shortAmount

    respGetTPLong = []
    getTotalPrice(long, respGetTPLong)

    respGetTPShort = []
    getTotalPrice(short, respGetTPShort)

    qLong = int(longAmount // respGetTPLong[0])
    qShort = int(shortAmount // respGetTPShort[0])

# Get the total price of the array of input stocks
def getTotalPrice(stocks, resp):
    totalPrice = 0
    for stock in stocks:
        bars = alpaca.get_barset(stock, "minute", 1)
        totalPrice += bars[stock][0].c
    resp.append(totalPrice)

# Submit a batch order that returns completed and uncompleted orders
def sendBatchOrder(qty, stocks, side, resp):
    executed = []
    incomplete = []
    for stock in stocks:
        if blacklist.isdisjoint({stock}):
            respSO = []
            submitOrder(qty, stock, side, respSO)
            if not respSO[0]:
                # Stock order did not go through, add it to incomplete
                incomplete.append(stock)
            else:
                executed.append(stock)
            respSO.clear()
    resp.append([executed, incomplete])

# Submit an order if quantity is above 0
def submitOrder(qty, stock, side, resp):
    if qty > 0:
        try:
            alpaca.submit_order(stock,qty,side,"market","day")
            print("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
            resp.append(True)
        except:
            print("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
            resp.append(False)
    else:
        print("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
        resp.append(True)

#Get percent changes of the stock prices over the past ten minutes
def getPercentChanges():
    length = 10
    for i, stock in enumerate(allStocks):
        bars = alpaca.get_barset(stock[0], "minute", length)
        allStocks[i][1] = (bars[stock[0]][len(bars[stock[0]]) - 1].c - bars[stock[0]][0].o) / bars[stock[0]][0].o

# Mechanism used to rank the stocks, the basis of the Long-Short Equity Strategy.
# Rank all stocks by percent change over the past 10 minutes (higher is better).
def rank():
    getPercentChanges()
    # Sort the stocks in place by the percent change field (marked by pc)
    allStocks.sort(key=lambda x: x[1]) #sort list x based on the second element (which is pc)

if __name__ == "__main__":
    initialize()
    run()