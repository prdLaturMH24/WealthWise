"""
FinGPT-Powered Financial AI Services API
FastAPI Application with Three Main Categories

1. AI Financial Advisor - Personalized financial advice based on user profiles
2. AI Recommendations - Non-advisory recommendations (market insights, news analysis, etc.)
3. AI Finance Goal Planner - Goal-based financial planning and strategy

Built with FastAPI and powered by FinGPT models from AI4Finance Foundation
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from huggingface_hub import login, InferenceClient
from json_repair import repair_json
import uvicorn
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
import os
import json
from contextlib import asynccontextmanager
import asyncio
from pydantic import ValidationError
from models.response_models import FinancialAdviceResponse
import re
import json

# Import configuration
from config.settings import settings

# Import services
from services.fingpt_service import FinGPTService
from services.market_data_service import MarketDataService

# Import middleware
from utils.logging_config import setup_logging, RequestLogger
from utils.rate_limiting import RateLimitMiddleware

# Import ALL API routers
from api.v1.advisor import router as advisor_router
from api.v1.recommendations import router as recommendations_router
from api.v1.planner import router as planner_router
from api.v1.auth import router as auth_router

def clean_json_string(raw_text: str) -> str:
    """
    Cleans a malformed JSON string by removing markdown code fences,
    language identifiers, trailing commas, and other impurities.
    Returns a valid JSON string ready for parsing.
    
    Args:
        raw_text: Raw string that may contain JSON with impurities
        
    Returns:
        Clean JSON string
        
    Raises:
        ValueError: If input is invalid or cannot be cleaned to valid JSON
    """
    
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("Input must be a non-empty string")
    
    cleaned = raw_text.strip()

    # Step 1: Unescape the string if it contains literal \n characters
    # This handles cases where JSON is double-encoded
    if '\n' in cleaned:
        # Replace escaped newlines with actual newlines
        cleaned = cleaned.replace('\n', '')
        # Replace escaped quotes
        cleaned = cleaned.replace('\"', '"')
        # Replace escaped backslashes
        cleaned = cleaned.replace('\\\\', '\\')
        
    # Step 2: Remove markdown code fences
    # Remove opening fence like ```json or ```
    cleaned = re.sub(r'```[a-zA-Z]*\s*', '', cleaned, count=1)
    # Remove closing fence ```
    cleaned = re.sub(r'\s*```\s*$', '', cleaned)
    
    # Step 2: Remove invisible Unicode characters
    cleaned = cleaned.replace('\ufeff', '')  # BOM
    cleaned = cleaned.replace('\u200b', '')  # Zero-width space
    cleaned = cleaned.replace('\x00', '')    # Null character
    cleaned = cleaned.replace('\u2028', '')  # Line separator
    
    # Step 3: Find JSON object/array boundaries
    json_match = re.search(r'(\{.*\}|$$.*$$)', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(1)
    
    cleaned = cleaned.strip()
    
    # Step 4: Fix common JSON errors - trailing commas
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Fix missing commas between properties (common LLM error)
    # Add comma between }" and "key if missing
    cleaned = re.sub(r'"\s*\n\s*"', '",\n"', cleaned)
    
    # Fix missing commas after numbers/booleans before next key
    cleaned = re.sub(r'(\d|true|false|null)\s*\n\s*"', r'\1,\n"', cleaned)
    
    # Remove duplicate commas
    cleaned = re.sub(r',\s*,', ',', cleaned)
    
    # Step 5: Try to parse - if it fails, show where the error is
    try:
        cleaned = repair_json(cleaned)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Print debug info to help locate the issue
        lines = cleaned.split('\n')
        error_line = e.lineno - 1 if e.lineno else 0
        
        print(f"JSON Error at line {e.lineno}, column {e.colno}")
        print(f"Error message: {e.msg}")
        
        # Show context around the error
        start = max(0, error_line - 2)
        end = min(len(lines), error_line + 3)
        
        print("\nContext around error:")
        for i in range(start, end):
            marker = " >>> " if i == error_line else "     "
            print(f"{marker}Line {i+1}: {lines[i]}")
        
        raise ValueError(f"Could not parse as valid JSON: {e}")

# Global services - these will be available to all route modules
fingpt_service = None
market_data_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global fingpt_service, market_data_service

    # Startup
    logging.info("Starting FinGPT Financial AI Services...")

    try:
        # Initialize FinGPT service
        logging.info("Initializing FinGPT service...")
        fingpt_service = FinGPTService()
        await fingpt_service.initialize()
        logging.info("FinGPT service initialized successfully")

        # Initialize market data service
        logging.info("Initializing market data service...")
        #market_data_service = MarketDataService()
        #await market_data_service.initialize()
        logging.info("Market data service initialized successfully")

        logging.info("All services initialized successfully!")

    except Exception as e:
        logging.error(f"Failed to initialize services: {e}")
        logging.warning("Services will run in fallback mode")

    yield

    # Shutdown
    logging.info("Shutting down FinGPT Financial AI Services...")

    if fingpt_service:
        await fingpt_service.cleanup()
        logging.info("FinGPT service cleanup completed")

    if market_data_service:
        await market_data_service.cleanup()
        logging.info("Market data service cleanup completed")

    logging.info("Shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="FinGPT Financial AI Services",
    description="""
    **AI-Powered Financial Advisory, Recommendations, and Goal Planning APIs**

    This API provides three main categories of financial AI services powered by FinGPT models:

    ## Category 1: AI Financial Advisor
    - **Personal Financial Advice**: Personalized recommendations based on user profiles
    - **Portfolio Analysis**: Investment portfolio optimization and analysis  
    - **Risk Assessment**: Financial risk evaluation and mitigation strategies

    ## Category 2: AI Recommendations  
    - **Market Insights**: AI-powered market trend analysis and insights
    - **News Analysis**: Financial news sentiment analysis and impact assessment
    - **Sector Analysis**: Sector-wise investment recommendations and analysis

    ## Category 3: AI Finance Goal Planner
    - **Goal Strategy**: Comprehensive financial planning for multiple goals
    - **Progress Tracking**: Goal progress monitoring and adjustment recommendations
    - **Savings Optimization**: Optimal savings allocation and investment strategies

    All APIs are powered by real FinGPT models from AI4Finance Foundation integrated with live market data.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    global_rate_limit=settings.rate_limit_requests,
    window_minutes=settings.rate_limit_window // 60
)

