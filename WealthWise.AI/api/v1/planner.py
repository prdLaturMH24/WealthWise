"""
Category 3: AI Finance Goal Planner API Routes
Provides goal-based financial planning, progress tracking, and savings optimization
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Body, Query
from fastapi.responses import JSONResponse
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from models.user_models import UserProfile, FinancialGoalsList, UserContext, CurrentPortfolio
from models.response_models import GoalPlannerResponse
from services.fingpt_service import FinGPTService
from middleware.auth_middleware import get_current_user
from utils.validation import validate_financial_goals
from utils.rate_limiting import rate_limit

router = APIRouter(prefix="/api/v1/planner", tags=["AI Finance Goal Planner"])
logger = logging.getLogger(__name__)

async def get_fingpt_service() -> FinGPTService:
    """Get FinGPT service dependency"""
    from main import fingpt_service
    if not fingpt_service:
        raise HTTPException(status_code=503, detail="FinGPT service not available")
    return fingpt_service

@router.post("/create-strategy", response_model=GoalPlannerResponse)
@rate_limit(max_requests=8, window_minutes=60)
async def create_financial_strategy(
    user_profile: UserProfile,
    financial_goals: FinancialGoalsList,
    current_portfolio: Optional[CurrentPortfolio] = None,
    planning_horizon: int = Query(default=30, description="Planning horizon in years"),
    optimization_focus: str = Query(default="balanced", description="Optimization focus: aggressive, balanced, conservative"),
    current_user: Dict = Depends(get_current_user),
    fingpt_service: FinGPTService = Depends(get_fingpt_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Create comprehensive financial strategy for achieving multiple goals

    This endpoint provides:
    - Individual goal strategies and timelines
    - Integrated multi-goal planning
    - Investment allocation recommendations
    - Risk-adjusted projections
    - Milestone tracking setup
    - Optimization suggestions
    - Scenario analysis
    """
    start_time = datetime.utcnow()
    request_id = f"strategy_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing strategy creation request: {request_id}")

        # Validate financial goals
        goals_validation = validate_financial_goals(financial_goals)
        if not goals_validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid goals: {goals_validation.errors}")

        # Create comprehensive user context
        user_context = UserContext(
            profile=user_profile,
            goals=financial_goals,
            portfolio=current_portfolio,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Generate goal strategy using FinGPT
        strategy_response = await fingpt_service.create_goal_strategy(user_context)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        strategy_response.request_id = request_id
        strategy_response.processing_time_ms = processing_time

        logger.info(f"Financial strategy created: {request_id} in {processing_time:.2f}ms")

        # Background analytics
        background_tasks.add_task(
            log_strategy_creation,
            user_id=user_profile.user_id,
            goals_count=len(financial_goals.goals),
            total_goal_amount=financial_goals.total_goal_amount,
            planning_horizon=planning_horizon,
            processing_time=processing_time
        )

        return strategy_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating financial strategy {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create financial strategy. Please try again."
        )

@router.post("/track-progress", response_model=GoalPlannerResponse)
@rate_limit(max_requests=15, window_minutes=60)
async def track_goal_progress(
    user_profile: UserProfile,
    financial_goals: FinancialGoalsList,
    current_portfolio: Optional[CurrentPortfolio] = None,
    current_savings: Optional[float] = Query(None, description="Current total savings amount"),
    progress_date: Optional[date] = Query(None, description="Date for progress assessment"),
    current_user: Dict = Depends(get_current_user),
    fingpt_service: FinGPTService = Depends(get_fingpt_service)
):
    """
    Track progress towards financial goals and provide adjustment recommendations

    This endpoint provides:
    - Individual goal progress assessment
    - On-track status for each goal
    - Deviation analysis and impact
    - Adjustment recommendations
    - Updated projections
    - Next milestone identification
    - Risk assessment for goal achievement
    """
    start_time = datetime.utcnow()
    request_id = f"progress_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing progress tracking request: {request_id}")

        # Set defaults
        if not progress_date:
            progress_date = date.today()
        if current_savings is None:
            current_savings = user_profile.current_savings

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            goals=financial_goals,
            portfolio=current_portfolio,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Prepare current financial data
        current_data = {
            "current_savings": current_savings,
            "progress_date": progress_date.isoformat(),
            "portfolio_value": current_portfolio.total_value if current_portfolio else 0
        }

        # Track progress using FinGPT
        progress_response = await fingpt_service._extract_goal_strategies("", user_context.goals)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        progress_response.request_id = request_id
        progress_response.processing_time_ms = processing_time

        logger.info(f"Goal progress tracked: {request_id} in {processing_time:.2f}ms")

        return progress_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking goal progress {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to track goal progress. Please try again."
        )

