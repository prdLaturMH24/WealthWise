from typing import Optional, List
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict
from AdviceCategory import AdviceCategory

class FinancialAdvice(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        json_schema_extra = {
            "example": {
                "Id": "123e4567-e89b-12d3-a456-426614174000",
                "Title": "Balanced Investment Strategy",
                "Description": "A diversified approach to long-term wealth building",
                "Category": "Investment",
                "ProjectedImpact": 15000.0,
                "ActionItems": ["Allocate 60% to stocks", "40% to bonds"],
                "GeneratedDate": "2024-01-01T00:00:00Z"
            }
            }
    )
    
    Id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="Id")
    Title: str = Field(..., alias="Title")
    Description: str = Field(..., alias="Description")
    Category: AdviceCategory = Field(AdviceCategory.Investment, alias="Category")
    ProjectedImpact: Optional[float] = Field(None, alias="ProjectedImpact")
    ActionItems: List[str] = Field(default_factory=list, alias="ActionItems")
    GeneratedDate: datetime = Field(default_factory=datetime.utcnow, alias="GeneratedDate")