# Add request logging middleware
app.add_middleware(RequestLogger)

# Include ALL API routers with proper registration
logger.info("Registering API routers...")
app.include_router(auth_router)
logger.info("Registered Authentication routes")

# Category 1: AI Financial Advisor
app.include_router(advisor_router)
logger.info("Registered AI Financial Advisor routes")

# Category 2: AI Recommendations  
app.include_router(recommendations_router)
logger.info("Registered AI Recommendations routes")

# Category 3: AI Finance Goal Planner
app.include_router(planner_router)
logger.info("Registered AI Finance Goal Planner routes")

logger.info("All API routes registered successfully!")

# Health check endpoint
@app.get("/health", response_model=Dict)
async def health_check():
    """Comprehensive health check endpoint"""
    global fingpt_service, market_data_service

    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": "development" if settings.debug else "production",
        "services": {
            "fingpt": {
                "status": "available" if fingpt_service and fingpt_service.is_ready() else "unavailable",
                "models_loaded": len(fingpt_service.fingpt_models) if fingpt_service else 0,
                "available_models": list(fingpt_service.fingpt_models.keys()) if fingpt_service else []
            },
            "market_data": {
                "status": "available" if market_data_service and market_data_service.is_ready() else "unavailable"
            }
        },
        "api_categories": {
            "advisor": {
                "status": "Available",
                "endpoints": [
                    "POST /api/v1/advisor/personal-advice",
                    "POST /api/v1/advisor/portfolio-analysis", 
                    "POST /api/v1/advisor/risk-assessment"
                ]
            },
            "recommendations": {
                "status": "Available",
                "endpoints": [
                    "POST /api/v1/recommendations/market-insights",
                    "POST /api/v1/recommendations/news-analysis",
                    "POST /api/v1/recommendations/sector-analysis"
                ]
            },
            "planner": {
                "status": "Available", 
                "endpoints": [
                    "POST /api/v1/planner/create-strategy",
                    "POST /api/v1/planner/track-progress",
                    "POST /api/v1/planner/optimize-savings"
                ]
            }
        }
    }

    # Determine overall status
    services_ready = (
        fingpt_service and fingpt_service.is_ready() and
        market_data_service and market_data_service.is_ready()
    )

    if not services_ready:
        health_status["status"] = "degraded"
        health_status["message"] = "Some services running in fallback mode"

    return health_status

