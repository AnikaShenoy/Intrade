import numpy as np
import scipy.stats as si
import sympy as sy
from sympy.stats import Normal, cdf
from sympy import init_printing
init_printing()


def black_scholes(S, X, T, r, sig, option):

    # S is the spot price of the asset
    # T is the maturity of the option
    # K is the strike prive of the asset
    # r is the interest rate (assume constant)
    # sig is the volatility (standard deviation of asset returns)


    d1 = (np.log(S/X) + (r + ((sig**2)/2))*T)/(sig * (T**(1/2)))
    d2 = (np.log(S/X) + (r - ((sig**2)/2))*T)/(sig * (T**(1/2)))
    res = 0
    if option == "call":
        res = S * N(d1) - X * np.exp(-r*T) * N(d2)
    elif option == "put":
        res = -S * N(-d1) + X * np.exp(-r*T) * N(-d2)
    return res

def N(d):

    # return cumulative normal distribution for the standard normal distribution
    # probability that the number is <= d

    return si.norm.cdf(d, 0.0, 1.0)