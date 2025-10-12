from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from RiskToleranceLevel import RiskToleranceLevel as RiskTolerance
from Investment import Investment
from FinancialGoal import FinancialGoal

class UserProfile(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True
    )
    
    Id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="Id")
    Name: str = Field(..., alias="Name")
    Email: str = Field(..., alias="Email")
    Age: Optional[int] = Field(0,ge=18, le=100, alias="Age")
    MonthlyIncome: Optional[float] = Field(0.0, alias="MonthlyIncome")
    MonthlySavings: Optional[float] = Field(0.0, alias="MonthlySavings")
    RiskTolerance: Optional[str] = Field(RiskTolerance.Conservative, alias="RiskTolerance")
    CurrentInvestments: Optional[List[Investment]] = Field(default_factory=list, alias="CurrentInvestments")
    FinancialGoals: Optional[List[FinancialGoal]] = Field(default_factory=list, alias="FinancialGoals")
