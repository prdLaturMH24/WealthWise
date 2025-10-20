"""
Category 2: AI Recommendations API Routes
Provides market insights, news analysis, and sector recommendations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

from models.user_models import UserProfile, MarketPreferences, UserContext
from models.response_models import RecommendationResponse
from services.fingpt_service import FinGPTService
from services.market_data_service import MarketDataService
from middleware.auth_middleware import get_current_user
from utils.validation import validate_market_preferences
from utils.rate_limiting import rate_limit

router = APIRouter(prefix="/api/v1/recommendations", tags=["AI Recommendations"])
logger = logging.getLogger(__name__)

async def get_services():
    """Get required services"""
    from main import fingpt_service, market_data_service
    if not fingpt_service:
        raise HTTPException(status_code=503, detail="FinGPT service not available")
    if not market_data_service:
        raise HTTPException(status_code=503, detail="Market data service not available")
    return fingpt_service, market_data_service

@router.post("/market-insights", response_model=RecommendationResponse)
@rate_limit(max_requests=20, window_minutes=60)
async def get_market_insights(
    user_profile: UserProfile,
    market_preferences: Optional[MarketPreferences] = None,
    symbols: Optional[List[str]] = Query(None, description="Specific symbols to analyze"),
    timeframe: str = Query("1M", description="Analysis timeframe (1D, 1W, 1M, 3M, 6M, 1Y)"),
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Generate AI-powered market insights and trend analysis

    This endpoint provides:
    - Market trend analysis
    - Sector performance insights
    - Economic indicator impact
    - Technical analysis insights
    - Market sentiment assessment
    - Trading opportunities identification
    """
    start_time = datetime.utcnow()
    request_id = f"insights_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing market insights request: {request_id}")

        fingpt_service, market_data_service = await get_services()

        # Set default preferences if not provided
        if not market_preferences:
            market_preferences = MarketPreferences()

        # Validate market preferences
        validation_result = validate_market_preferences(market_preferences)
        if not validation_result.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid preferences: {validation_result.errors}")

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            preferences=market_preferences,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Gather market data
        market_data = await market_data_service.get_market_data(
            symbols=symbols or market_preferences.focus_regions,
            timeframe=timeframe,
            include_technical=market_preferences.technical_analysis,
            include_fundamental=market_preferences.fundamental_analysis
        )

        # Generate AI insights
        insights_response = await fingpt_service._extract_market_insights("", market_data)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        #insights_response.request_id = request_id
        #insights_response.processing_time_ms = processing_time

        logger.info(f"Market insights generated: {request_id} in {processing_time:.2f}ms")

        # Background analytics
        background_tasks.add_task(
            log_insights_request,
            user_id=user_profile.user_id,
            symbols_count=len(symbols) if symbols else 0,
            timeframe=timeframe,
            processing_time=processing_time
        )

        return insights_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating market insights {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate market insights. Please try again."
        )

