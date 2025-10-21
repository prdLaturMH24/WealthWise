"""
Category 1: AI Financial Advisor API Routes
Provides personalized financial advice, portfolio analysis, and risk assessment
"""
#External imports
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict

# Internal imports
from models.user_models import UserProfile, UserContext, CurrentPortfolio
from models.response_models import FinancialAdviceResponse
from services.fingpt_service import FinGPTService
from middleware.auth_middleware import get_current_user
from utils.validation import validate_user_profile, validate_portfolio
from utils.rate_limiting import rate_limit

router = APIRouter(prefix="/api/v1/advisor", tags=["AI Financial Advisor"])
logger = logging.getLogger(__name__)

# Dependency injection
async def get_fingpt_service() -> FinGPTService:
    """Get FinGPT service dependency"""
    from main import fingpt_service
    if not fingpt_service:
        raise HTTPException(status_code=503, detail="FinGPT service not available")
    return fingpt_service

@router.post("/personal-advice", response_model=FinancialAdviceResponse)
@rate_limit(max_requests=10, window_minutes=60)
async def get_personal_financial_advice(
    user_profile: UserProfile,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    fingpt_service: FinGPTService = Depends(get_fingpt_service)
):
    """
    Generate personalized financial advice based on user profile

    This endpoint provides comprehensive financial advice including:
    - Overall financial health assessment
    - Personalized recommendations
    - Risk management strategies
    - Investment allocation suggestions
    - Priority action items with timelines
    """
    start_time = datetime.utcnow()
    request_id = f"advice_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing personal advice request: {request_id}")

        # Validate user profile
        validation_result = validate_user_profile(user_profile)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid user profile: {', '.join(validation_result.errors)}"
            )

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Generate financial advice using FinGPT
        advice_response = await fingpt_service.generate_personal_advice(user_context)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        advice_response["success"] = True
        advice_response["timestamp"] = datetime.utcnow()
        advice_response["request_id"] = request_id
        advice_response["processing_time_ms"] = processing_time
        advice_response["model_used"] = "swiss-ai/Apertus-8B-Instruct-2509"
        
        financial_advice = FinancialAdviceResponse(**advice_response)
        # Log successful request
        logger.info(f"Personal advice generated successfully: {request_id} in {processing_time:.2f}ms")

        # Background task for analytics
        background_tasks.add_task(
            log_advice_request, 
            user_id=user_profile.user_id, 
            request_id=request_id,
            processing_time=processing_time
        )

        return advice_response

    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error generating personal advice {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate financial advice. Please try again."
        )

@router.post("/portfolio-analysis", response_model=FinancialAdviceResponse)
@rate_limit(max_requests=5, window_minutes=60)
async def analyze_user_portfolio(
    user_profile: UserProfile,
    portfolio: CurrentPortfolio,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    fingpt_service: FinGPTService = Depends(get_fingpt_service)
):
    """
    Analyze user's investment portfolio and provide optimization recommendations

    This endpoint provides:
    - Asset allocation analysis
    - Diversification assessment
    - Risk concentration evaluation
    - Performance analysis
    - Rebalancing recommendations
    - Optimization opportunities
    """
    start_time = datetime.utcnow()
    request_id = f"portfolio_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing portfolio analysis request: {request_id}")

        # Validate inputs
        profile_validation = validate_user_profile(user_profile)
        portfolio_validation = validate_portfolio(portfolio)

        if not profile_validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid user profile: {profile_validation.errors}")
        if not portfolio_validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid portfolio: {portfolio_validation.errors}")

        # Create user context with portfolio
        user_context = UserContext(
            profile=user_profile,
            portfolio=portfolio,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Analyze portfolio using FinGPT
        analysis_response = await fingpt_service.analyze_portfolio(user_context)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        analysis_response.request_id = request_id
        analysis_response.processing_time_ms = processing_time

        logger.info(f"Portfolio analysis completed: {request_id} in {processing_time:.2f}ms")

        # Background analytics
        background_tasks.add_task(
            log_portfolio_analysis,
            user_id=user_profile.user_id,
            portfolio_value=portfolio.total_value,
            holdings_count=len(portfolio.holdings),
            processing_time=processing_time
        )

        return analysis_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing portfolio {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze portfolio. Please try again."
        )

@router.post("/risk-assessment", response_model=FinancialAdviceResponse)
@rate_limit(max_requests=5, window_minutes=60)
async def assess_financial_risk(
    user_profile: UserProfile,
    current_user: Dict = Depends(get_current_user),
    fingpt_service: FinGPTService = Depends(get_fingpt_service)
):
    """
    Assess user's financial risk profile and provide risk management advice

    This endpoint provides:
    - Overall financial risk assessment
    - Key risk factor identification
    - Risk mitigation strategies
    - Insurance needs assessment
    - Emergency preparedness evaluation
    - Actionable risk reduction steps
    """
    start_time = datetime.utcnow()
    request_id = f"risk_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing risk assessment request: {request_id}")

        # Validate user profile
        validation_result = validate_user_profile(user_profile)
        if not validation_result.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid user profile: {validation_result.errors}")

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Assess financial risk using FinGPT
        risk_response = await fingpt_service.assess_financial_risk(user_context)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        risk_response.request_id = request_id
        risk_response.processing_time_ms = processing_time

        logger.info(f"Risk assessment completed: {request_id} in {processing_time:.2f}ms")

        return risk_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing financial risk {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to assess financial risk. Please try again."
        )

@router.get("/health")
async def advisor_health_check():
    """Health check for AI Financial Advisor endpoints"""
    try:
        from main import fingpt_service
        is_ready = fingpt_service and fingpt_service.is_ready()

        return {
            "status": "healthy" if is_ready else "degraded",
            "advisor_model": "available" if is_ready and 'advisor' in getattr(fingpt_service, 'models', {}) else "unavailable",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": [
                "POST /api/v1/advisor/personal-advice",
                "POST /api/v1/advisor/portfolio-analysis", 
                "POST /api/v1/advisor/risk-assessment"
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
async def log_advice_request(user_id: str, request_id: str, processing_time: float):
    """Log advice request for analytics"""
    try:
        logger.info(f"Analytics: Advice request {request_id} for user {user_id}, "
                   f"time: {processing_time:.2f}ms")

    except Exception as e:
        logger.error(f"Failed to log advice request analytics: {e}")

async def log_portfolio_analysis(user_id: str, portfolio_value: float, holdings_count: int, processing_time: float):
    """Log portfolio analysis for analytics"""
    try:
        logger.info(f"Analytics: Portfolio analysis for user {user_id}, "
                   f"value: ${portfolio_value:.2f}, holdings: {holdings_count}, "
                   f"time: {processing_time:.2f}ms")
    except Exception as e:
        logger.error(f"Failed to log portfolio analysis analytics: {e}")
