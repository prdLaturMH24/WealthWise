"""
User Profile and Input Models for FinGPT Financial AI Services

These models define the structure for user data, preferences, and goals
that will be used across all three API categories.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, date
from enum import Enum

class RiskTolerance(str, Enum):
    """Risk tolerance levels"""
    Conservative = "Conservative"
    Moderate = "Moderate"
    Aggressive = "Aggressive"
    VeryAggressive = "VeryAggressive"

class InvestmentGoalType(str, Enum):
    """Types of investment goals"""
    RETIREMENT = "Retirement"
    HOME_PURCHASE = "HomePurchase"
    EDUCATION = "Education"
    EMERGENCY_FUND = "EmergencyFund"
    WEALTH_BUILDING = "WealthBuilding"
    DEBT_PAYOFF = "DebtPayoff"
    TRAVEL = "Travel"
    OTHER = "Other"

class EmploymentStatus(str, Enum):
    """Employment status options"""
    Employed = "Employed"
    SelfEmployed = "SelfEmployed"
    Unemployed = "Unemployed"
    Retired = "Retired"
    Student = "Student"

class MarketSector(str, Enum):
    """Market sectors for recommendations"""
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCE = "Finance"
    ENERGY = "Energy"
    CONSUMER_GOODS = "ConsumerGoods"
    REAL_ESTATE = "RealEstate"
    UTILITIES = "Utilities"
    MATERIALS = "Materials"
    INDUSTRIALS = "Industrials"
    TELECOMMUNICATIONS = "Telecommunications"

class UserProfile(BaseModel):
    """Comprehensive user profile for financial AI services"""

    # Basic Demographics
    user_id: str = Field(..., description="Unique user identifier")
    age: int = Field(..., ge=18, le=100, description="User age")
    location: Optional[str] = Field(None, description="User location/country")
    employment_status: EmploymentStatus = Field(..., description="Current employment status")

    # Financial Information
    annual_income: float = Field(..., ge=0, description="Annual income in INR")
    monthly_expenses: float = Field(..., ge=0, description="Monthly expenses in INR")
    current_savings: float = Field(..., ge=0, description="Current total savings")
    current_investments: float = Field(default=0, ge=0, description="Current investment portfolio value")
    monthly_savings_capacity: float = Field(..., ge=0, description="Amount available for savings/investment monthly")

    # Debt Information
    total_debt: float = Field(default=0, ge=0, description="Total outstanding debt")
    monthly_debt_payments: float = Field(default=0, ge=0, description="Monthly debt payments")

    # Risk and Investment Profile
    risk_tolerance: RiskTolerance = Field(..., description="Risk tolerance level")
    investment_experience: int = Field(default=0, ge=0, le=30, description="Years of investment experience")
    preferred_sectors: List[MarketSector] = Field(default=[], description="Preferred market sectors")

    # Time Horizons
    short_term_horizon: Optional[int] = Field(None, ge=1, le=5, description="Short-term investment horizon in years")
    medium_term_horizon: Optional[int] = Field(None, ge=5, le=10, description="Medium-term investment horizon in years")
    long_term_horizon: Optional[int] = Field(None, ge=10, le=50, description="Long-term investment horizon in years")

    # Additional Context
    family_dependents: int = Field(default=0, ge=0, description="Number of financial dependents")
    has_emergency_fund: bool = Field(default=False, description="Whether user has emergency fund")
    retirement_contributions: float = Field(default=0, ge=0, description="Current monthly retirement contributions")

    # Preferences and Constraints
    investment_constraints: List[str] = Field(default=[], description="Any investment constraints or preferences")
    esg_preference: bool = Field(default=False, description="Preference for ESG investments")
    crypto_tolerance: bool = Field(default=False, description="Tolerance for cryptocurrency investments")

class FinancialGoal(BaseModel):
    """Individual financial goal definition"""

    goal_id: str = Field(..., description="Unique goal identifier")
    goal_type: InvestmentGoalType = Field(..., description="Type of financial goal")
    goal_name: str = Field(..., description="Custom name for the goal")
    target_amount: float = Field(..., ge=0, description="Target amount needed")
    current_amount: float = Field(default=0, ge=0, description="Current amount saved towards goal")
    target_date: date = Field(..., description="Target completion date")
    priority: int = Field(..., ge=1, le=10, description="Goal priority (1=highest, 10=lowest)")
    is_flexible: bool = Field(default=True, description="Whether goal timeline is flexible")
    additional_info: Optional[str] = Field(None, description="Additional context about the goal")

class FinancialGoalsList(BaseModel):
    """Collection of user's financial goals"""

    user_id: str = Field(..., description="User identifier")
    goals: List[FinancialGoal] = Field(..., description="List of financial goals")
    total_goal_amount: float = Field(..., ge=0, description="Total amount needed for all goals")
    total_current_amount: float = Field(default=0, ge=0, description="Total amount currently saved")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MarketPreferences(BaseModel):
    """Market analysis and recommendation preferences"""

    # Geographic Preferences
    focus_regions: List[str] = Field(default=["IND"], description="Geographic regions of interest")
    currency_preference: str = Field(default="INR", description="Preferred currency for analysis")

    # Market Data Preferences
    analysis_timeframe: str = Field(default="1Y", description="Preferred analysis timeframe")
    news_sources: List[str] = Field(default=[], description="Preferred news sources")
    data_frequency: str = Field(default="daily", description="Preferred data update frequency")

    # Analysis Preferences
    technical_analysis: bool = Field(default=True, description="Include technical analysis")
    fundamental_analysis: bool = Field(default=True, description="Include fundamental analysis")
    sentiment_analysis: bool = Field(default=True, description="Include sentiment analysis")

    # Notification Preferences
    alert_threshold: float = Field(default=5.0, ge=0, le=100, description="Alert threshold percentage")
    email_notifications: bool = Field(default=False, description="Enable email notifications")
    push_notifications: bool = Field(default=True, description="Enable push notifications")

class CurrentPortfolio(BaseModel):
    """User's current investment portfolio"""

    portfolio_id: str = Field(..., description="Unique portfolio identifier")
    total_value: float = Field(..., ge=0, description="Total portfolio value")
    cash_balance: float = Field(default=0, ge=0, description="Available cash balance")
    holdings: List[Dict] = Field(default=[], description="List of portfolio holdings")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    # Portfolio Metrics
    total_cost_basis: float = Field(default=0, ge=0, description="Total cost basis of investments")
    unrealized_gain_loss: float = Field(default=0, description="Unrealized gains/losses")
    realized_gain_loss_ytd: float = Field(default=0, description="Realized gains/losses year-to-date")

class UserContext(BaseModel):
    """Complete user context for AI services"""

    profile: UserProfile
    goals: Optional[FinancialGoalsList] = None
    portfolio: Optional[CurrentPortfolio] = None
    preferences: Optional[MarketPreferences] = None
    session_id: Optional[str] = None
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
