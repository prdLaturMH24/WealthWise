from enum import Enum

class RiskToleranceLevel(str, Enum):
    Conservative = "Conservative"
    Moderate = "Moderate"
    Aggressive = "Aggressive"