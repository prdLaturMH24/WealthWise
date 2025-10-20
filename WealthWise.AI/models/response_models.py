"""
Response Models for FinGPT Financial AI Services

These models define the structure for API responses across all three categories:
1. AI Financial Advisor responses
2. AI Recommendations responses  
3. AI Finance Goal Planner responses
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum

class ConfidenceLevel(str, Enum):
    """Confidence levels for AI recommendations"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class ActionPriority(str, Enum):
    """Priority levels for recommended actions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RecommendationType(str, Enum):
    """Types of recommendations"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REDUCE = "reduce"
    INCREASE = "increase"
    AVOID = "avoid"

# Base response model
class APIResponse(BaseModel):
    """Base API response structure"""

    success: bool = Field(..., description="Whether the request was successful")
    timestamp: Union[datetime, str] = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    model_used: Optional[str] = Field(None, description="AI model version used")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamps(cls, v):
        """Convert string timestamps to datetime objects"""
        if isinstance(v, str):
            try:
                if v.endswith("Z"):
                    v = v[:-1] + "+00:00"
                return datetime.fromisoformat(v)
            except ValueError:
                from dateutil import parser
                return parser.isoparse(v)
        elif isinstance(v, datetime):
            return v
        return v

# Category 1: AI Financial Advisor Response Models

class ActionItem(BaseModel):
    """Individual action item recommendation"""

    title: str = Field(..., description="Action item title")
    description: str = Field(..., description="Detailed description")
    priority: ActionPriority = Field(..., description="Priority level")
    category: str = Field(..., description="Action category")
    timeline: str = Field(..., description="Recommended timeline")
    estimated_impact: Optional[str] = Field(None, description="Expected impact description")
    resources_needed: List[str] = Field(default=[], description="Resources or tools needed")
    success_metrics: List[str] = Field(default=[], description="How to measure success")

class RiskAssessment(BaseModel):
    """Risk assessment details"""

    overall_risk_level: str = Field(..., description="Overall risk level assessment")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    mitigation_strategies: List[str] = Field(..., description="Risk mitigation recommendations")
    risk_tolerance_alignment: bool = Field(..., description="Whether current approach aligns with risk tolerance")
    stress_test_results: Optional[Dict[str, Any]] = Field(None, description="Portfolio stress test results")

class PortfolioAnalysis(BaseModel):
    """Portfolio analysis results"""

    current_allocation: Dict[str, float] = Field(..., description="Current asset allocation percentages")
    recommended_allocation: Dict[str, float] = Field(..., description="Recommended asset allocation")
    diversification_score: int = Field(..., ge=0, le=100, description="Portfolio diversification score")
    performance_metrics: Dict[str, float] = Field(..., description="Portfolio performance metrics")
    rebalancing_needed: bool = Field(..., description="Whether rebalancing is recommended")
    underperforming_assets: List[str] = Field(default=[], description="Assets underperforming benchmarks")
    optimization_opportunities: List[str] = Field(default=[], description="Portfolio optimization opportunities")

class FinancialAdviceResponse(APIResponse):
    """Response for personal financial advice requests"""

    advice_summary: str = Field(..., description="Executive summary of advice")
    detailed_analysis: str = Field(..., description="Detailed financial analysis")
    action_items: List[ActionItem] = Field(..., description="Recommended action items")
    risk_assessment: RiskAssessment = Field(..., description="Risk analysis and recommendations")
    portfolio_analysis: Optional[PortfolioAnalysis] = Field(None, description="Portfolio analysis if applicable")
    confidence_level: ConfidenceLevel = Field(..., description="AI confidence in recommendations")
    follow_up_timeline: str = Field(..., description="When to reassess or follow up")
    additional_resources: List[str] = Field(default=[], description="Educational resources and tools")
    # Financial projections
    projected_net_worth: Optional[Dict[str, float]] = Field(None, description="Net worth projections over time")
    savings_projections: Optional[Dict[str, float]] = Field(None, description="Savings growth projections")
    retirement_readiness: Optional[Dict[str, Any]] = Field(None, description="Retirement readiness assessment")

# Category 2: AI Recommendations Response Models

class MarketInsight(BaseModel):
    """Individual market insight"""

    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed insight description")
    impact_level: str = Field(..., description="Expected market impact level")
    timeframe: str = Field(..., description="Relevant timeframe")
    sectors_affected: List[str] = Field(default=[], description="Market sectors affected")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    supporting_data: Dict[str, Any] = Field(default={}, description="Supporting data and metrics")

class NewsAnalysis(BaseModel):
    """Financial news analysis result"""

    headline: str = Field(..., description="News headline")
    source: str = Field(..., description="News source")
    published_date: datetime = Field(..., description="Publication date")
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment score -1 to 1")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score 0-1")
    key_entities: List[str] = Field(default=[], description="Key entities mentioned")
    impact_analysis: str = Field(..., description="Potential market impact analysis")
    related_symbols: List[str] = Field(default=[], description="Related stock symbols")
    action_implications: List[str] = Field(default=[], description="Potential action implications")

class SectorRecommendation(BaseModel):
    """Sector-specific investment recommendation"""

    sector_name: str = Field(..., description="Market sector name")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence in recommendation")
    rationale: str = Field(..., description="Reasoning behind recommendation")
    key_drivers: List[str] = Field(..., description="Key factors driving the recommendation")
    potential_risks: List[str] = Field(..., description="Potential risks to consider")
    time_horizon: str = Field(..., description="Investment time horizon")
    allocation_suggestion: Optional[float] = Field(None, ge=0, le=100, description="Suggested allocation percentage")
    top_picks: List[str] = Field(default=[], description="Top stock picks in sector")

