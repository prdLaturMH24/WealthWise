from click import DateTime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from InvestmentCategory import InvestmentCategory

class Investment(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    Id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="Id")
    Name: Optional[str] = Field('', alias="Name")
    Type: Optional[str] = Field(InvestmentCategory.Other, alias="Type")
    Amount: Optional[float] = Field(0.0, alias="Amount")
    PurchaseDate: Optional[datetime] = Field(None, alias="PurchaseDate")
    CurrentValue: Optional[float] = Field(0.0, alias="CurrentValue")