# Root endpoint with comprehensive API documentation
@app.get("/", response_class=HTMLResponse)
async def root():
    """Interactive API documentation homepage"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinGPT Financial AI Services</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
            .header { text-align: center; margin-bottom: 3rem; }
            .header h1 { font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .header p { font-size: 1.2rem; opacity: 0.9; }
            .categories { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; margin-bottom: 3rem; }
            .category { 
                background: rgba(255,255,255,0.1); 
                padding: 2rem; 
                border-radius: 15px; 
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            .category:hover { transform: translateY(-5px); }
            .category h2 { font-size: 1.5rem; margin-bottom: 1rem; display: flex; align-items: center; }
            .category h2 .icon { font-size: 2rem; margin-right: 0.5rem; }
            .endpoint { 
                background: rgba(255,255,255,0.1); 
                padding: 1rem; 
                margin: 1rem 0; 
                border-radius: 8px;
                border-left: 4px solid rgba(255,255,255,0.5);
            }
            .endpoint-method { 
                display: inline-block; 
                background: rgba(255,255,255,0.2); 
                padding: 0.2rem 0.5rem; 
                border-radius: 4px; 
                font-size: 0.8rem; 
                font-weight: bold;
                margin-right: 0.5rem;
                color: #333;
            }
            .links { 
                display: flex; 
                justify-content: center; 
                gap: 2rem; 
                margin-top: 3rem; 
                flex-wrap: wrap;
            }
            .btn { 
                display: inline-block; 
                padding: 1rem 2rem; 
                background: rgba(255,255,255,0.2); 
                color: white; 
                text-decoration: none; 
                border-radius: 50px; 
                transition: all 0.3s ease;
                border: 2px solid rgba(255,255,255,0.3);
                font-weight: bold;
            }
            .btn:hover { 
                background: rgba(255,255,255,0.3); 
                transform: scale(1.05);
                border-color: rgba(255,255,255,0.6);
            }
            .features { 
                background: rgba(255,255,255,0.1); 
                padding: 2rem; 
                border-radius: 15px; 
                margin-top: 2rem; 
                backdrop-filter: blur(10px);
            }
            .feature-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
            .feature { display: flex; align-items: center; padding: 0.5rem; }
            .feature-icon { margin-right: 0.5rem; font-size: 1.2rem; }
            .api-summary { 
                text-align: center; 
                margin: 2rem 0; 
                padding: 1.5rem; 
                background: rgba(255,255,255,0.15); 
                border-radius: 10px; 
            }
            @media (max-width: 768px) {
                .container { padding: 1rem; }
                .header h1 { font-size: 2rem; }
                .categories { grid-template-columns: 1fr; gap: 1rem; }
                .links { flex-direction: column; align-items: center; gap: 1rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 WealthWise : Wealth Management Simplified</h1>
                <p>AI-Powered Financial Advisory • Market Recommendations • Goal Planning</p>
                <p style="font-size: 1rem; opacity: 0.8; margin-top: 0.5rem;">
                    Powered by AI4Finance Foundation's FinGPT Models
                </p>
            </div>

            <div class="api-summary">
                <h2>🎯 Complete API Implementation</h2>
                <p><strong>9 Endpoints</strong> across <strong>3 Categories</strong> | <strong>Real FinGPT Models</strong> | <strong>Live Market Data</strong></p>
            </div>

            <div class="categories">
                <div class="category">
                    <h2><span class="icon">📊</span> AI Financial Advisor</h2>
                    <p style="margin-bottom: 1rem;">Personalized financial advice and portfolio optimization</p>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/advisor/personal-advice</strong><br>
                        <small>Get comprehensive personal financial advice based on user profile</small>
                    </div>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/advisor/portfolio-analysis</strong><br>
                        <small>Analyze and optimize investment portfolio with AI insights</small>
                    </div>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/advisor/risk-assessment</strong><br>
                        <small>Assess financial risk and get AI-powered mitigation strategies</small>
                    </div>
                </div>

                <div class="category">
                    <h2><span class="icon">💡</span> AI Recommendations</h2>
                    <p style="margin-bottom: 1rem;">Market insights and investment recommendations</p>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/recommendations/market-insights</strong><br>
                        <small>Get AI-powered market trend analysis and trading insights</small>
                    </div>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/recommendations/news-analysis</strong><br>
                        <small>Analyze financial news sentiment and market impact with AI</small>
                    </div>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/recommendations/sector-analysis</strong><br>
                        <small>Get AI-generated sector-wise investment recommendations</small>
                    </div>
                </div>

                <div class="category">
                    <h2><span class="icon">🎯</span> AI Finance Goal Planner</h2>
                    <p style="margin-bottom: 1rem;">Goal-based financial planning and optimization</p>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/planner/create-strategy</strong><br>
                        <small>Create AI-powered comprehensive financial goal strategies</small>
                    </div>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/planner/track-progress</strong><br>
                        <small>Track progress towards financial goals with AI insights</small>
                    </div>

                    <div class="endpoint">
                        <span class="endpoint-method">POST</span><strong>/api/v1/planner/optimize-savings</strong><br>
                        <small>AI-optimized savings strategy for multiple financial goals</small>
                    </div>
                </div>
            </div>

            <div class="features">
                <h2 style="text-align: center; margin-bottom: 1.5rem;">🚀 Production Features</h2>
                <div class="feature-list">
                    <div class="feature">
                        <span class="feature-icon">🤖</span>
                        <span>Real FinGPT AI Models</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">📊</span>
                        <span>Live Market Data Integration</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">🔐</span>
                        <span>JWT Authentication</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">⚡</span>
                        <span>FastAPI Async Performance</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">🛡️</span>
                        <span>Rate Limiting Protection</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">📈</span>
                        <span>Advanced Analytics</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">🔄</span>
                        <span>Fallback Support</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">📝</span>
                        <span>Input Validation</span>
                    </div>
                </div>
            </div>

            <div class="links">
                <a href="/docs" class="btn">📚 Interactive API Docs</a>
                <a href="/health" class="btn">🏥 Health Check</a>
                <a href="/redoc" class="btn">📖 Alternative Docs</a>
                <a href="/status" class="btn">📊 API Status</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/financial/chat")
async def chat_endpoint(message: str):
    """Simple chat endpoint for testing"""
    try:
        if not message or message.strip() == "":
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        prompt: str = message + "Financial Advice Output should be in plain json format matching the following json schema: " 
        prompt += r"""{"$schema":"http://json-schema.org/draft-07/schema#","title":"FinancialAdviceResponse","description":"Response for personal financial advice requests","type":"object","properties":{"advice_summary":{"type":"string","description":"Executive summary of advice"},"detailed_analysis":{"type":"string","description":"Detailed financial analysis"},"action_items":{"type":"array","description":"Recommended action items","items":{"$ref":"#/definitions/ActionItem"}},"risk_assessment":{"$ref":"#/definitions/RiskAssessment","description":"Risk analysis and recommendations"},"portfolio_analysis":{"anyOf":[{"$ref":"#/definitions/PortfolioAnalysis"},{"type":"null"}],"description":"Portfolio analysis if applicable"},"confidence_level":{"$ref":"#/definitions/ConfidenceLevel","description":"AI confidence in recommendations"},"follow_up_timeline":{"type":"string","description":"When to reassess or follow up"},"additional_resources":{"type":"array","description":"Educational resources and tools","items":{"type":"string"},"default":[]},"projected_net_worth":{"anyOf":[{"type":"object","additionalProperties":{"type":"number"}},{"type":"null"}],"description":"Net worth projections over time"},"savings_projections":{"anyOf":[{"type":"object","additionalProperties":{"type":"number"}},{"type":"null"}],"description":"Savings growth projections"},"retirement_readiness":{"anyOf":[{"type":"object","additionalProperties":true},{"type":"null"}],"description":"Retirement readiness assessment"}},"required":["advice_summary","detailed_analysis","action_items","risk_assessment","confidence_level","follow_up_timeline"],"definitions":{"ActionItem":{"type":"object","description":"Represents an actionable financial recommendation"},"RiskAssessment":{"type":"object","description":"Represents risk analysis and related insights"},"PortfolioAnalysis":{"type":"object","description":"Represents a breakdown of portfolio performance and allocation"},"ConfidenceLevel":{"type":"object","description":"Describes model confidence and reliability metrics"}}}"""

        client = InferenceClient(
        provider="publicai",
        api_key=settings.huggingface_token,
        )
        completion = client.chat.completions.create(
            model="swiss-ai/Apertus-8B-Instruct-2509",
            messages=[
                {
                    "role": "system",
                    "content": "I am a professional financial advisor trained on Financial Data"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        content = completion.choices[0].message.content
        if completion is None or content is None:
            raise HTTPException(status_code=500, detail="No response from AI model")
        
        cleaned = clean_json_string(content)
        return cleaned

    except Exception as e:
        logger.error("Error ocuured while getting chat response: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal server error while processing chat request: {e}")

# API Status endpoint with complete route listing
@app.get("/status")
async def api_status():
    """Get detailed API status information with all endpoints"""
    return {
        "api_version": "1.0.0",
        "total_endpoints": 9,
        "categories": {
            "advisor": {
                "name": "AI Financial Advisor",
                "endpoints": 3,
                "routes": [
                    {
                        "method": "POST",
                        "path": "/api/v1/advisor/personal-advice",
                        "description": "Get comprehensive personal financial advice"
                    },
                    {
                        "method": "POST", 
                        "path": "/api/v1/advisor/portfolio-analysis",
                        "description": "Analyze and optimize investment portfolio"
                    },
                    {
                        "method": "POST",
                        "path": "/api/v1/advisor/risk-assessment", 
                        "description": "Assess financial risk and get mitigation strategies"
                    }
                ]
            },
            "recommendations": {
                "name": "AI Recommendations",
                "endpoints": 3,
                "routes": [
                    {
                        "method": "POST",
                        "path": "/api/v1/recommendations/market-insights",
                        "description": "Get AI-powered market trend analysis"
                    },
                    {
                        "method": "POST",
                        "path": "/api/v1/recommendations/news-analysis", 
                        "description": "Analyze financial news sentiment and impact"
                    },
                    {
                        "method": "POST",
                        "path": "/api/v1/recommendations/sector-analysis",
                        "description": "Get sector-wise investment recommendations"
                    }
                ]
            },
            "planner": {
                "name": "AI Finance Goal Planner", 
                "endpoints": 3,
                "routes": [
                    {
                        "method": "POST",
                        "path": "/api/v1/planner/create-strategy",
                        "description": "Create comprehensive financial goal strategy"
                    },
                    {
                        "method": "POST",
                        "path": "/api/v1/planner/track-progress",
                        "description": "Track progress towards financial goals"
                    },
                    {
                        "method": "POST", 
                        "path": "/api/v1/planner/optimize-savings",
                        "description": "Optimize savings strategy for multiple goals"
                    }
                ]
            }
        },
        "models": {
            "fingpt_advisor": {
                "available": fingpt_service and 'advisor' in fingpt_service.fingpt_models,
                "model": "FinGPT/fingpt-mt_llama2-7b_lora"
            },
            "fingpt_sentiment": {
                "available": fingpt_service and 'sentiment' in fingpt_service.fingpt_models,
                "model": "FinGPT/fingpt-sentiment_llama2-13b_lora"
            },
            "fingpt_forecaster": {
                "available": fingpt_service and 'forecaster' in fingpt_service.fingpt_models,
                "model": "FinGPT/fingpt-forecaster_dow30_llama2-7b_lora"
            }
        },
        "features": [
            "Real FinGPT model integration",
            "Live market data feeds",
            "Comprehensive input validation", 
            "JWT authentication",
            "Rate limiting and security",
            "Structured logging",
            "Fallback modes",
            "Background analytics",
            "Interactive documentation"
        ]
    }

# List all available routes endpoint
@app.get("/routes")
async def list_routes():
    """List all available API routes"""
    routes = []
    for route in app.routes:
        path = getattr(route, 'path', None)
        methods = getattr(route, 'methods', None)

        if path and methods and path.startswith('/api/'):
            for method in methods:
                if method != 'HEAD':  # Skip HEAD methods
                    routes.append({
                        "method": method,
                        "path": path,
                        "name": getattr(route, 'name', ''),
                        "tags": getattr(route, 'tags', [])
                    })

    # Sort routes by path
    routes.sort(key=lambda x: x['path'])

    return {
        "total_routes": len(routes),
        "routes": routes,
        "categories": {
            "advisor": len([r for r in routes if r['path'].startswith('/api/v1/advisor')]),
            "recommendations": len([r for r in routes if r['path'].startswith('/api/v1/recommendations')]),
            "planner": len([r for r in routes if r['path'].startswith('/api/v1/planner')])
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "The requested API endpoint does not exist",
            "available_categories": [
                "/api/v1/advisor/* - AI Financial Advisor endpoints",
                "/api/v1/recommendations/* - AI Recommendations endpoints", 
                "/api/v1/planner/* - AI Finance Goal Planner endpoints"
            ],
            "documentation": "/docs",
            "all_routes": "/routes"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "support": "Check logs for details",
            "health_check": "/health"
        }
    )

if __name__ == "__main__":
    # Development server
    logger.info("Starting FinGPT Financial AI Services...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"FinGPT models will be loaded on startup")
    logger.info(f"Server will run on {settings.host}:{settings.port}")
    logger.info(f"API Documentation: http://{settings.host}:{settings.port}/docs")
    # Login to HuggingFace if token is provided
    login(settings.huggingface_token, new_session=True)
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        workers=1 # Use 1 worker for model loading
    )
