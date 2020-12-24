import numpy as np
import scipy.stats as si
import sympy as sy
from sympy.stats import Normal, cdf
from sympy import init_printing
init_printing()


def black_scholes(S, X, T, r, sig, option):
    d1 = (np.log(S/X) + (r + ((sig**2)/2))*T)/(sig * (T**(1/2)))
    d2 = (np.log(S/X) + (r - ((sig**2)/2))*T)/(sig * (T**(1/2)))
    res = 0
    if option == "call":
        res = S * N(d1) - X * np.exp(-r*T) * N(d2)
    elif option == "put":
        res = -S * N(-d1) + X * np.exp(-r*T) * N(-d2)
    return res

def N(d):
    return si.norm.cdf(d, 0.0, 1.0)
    # return cumulative normal distribution for the standard normal distribution
    # probability that the number is <= d