class RecommendationResponse(APIResponse):
    """Response for AI recommendations requests"""

    recommendation_type: str = Field(..., description="Type of recommendation provided")
    executive_summary: str = Field(..., description="Executive summary of recommendations")

    # Market insights
    market_insights: List[MarketInsight] = Field(default=[], description="Market insights and trends")

    # News analysis
    news_analysis: List[NewsAnalysis] = Field(default=[], description="Financial news analysis")

    # Sector recommendations
    sector_recommendations: List[SectorRecommendation] = Field(default=[], description="Sector-specific recommendations")

    # Overall market sentiment
    market_sentiment: Dict[str, Any] = Field(default={}, description="Overall market sentiment analysis")

    # Economic indicators
    economic_indicators: Dict[str, float] = Field(default={}, description="Relevant economic indicators")

    # Risk factors
    current_risk_factors: List[str] = Field(default=[], description="Current market risk factors")

    # Opportunities
    identified_opportunities: List[str] = Field(default=[], description="Investment opportunities identified")

# Category 3: AI Finance Goal Planner Response Models

class GoalStrategy(BaseModel):
    """Strategy for achieving a specific financial goal"""

    goal_id: str = Field(..., description="Goal identifier")
    goal_name: str = Field(..., description="Goal name")
    strategy_summary: str = Field(..., description="Overall strategy summary")
    monthly_savings_required: float = Field(..., ge=0, description="Required monthly savings")
    recommended_investments: List[str] = Field(..., description="Recommended investment vehicles")
    risk_level: str = Field(..., description="Risk level for this goal")
    probability_of_success: float = Field(..., ge=0, le=1, description="Probability of achieving goal")

    # Timeline and milestones
    milestones: List[Dict[str, Any]] = Field(default=[], description="Goal milestones")
    progress_tracking: Dict[str, Any] = Field(default={}, description="Progress tracking metrics")

    # Optimization suggestions
    optimization_suggestions: List[str] = Field(default=[], description="Ways to optimize the strategy")
    alternative_scenarios: List[Dict[str, Any]] = Field(default=[], description="Alternative scenarios and outcomes")

class SavingsOptimization(BaseModel):
    """Savings optimization recommendations"""

    current_savings_rate: float = Field(..., description="Current savings rate percentage")
    optimal_savings_rate: float = Field(..., description="Recommended optimal savings rate")
    savings_reallocation: Dict[str, float] = Field(..., description="How to reallocate savings across goals")
    automation_recommendations: List[str] = Field(default=[], description="Savings automation suggestions")
    tax_optimization: List[str] = Field(default=[], description="Tax optimization strategies")

    # Impact projections
    projected_savings_growth: Dict[str, float] = Field(default={}, description="Projected savings growth over time")
    compound_interest_impact: float = Field(..., description="Expected compound interest impact")

class ProgressTracking(BaseModel):
    """Goal progress tracking information"""

    goal_id: str = Field(..., description="Goal identifier")
    current_progress_percentage: float = Field(..., ge=0, le=100, description="Current progress percentage")
    on_track_status: bool = Field(..., description="Whether goal is on track")
    deviation_amount: Optional[float] = Field(None, description="Amount ahead/behind target")
    recommended_adjustments: List[str] = Field(default=[], description="Recommended adjustments")
    next_milestone: Optional[Dict[str, Any]] = Field(None, description="Next milestone details")
    completion_probability: float = Field(..., ge=0, le=1, description="Probability of completion")

class GoalPlannerResponse(APIResponse):
    """Response for AI Finance Goal Planner requests"""

    planner_type: str = Field(..., description="Type of planning performed")
    overall_strategy_summary: str = Field(..., description="Overall financial strategy summary")

    # Individual goal strategies
    goal_strategies: List[GoalStrategy] = Field(default=[], description="Strategies for each goal")

    # Savings optimization
    savings_optimization: SavingsOptimization = Field(..., description="Savings optimization recommendations")

    # Progress tracking
    progress_tracking: List[ProgressTracking] = Field(default=[], description="Progress tracking for each goal")

    # Integrated planning insights
    goal_conflicts: List[str] = Field(default=[], description="Conflicts between goals")
    synergy_opportunities: List[str] = Field(default=[], description="Synergies between goals")
    priority_adjustments: List[str] = Field(default=[], description="Recommended priority adjustments")

    # Financial projections
    net_worth_projection: Dict[str, float] = Field(default={}, description="Net worth projections")
    cash_flow_projections: Dict[str, float] = Field(default={}, description="Cash flow projections")

    # Risk and scenario analysis
    scenario_analysis: Dict[str, Any] = Field(default={}, description="Different scenario outcomes")
    stress_test_results: Dict[str, Any] = Field(default={}, description="Stress test results for goals")

    # Actionable next steps
    immediate_actions: List[ActionItem] = Field(default=[], description="Immediate actions to take")
    quarterly_reviews: List[str] = Field(default=[], description="Items to review quarterly")

# Error response models
class ErrorDetail(BaseModel):
    """Error detail information"""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")

class ErrorResponse(APIResponse):
    """Error response structure"""

    success: bool = Field(default=False)
    error: str = Field(..., description="Error type")
    details: List[ErrorDetail] = Field(default=[], description="Detailed error information")
    suggestion: Optional[str] = Field(None, description="Suggestion to fix the error")

class Message(BaseModel):
    role: str
    content: str
    reasoning: Optional[Any] = None
    tool_call_id: Optional[Any] = None
    tool_calls: Optional[Any] = None

class Choice(BaseModel):
    finish_reason: str
    index: int
    message: Message
    logprobs: Optional[Any] = None

class Usage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

class FinancialChatApiResponse(BaseModel):
    choices: List[Choice]
    created: int
    id: str
    model: str
    system_fingerprint: Optional[Any] = None
    usage: Usage

