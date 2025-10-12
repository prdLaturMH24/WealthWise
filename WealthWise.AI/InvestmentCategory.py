from enum import Enum

class InvestmentCategory(str, Enum):
    Stocks = "Stocks"
    Bonds = "Bonds"
    MutualFunds = "MutualFunds"
    RealEstate = "RealEstate"
    Cryptocurrency = "Cryptocurrency"
    BankDeposits = "BankDeposits",
    RecurringDeposits = "RecurringDeposits",
    Other = "Other"
