from http.client import HTTPResponse
import json
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Optional, Any, List
import traceback

from UserProfile import UserProfile
from RiskToleranceLevel import RiskToleranceLevel
from FinancialAdvice import FinancialAdvice
from AdviceCategory import AdviceCategory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Financial Advisor API",
    description="An AI-powered financial advisory service using FinGPT and TabPFN",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Module availability tracking
class AIModules:
    def __init__(self):
        self.fingpt_available = False
        self.tabpfn_available = False
        self.fingpt_module = None
        self.tabpfn_module = None
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize AI modules with proper error handling"""
        # FinGPT initialization
        try:
            import fingpt as fingpt_mod
            self.fingpt_module = fingpt_mod
            self.fingpt_available = True
            logger.info("FinGPT module loaded successfully")
        except ImportError:
            try:
                import FinGPT as fingpt_mod
                self.fingpt_module = fingpt_mod
                self.fingpt_available = True
                logger.info("FinGPT module (alternative import) loaded successfully")
            except ImportError:
                logger.warning("FinGPT module not available - using fallback logic")
        except Exception as e:
            logger.error(f"Error loading FinGPT: {e}")
        
        # TabPFN initialization
        try:
            import tabpfn as tabpfn_mod
            self.tabpfn_module = tabpfn_mod
            self.tabpfn_available = True
            logger.info("TabPFN module loaded successfully")
        except ImportError:
            logger.warning("TabPFN module not available - using fallback logic")
        except Exception as e:
            logger.error(f"Error loading TabPFN: {e}")

# Global AI modules instance
ai_modules = AIModules()

class FinancialAdvisor:
    """Main financial advisor class with AI integration"""
    
    def __init__(self):
        self.ai_modules = ai_modules
    
    def generate_advice(self, profile: UserProfile) -> FinancialAdvice:
        """Generate personalized financial advice using AI or fallback logic"""
        logger.info(f"Generating advice for user profile: Age={profile.Age}, Income={profile.MonthlyIncome}")
        
        # Try AI-based advice generation first
        ai_advice = self._try_ai_generation(profile)
        if ai_advice:
            return ai_advice
        
        # Fallback to rule-based advice
        logger.info("Using rule-based fallback for advice generation")
        return self._generate_rule_based_advice(profile)
    
    def _try_ai_generation(self, profile: UserProfile) -> Optional[FinancialAdvice]:
        """Attempt to generate advice using AI modules"""
        
        # Try FinGPT first
        fingpt_advice = self._try_fingpt_advice(profile)
        if fingpt_advice:
            return fingpt_advice
        
        # Try TabPFN if FinGPT fails
        tabpfn_advice = self._try_tabpfn_advice(profile)
        if tabpfn_advice:
            return tabpfn_advice
        
        return None
    
    def _try_fingpt_advice(self, profile: UserProfile) -> Optional[FinancialAdvice]:
        """Generate advice using FinGPT"""
        if not self.ai_modules.fingpt_available:
            return None
        
        try:
            # Convert profile to dictionary for AI processing
            profile_data = profile.model_dump(exclude_unset=True)
            
            fingpt_mod = self.ai_modules.fingpt_module
            text_advice = None
            
            # Try different FinGPT API patterns
            if hasattr(fingpt_mod, "generate_advice"):
                text_advice = fingpt_mod.generate_advice(profile_data)
            elif hasattr(fingpt_mod, "FinGPT"):
                try:
                    fg = fingpt_mod.FinGPT()
                    if hasattr(fg, "generate"):
                        text_advice = fg.generate(profile_data)
                    elif hasattr(fg, "chat"):
                        prompt = self._create_fingpt_prompt(profile)
                        text_advice = fg.chat(prompt)
                except Exception as e:
                    logger.warning(f"Error with FinGPT class instantiation: {e}")
                    if hasattr(fingpt_mod, "generate"):
                        text_advice = fingpt_mod.generate(profile_data)
            elif hasattr(fingpt_mod, "generate"):
                text_advice = fingpt_mod.generate(profile_data)
            
            if text_advice:
                # Process FinGPT response
                advice_text = self._process_fingpt_response(text_advice)
                return FinancialAdvice(
                    Title="AI-Powered Financial Advice (FinGPT)",
                    Description=advice_text,
                    Category=AdviceCategory.Investment,
                    ProjectedImpact=self._calculate_projected_impact(profile),
                    ActionItems=self._extract_action_items(advice_text),
                    Confidence=0.85
                )
        
        except Exception as e:
            logger.error(f"Error in FinGPT advice generation: {e}")
        
        return None
    
    def _try_tabpfn_advice(self, profile: UserProfile) -> Optional[FinancialAdvice]:
        """Generate advice using TabPFN predictions"""
        if not self.ai_modules.tabpfn_available:
            return None
        
        try:
            tabpfn_mod = self.ai_modules.tabpfn_module
            
            # Create feature vector from user profile
            features = self._create_feature_vector(profile)
            
            prediction_score = None
            
            # Try TabPFN prediction patterns
            if hasattr(tabpfn_mod, "TabPFNClassifier"):
                try:
                    # Note: In real implementation, you'd need pre-trained model or training data
                    # This is a simplified example
                    clf = tabpfn_mod.TabPFNClassifier(device="cpu")
                    
                    # Mock prediction since we don't have training data
                    # In practice, you'd fit the model first: clf.fit(X_train, y_train)
                    predictions = clf.predict(np.array([features]))
                    prediction_score = float(predictions[0]) if len(predictions) > 0 else None
                    
                except Exception as e:
                    logger.warning(f"TabPFN classifier error: {e}")
            
            elif hasattr(tabpfn_mod, "predict"):
                try:
                    pred = tabpfn_mod.predict(features)
                    prediction_score = float(pred[0]) if isinstance(pred, (list, tuple)) else float(pred)
                except Exception as e:
                    logger.warning(f"TabPFN predict error: {e}")
            
            if prediction_score is not None:
                # Generate advice based on TabPFN prediction
                return self._create_tabpfn_advice(profile, prediction_score)
        
        except Exception as e:
            logger.error(f"Error in TabPFN advice generation: {e}")
        
        return None
    
    def _generate_rule_based_advice(self, profile: UserProfile) -> FinancialAdvice:
        """Generate rule-based financial advice as fallback"""
        
        # Determine risk tolerance
        risk_level = self._get_risk_level(profile.RiskTolerance)
        
        # Generate advice based on risk tolerance and profile
        if risk_level == "conservative":
            return self._create_conservative_advice(profile)
        elif risk_level == "aggressive":
            return self._create_aggressive_advice(profile)
        else:
            return self._create_balanced_advice(profile)
    
    def _get_risk_level(self, risk_tolerance: Optional[RiskToleranceLevel]) -> str:
        """Extract risk level as string"""
        if risk_tolerance is None:
            return "moderate"
        
        risk_str = risk_tolerance.value if hasattr(risk_tolerance, 'value') else str(risk_tolerance)
        return risk_str.lower()
    
    def _create_conservative_advice(self, profile: UserProfile) -> FinancialAdvice:
        """Create conservative investment advice"""
        monthly_savings = profile.MonthlySavings or 0
        projected_return = 0.03  # 3% annual return
        
        return FinancialAdvice(
            Title="Conservative Investment Strategy",
            Description="A low-risk approach focusing on capital preservation with steady, modest returns through bonds and stable investments.",
            Category=AdviceCategory.Investment,
            ProjectedImpact=monthly_savings * 12 * (1 + projected_return),
            ActionItems=[
                "Allocate 60% of portfolio to government and corporate bonds",
                "Allocate 30% to blue-chip dividend stocks",
                "Keep 10% in high-yield savings accounts",
                f"Maintain consistent monthly investments of ${monthly_savings:.2f}",
                "Review and rebalance portfolio quarterly"
            ],
            Confidence=0.90
        )
    
    def _create_aggressive_advice(self, profile: UserProfile) -> FinancialAdvice:
        """Create aggressive investment advice"""
        monthly_savings = profile.MonthlySavings or 0
        projected_return = 0.10  # 10% annual return
        
        return FinancialAdvice(
            Title="Aggressive Growth Strategy",
            Description="A high-risk, high-reward strategy focusing on growth stocks and emerging markets for maximum long-term returns.",
            Category=AdviceCategory.Investment,
            ProjectedImpact=monthly_savings * 12 * (1 + projected_return),
            ActionItems=[
                "Allocate 70% to growth stocks and technology ETFs",
                "Allocate 20% to emerging market funds",
                "Allocate 10% to alternative investments (REITs, commodities)",
                f"Increase monthly investments to ${monthly_savings * 1.1:.2f} if possible",
                "Monitor portfolio monthly and adjust based on market conditions"
            ],
            Confidence=0.75
        )
    
    def _create_balanced_advice(self, profile: UserProfile) -> FinancialAdvice:
        """Create balanced investment advice"""
        monthly_savings = profile.MonthlySavings or 0
        projected_return = 0.07  # 7% annual return
        
        return FinancialAdvice(
            Title="Balanced Investment Portfolio",
            Description="A diversified approach balancing growth potential with risk management through a mix of stocks, bonds, and alternative investments.",
            Category=AdviceCategory.Investment,
            ProjectedImpact=monthly_savings * 12 * (1 + projected_return),
            ActionItems=[
                "Allocate 50% to diversified stock ETFs (domestic and international)",
                "Allocate 40% to bond funds (government and corporate)",
                "Allocate 10% to REITs for real estate exposure",
                f"Set up automatic monthly investments of ${monthly_savings:.2f}",
                "Rebalance portfolio semi-annually",
                "Consider tax-advantaged accounts (401k, IRA) for retirement savings"
            ],
            Confidence=0.85
        )
    
    def _create_tabpfn_advice(self, profile: UserProfile, prediction_score: float) -> FinancialAdvice:
        """Create advice based on TabPFN prediction"""
        monthly_savings = profile.MonthlySavings or 0
        
        # Use prediction score to adjust projected returns
        base_return = 0.07
        adjusted_return = base_return * (1 + prediction_score * 0.1)
        
        return FinancialAdvice(
            Title="AI-Enhanced Investment Strategy (TabPFN)",
            Description=f"Machine learning model suggests optimized allocation with predicted performance factor of {prediction_score:.3f}",
            Category=AdviceCategory.Investment,
            ProjectedImpact=monthly_savings * 12 * (1 + adjusted_return),
            ActionItems=[
                f"Follow AI-optimized allocation strategy (prediction factor: {prediction_score:.3f})",
                "Implement gradual portfolio adjustments over 3-6 months",
                "Monitor model predictions monthly for strategy updates",
                f"Target monthly investment of ${monthly_savings:.2f}"
            ]
        )
    
    def _create_fingpt_prompt(self, profile: UserProfile) -> str:
        """Create a structured prompt for FinGPT"""
        return f"""
        Provide personalized financial advice for a client with the following profile:
        - Age: {profile.Age}
        - Monthly Income: ${profile.MonthlyIncome or 0:,.2f}
        - Monthly Savings: ${profile.MonthlySavings or 0:,.2f}
        - Risk Tolerance: {profile.RiskTolerance}
        
        Please provide specific, actionable investment recommendations.
        """
    
    def _process_fingpt_response(self, response: Any) -> str:
        """Process and clean FinGPT response"""
        if isinstance(response, dict):
            return response.get("advice") or response.get("text") or str(response)
        elif isinstance(response, list):
            return "\\n".join(map(str, response))
        else:
            return str(response)
    
    def _create_feature_vector(self, profile: UserProfile) -> List[float]:
        """Create feature vector for TabPFN from user profile"""
        return [
            float(profile.Age or 30),
            float(profile.MonthlyIncome or 0),
            float(profile.MonthlySavings or 0),
            float(profile.InvestmentHorizon or 10),
            float(profile.CurrentSavings or 0),
            float({'Conservative': 1, 'Moderate': 2, 'Aggressive': 3}.get(
                self._get_risk_level(profile.RiskTolerance).title(), 2
            ))
        ]
    
    def _calculate_projected_impact(self, profile: UserProfile) -> float:
        """Calculate projected financial impact"""
        monthly_savings = profile.MonthlySavings or 0
        return monthly_savings * 12 * 1.07  # 7% default return
    
    def _extract_action_items(self, advice_text: str) -> List[str]:
        """Extract action items from advice text"""
        # Simple extraction - in practice, you might use NLP
        lines = advice_text.split('\\n')
        action_items = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
        return action_items[:5] if action_items else ["Follow the provided advice"]


# Initialize the financial advisor
financial_advisor = FinancialAdvisor()


@app.get("/", tags=["Health Check"])
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Financial Advisor API is running",
        "version": "1.0.0",
        "ai_modules": {
            "fingpt_available": ai_modules.fingpt_available,
            "tabpfn_available": ai_modules.tabpfn_available
        }
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Detailed health check with system status"""
    return {
        "status": "healthy",
        "ai_modules": {
            "fingpt": {
                "available": ai_modules.fingpt_available,
                "module": str(ai_modules.fingpt_module) if ai_modules.fingpt_module else None
            },
            "tabpfn": {
                "available": ai_modules.tabpfn_available,
                "module": str(ai_modules.tabpfn_module) if ai_modules.tabpfn_module else None
            }
        }
    }


@app.post("/generate-advice", response_model=FinancialAdvice, tags=["Financial Advice"])
async def generate_advice(profile: UserProfile):
    """
    Generate personalized financial advice based on user profile.
    
    This endpoint analyzes the user's financial profile and generates
    personalized investment advice using AI models when available,
    or fallback to rule-based recommendations.
    """
    try:
        logger.info(f"Received advice request for profile: {profile.model_dump(exclude_unset=True)}")
        
        # Validate input
        if profile.MonthlyIncome and profile.MonthlySavings and profile.MonthlySavings > profile.MonthlyIncome:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monthly savings cannot exceed monthly income"
            )
        
        # Generate advice
        advice = financial_advisor.generate_advice(profile)
        
        logger.info(f"Successfully generated advice: {advice.Title}")
        return advice
        # return JSONResponse(
        #     status_code=status.HTTP_200_OK,
        #     content=advice.model_dump(mode='json')
        #     )
    
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input data: {str(ve)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error generating advice: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating financial advice. Please try again."
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )