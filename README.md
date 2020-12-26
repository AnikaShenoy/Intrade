# Long Short Equity Trading Strategy Python Program

**Thank you to Part Time Larry and Eth Klein Youtube tutorials on the Alpaca API and algorithmic trading.**

Overall structure:

1. Check for market opening
2. Loop: Rebalance the portfolio every minute by making necessary trades 

3. Rank the stocks 

&ensp;&ensp;&ensp;&ensp;&ensp; - Rank by percent change over the last ten minutes (higher is better)

&ensp;&ensp;&ensp;&ensp;&ensp; - Grabs top and bottom quarter of the sorted stock list to get the long and short lists

&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp; - Bottom quarter are shorted

&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp; - Top quarter added to long list

&ensp;&ensp;&ensp;&ensp;&ensp; - Amount to Short vs Long = 30% vs 70% of equity 

&ensp;&ensp;&ensp;&ensp;&ensp; - Determine quantity to long/short

&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp; - qLong = longAmount / Total Price Long

&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp; - qShort = shortAmount / Total Price Short 

4. Remove positions that are no longer in the short/long list by buying/selling respectively
5. Send orders to all remaining stocks in the long and short list 
6. 15 min before market closes, Close all positions by buying shorted stocks and selling if position is long