@router.post("/news-analysis", response_model=RecommendationResponse)
@rate_limit(max_requests=15, window_minutes=60)
async def analyze_financial_news(
    user_profile: UserProfile,
    news_sources: List[str] = Query(..., description="News sources to analyze"),
    keywords: Optional[List[str]] = Query(None, description="Keywords to focus on"),
    date_from: Optional[date] = Query(None, description="Start date for news analysis"),
    date_to: Optional[date] = Query(None, description="End date for news analysis"),
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Analyze financial news and provide actionable insights

    This endpoint provides:
    - News sentiment analysis
    - Impact assessment on markets/sectors
    - Key event identification
    - Actionable insights extraction
    - Related symbol recommendations
    - Market timing implications
    """
    start_time = datetime.utcnow()
    request_id = f"news_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing news analysis request: {request_id}")

        fingpt_service, market_data_service = await get_services()

        # Set default date range if not provided
        if not date_from:
            date_from = date.today() - timedelta(days=7)
        if not date_to:
            date_to = date.today()

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Gather news data
        news_data = await market_data_service.get_financial_news(
            sources=news_sources,
            keywords=keywords,
            date_from=date_from,
            date_to=date_to
        )

        # Analyze news using FinGPT
        news_response = await fingpt_service._extract_news_analysis("", news_data)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        #news_response.request_id = request_id
        #news_response.processing_time_ms = processing_time

        logger.info(f"News analysis completed: {request_id} in {processing_time:.2f}ms")

        # Background analytics
        background_tasks.add_task(
            log_news_analysis,
            user_id=user_profile.user_id,
            news_count=len(news_data),
            sources=news_sources,
            processing_time=processing_time
        )

        return news_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing financial news {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze financial news. Please try again."
        )

@router.post("/sector-analysis", response_model=RecommendationResponse)
@rate_limit(max_requests=10, window_minutes=60)
async def generate_sector_recommendations(
    user_profile: UserProfile,
    sectors: Optional[List[str]] = Query(None, description="Specific sectors to analyze"),
    analysis_depth: str = Query("comprehensive", description="Analysis depth: basic, comprehensive, detailed"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate sector-wise investment recommendations

    This endpoint provides:
    - Sector performance analysis
    - Relative strength assessment
    - Growth prospects evaluation
    - Risk-return analysis by sector
    - Top stock picks within sectors
    - Allocation recommendations
    """
    start_time = datetime.utcnow()
    request_id = f"sector_{user_profile.user_id}_{int(start_time.timestamp())}"

    try:
        logger.info(f"Processing sector analysis request: {request_id}")

        fingpt_service, market_data_service = await get_services()

        # Create user context
        user_context = UserContext(
            profile=user_profile,
            session_id=request_id,
            request_timestamp=start_time
        )

        # Use preferred sectors if none specified
        if not sectors:
            sectors = [sector.value for sector in user_profile.preferred_sectors] if user_profile.preferred_sectors else [
                "technology", "healthcare", "finance", "consumer_goods", "energy"
            ]

        # Gather sector data
        market_data = await market_data_service.get_sector_data(
            sectors=sectors,
            analysis_depth=analysis_depth
        )

        # Generate sector recommendations
        sector_response = await fingpt_service._extract_sector_recommendations("", market_data.sectors)

        # Set response metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        #sector_response.request_id = request_id
        #sector_response.processing_time_ms = processing_time

        logger.info(f"Sector analysis completed: {request_id} in {processing_time:.2f}ms")

        return sector_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating sector recommendations {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate sector recommendations. Please try again."
        )

@router.get("/health")
async def recommendations_health_check():
    """Health check for AI Recommendations endpoints"""
    try:
        fingpt_service, market_data_service = await get_services()

        sentiment_available = 'sentiment' in fingpt_service.models if fingpt_service else False
        market_data_ready = market_data_service.is_ready() if market_data_service else False

        return {
            "status": "healthy" if sentiment_available and market_data_ready else "degraded",
            "sentiment_model": "available" if sentiment_available else "unavailable",
            "market_data": "available" if market_data_ready else "unavailable",
            "timestamp": datetime.utcnow().isoformat()
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
async def log_insights_request(user_id: str, symbols_count: int, timeframe: str, processing_time: float):
    """Log insights request for analytics"""
    try:
        logger.info(f"Analytics: Market insights for user {user_id}, "
                   f"symbols: {symbols_count}, timeframe: {timeframe}, "
                   f"time: {processing_time:.2f}ms")
    except Exception as e:
        logger.error(f"Failed to log insights analytics: {e}")

async def log_news_analysis(user_id: str, news_count: int, sources: List[str], processing_time: float):
    """Log news analysis for analytics"""
    try:
        logger.info(f"Analytics: News analysis for user {user_id}, "
                   f"articles: {news_count}, sources: {len(sources)}, "
                   f"time: {processing_time:.2f}ms")
    except Exception as e:
        logger.error(f"Failed to log news analytics: {e}")