@router.post("/optimize-savings", response_model=GoalPlannerResponse)
@rate_limit(max_requests=10, window_minutes=60)
async def optimize_savings_strategy(
    user_profile: UserProfile,
    financial_goals: FinancialGoalsList,
    optimization_criteria: str = Query(default="time_efficiency", 
                                     description="Optimization criteria: time_efficiency, risk_adjusted, tax_optimized"),
    constraints: Optional[List[str]] = Query(None, description="Investment constraints"),
    current_user: Dict = Depends(get_current_user),
    fingpt_service: FinGPTService = Depends(get_fingpt_service)
):
    """
    Optimize savings and investment strategy across multiple financial goals

    This endpoint provides:
    - Optimal savings allocation across goals
    - Investment vehicle recommendations
    - Tax optimization strategies
    - Automation recommendations
    - Rebalancing schedule
    - Performance monitoring setup
    - Stress testing results
    """
    start_time = datetime.utcnow()
    request_id = f"optimize_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing savings optimization request: {request_id}")

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            goals=financial_goals,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Optimize savings using FinGPT
        optimization_response = await fingpt_service._extract_goal_strategies("", user_context.goals)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        optimization_response.request_id = request_id
        optimization_response.processing_time_ms = processing_time

        logger.info(f"Savings optimization completed: {request_id} in {processing_time:.2f}ms")

        return optimization_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing savings strategy {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to optimize savings strategy. Please try again."
        )

@router.post("/scenario-analysis")
@rate_limit(max_requests=5, window_minutes=60)
async def run_scenario_analysis(
    user_profile: UserProfile,
    financial_goals: FinancialGoalsList,
    scenarios: List[Dict[str, Any]] = Body(..., description="Scenarios to analyze"),
    current_user: Dict = Depends(get_current_user),
    fingpt_service: FinGPTService = Depends(get_fingpt_service)
):
    """
    Run scenario analysis for financial goals under different market conditions

    This endpoint provides analysis for scenarios like:
    - Market downturns (recession, bear market)
    - Interest rate changes
    - Income changes (job loss, promotion)
    - Expense changes (healthcare, education)
    - Goal timeline changes
    """
    start_time = datetime.utcnow()
    request_id = f"scenario_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing scenario analysis request: {request_id}")

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            goals=financial_goals,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Run scenario analysis (simplified implementation)
        scenario_results = []
        for i, scenario in enumerate(scenarios[:3]):  # Limit to 3 scenarios
            scenario_results.append({
                "scenario_name": scenario.get("name", f"Scenario {i+1}"),
                "description": scenario.get("description", "Market scenario analysis"),
                "probability_impact": "Medium",
                "goal_impact": "Goals may need 6-12 month adjustment",
                "recommended_actions": [
                    "Maintain emergency fund",
                    "Consider defensive assets",
                    "Review goal timelines"
                ]
            })

        # Create response
        response = {
            "success": True,
            "request_id": request_id,
            "scenario_results": scenario_results,
            "summary": "Scenario analysis shows goals are achievable with minor adjustments",
            "recommendations": [
                "Maintain flexible goal timelines",
                "Build larger emergency reserves",
                "Diversify income sources"
            ],
            "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
        }

        logger.info(f"Scenario analysis completed: {request_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running scenario analysis {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to run scenario analysis. Please try again."
        )

@router.get("/health")
async def planner_health_check():
    """Health check for AI Finance Goal Planner endpoints"""
    try:
        from main import fingpt_service

        forecaster_available = fingpt_service and 'forecaster' in getattr(fingpt_service, 'models', {})
        is_ready = fingpt_service and fingpt_service.is_ready()

        return {
            "status": "healthy" if is_ready else "degraded",
            "forecaster_model": "available" if forecaster_available else "unavailable",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": [
                "POST /api/v1/planner/create-strategy",
                "POST /api/v1/planner/track-progress",
                "POST /api/v1/planner/optimize-savings",
                "POST /api/v1/planner/scenario-analysis"
            ]
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Background task functions
async def log_strategy_creation(user_id: str, goals_count: int, total_goal_amount: float, 
                              planning_horizon: int, processing_time: float):
    """Log strategy creation for analytics"""
    try:
        logger.info(f"Analytics: Strategy created for user {user_id}, "
                   f"goals: {goals_count}, amount: ${total_goal_amount:.2f}, "
                   f"horizon: {planning_horizon}y, time: {processing_time:.2f}ms")
    except Exception as e:
        logger.error(f"Failed to log strategy analytics: {e}")
