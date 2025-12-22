import pandas as pd
import numpy as np
import math

def loan(initial_capital, monthly_payment, annual_interest_rate, years):
    """
    Calculate the remaining capital of a loan after a given number of years.
    Also calculate the total amount of interest paid.
    Parameters
    ----------
    initial_capital : float
        The initial capital of the loan.
    monthly_payment : float
        The monthly payment of the loan.
    annual_interest_rate : float
        The annual interest rate of the loan.
    years : int
        The number of years of the loan.
    Returns
    -------
    remaining_capital : float
        The remaining capital of the loan after the given number of years.
    total_interest : float
        The total amount of interest paid.
    """
    total_interest = 0
    for i in range(years * 12):
        interest = initial_capital * annual_interest_rate / 12
        total_interest += interest
        initial_capital -= monthly_payment
    remaining_capital = initial_capital
    return remaining_capital, total_interest
    
    