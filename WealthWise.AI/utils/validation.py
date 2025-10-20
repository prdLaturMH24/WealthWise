"""
Input validation utilities for FinGPT Financial AI Services
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None # pyright: ignore[reportAssignmentType]

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

def validate_user_profile(profile) -> ValidationResult:
    """Validate user profile data"""
    errors = []
    warnings = []

    try:
        # Age validation
        if profile.age < 18 or profile.age > 100:
            errors.append("Age must be between 18 and 100")

        # Income validation
        if profile.annual_income <= 0:
            errors.append("Annual income must be greater than 0")
        elif profile.annual_income > 10_000_000:
            warnings.append("Annual income seems unusually high")

        # Expense validation
        if profile.monthly_expenses < 0:
            errors.append("Monthly expenses cannot be negative")
        elif profile.monthly_expenses * 12 > profile.annual_income * 1.2:
            errors.append("Monthly expenses cannot significantly exceed annual income")

        # Savings validation
        if profile.current_savings < 0:
            errors.append("Current savings cannot be negative")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    except Exception as e:
        return ValidationResult(is_valid=False, errors=[f"Validation error: {str(e)}"])

def validate_financial_goals(goals) -> ValidationResult:
    """Validate financial goals data"""
    errors = []
    warnings = []

    try:
        if not goals.goals:
            errors.append("At least one financial goal is required")
            return ValidationResult(is_valid=False, errors=errors)

        for i, goal in enumerate(goals.goals):
            goal_prefix = f"Goal {i+1}"

            if goal.target_amount <= 0:
                errors.append(f"{goal_prefix}: Target amount must be greater than 0")

            if goal.current_amount < 0:
                errors.append(f"{goal_prefix}: Current amount cannot be negative")
            elif goal.current_amount > goal.target_amount:
                errors.append(f"{goal_prefix}: Current amount cannot exceed target amount")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    except Exception as e:
        return ValidationResult(is_valid=False, errors=[f"Validation error: {str(e)}"])

def validate_portfolio(portfolio) -> ValidationResult:
    """Validate portfolio data"""
    errors = []
    warnings = []

    try:
        if portfolio.total_value < 0:
            errors.append("Total portfolio value cannot be negative")

        if portfolio.cash_balance < 0:
            errors.append("Cash balance cannot be negative")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    except Exception as e:
        return ValidationResult(is_valid=False, errors=[f"Validation error: {str(e)}"])

def validate_market_preferences(preferences) -> ValidationResult:
    """Validate market preferences"""
    errors = []
    warnings = []

    try:
        if preferences.alert_threshold < 0 or preferences.alert_threshold > 100:
            errors.append("Alert threshold must be between 0 and 100")

        valid_timeframes = ['1D', '1W', '1M', '3M', '6M', '1Y', '2Y', '5Y']
        if preferences.analysis_timeframe not in valid_timeframes:
            errors.append(f"Invalid analysis timeframe: {preferences.analysis_timeframe}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    except Exception as e:
        return ValidationResult(is_valid=False, errors=[f"Validation error: {str(e)}"])
