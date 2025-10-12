from typing import Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict

class FinancialGoal(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    Id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="Id")
    Name: Optional[str] = Field('', alias="Name")
    Description: Optional[str] = Field('', alias="Description")
    TargetAmount: Optional[float] = Field(0.0, alias="TargetAmount")
    TargetDate: Optional[datetime] = Field(None, alias="TargetDate")
    Priority: Optional[str] = Field(None, alias="Priority")
    Status: Optional[str] = Field(None, alias="Status")