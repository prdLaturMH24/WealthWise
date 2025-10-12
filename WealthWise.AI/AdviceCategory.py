from enum import Enum

class AdviceCategory(str, Enum):
    Savings = "Savings"
    Investment = "Investment"
    Budgeting = "Budgeting"
    DebtManagement = "DebtManagement"
    RetirementPlanning = "RetirementPlanning"
    TaxOptimization = "TaxOptimization"