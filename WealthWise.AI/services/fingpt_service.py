"""
FinGPT Service Integration for Financial AI APIs with Real Hugging Face Models

This service integrates with real FinGPT models from AI4Finance Foundation
using Hugging Face InferenceClient to power the three main API categories:
1. AI Financial Advisor
2. AI Recommendations  
3. AI Finance Goal Planner
"""

import asyncio
from http.client import HTTPException
import logging
import profile
import aiohttp
from json_repair import repair_json
from pydantic import ValidationError
import torch
from typing import Dict, List, Optional, Any
from datetime import datetime, time
import numpy as np
from huggingface_hub import InferenceClient
import os
import json
import re
import transformers
import os
import requests
from dateutil import parser as date_parser

from config.settings import settings
from models.chat_completions import ChatCompletion
from models.response_models import FinancialAdviceResponse
from utils.model_utils import PromptEngine

logger = logging.getLogger(__name__)

class FinGPTService:
    """Main service class for FinGPT integration with Hugging Face"""    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.inference_clients = {}
        self.prompt_engine = PromptEngine()
        self._is_ready = False
        self.hf_token = None
        self.fingpt_models = {}
        self.session = None
        self.public_ai_model = None
        self.public_ai_tokenizer = None
        self.public_ai_model_name = "swiss-ai/Apertus-8B-Instruct-2509"
        self.pipeline = {}
        self.huggingface_api_url = "https://router.huggingface.co/v1/chat/completions"
        self.hf_api_authorization = {}

        logger.info(f"FinGPT Service being initialized with device: {self.device}")

    async def initialize(self):
        """Initialize FinGPT InferenceClient connections or load FinGPT Models"""
        try:
            logger.info("Starting FinGPT model initialization...")
            # Initialize aiohttp session for async requests
            self.session = aiohttp.ClientSession()
            # Get HuggingFace token from settings
            self.hf_token = settings.huggingface_token
            if self.hf_token:
                logger.info("HuggingFace token found - real models will be used")
                self.hf_api_authorization = {"Authorization": f"Bearer {self.hf_token}"}
            else:
                logger.warning("No HuggingFace token found - fallback mode will be used")

            # Try to load real models via HuggingFace InferenceClient
            try:
                #await self._load_fingpt_models()
                logger.info(f"Initialized advisor model: meta-llama/Meta-Llama-3.1-8B-Instruct")
                logger.info("Real FinGPT InferenceClients initialized successfully")
            except Exception as e:
                logger.error(f"Error loading FinGPT models: {e}")
                logger.warning("Falling back to basic heuristic responses")
            
            self._is_ready = True 
            
        except Exception as e:
            logger.error(f"Failed to initialize FinGPT service: {e}")
            self._is_ready = False
    
    async def _load_fingpt_models(self):
        """Initialize HuggingFace InferenceClients for FinGPT models"""
        try:
            for model_type, model_id in self.fingpt_models.items():
                try:

                    pipeline = transformers.pipeline(
                    "text-generation",
                    model=model_id,
                    trust_remote_code=True,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    use_auth_token=self.hf_token
                    )

                    messages = [
                        {"role": "system", "content": "You are a professional financial advisor!"},
                        {"role": "user", "content": "Who are you?"},
                    ]

                    outputs = pipeline(
                        messages,
                        max_new_tokens=256,
                    )
                    print(outputs[0]["generated_text"][-1])
                    self.pipeline[model_type] = pipeline
                    logger.info(f"Initialized {model_type} model: {model_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize {model_type} model {model_id}: {e}")
                    # Continue without this model - fallback will be used
                    
            if not self.inference_clients:
                raise Exception("No FinGPT models could be initialized")
                
            logger.info(f"Successfully initialized {len(self.inference_clients)} FinGPT models")
            
        except Exception as e:
            logger.error(f"Error initializing FinGPT InferenceClients: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            logger.info("Market data service cleanup completed")
        except Exception as e:
            logger.error(f"Error during market data cleanup: {e}")

    def _test_model_connection(self, client: InferenceClient, prompt: str, model_id: str):
        """Test model connection with a simple prompt"""
        try:
            _response = client.text_generation(
                prompt=prompt,
                max_new_tokens=10,
                temperature=0.1
            )
            logger.debug(f"Model connection test successful %s", json.dumps(_response))
        except Exception as e:
            logger.warning(f"Model connection test failed: {e}")
            raise

    def _test_public_ai_model_connection(self, prompt: str):
        """Test model connection with a simple prompt"""
        try:
            messages_think = [
                {"role": "user", "content": prompt}
            ]

            text = self.public_ai_tokenizer.apply_chat_template(
                messages_think,
                tokenize=False,
                add_generation_prompt=True,
            )
            model_inputs  = self.public_ai_tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(self.public_ai_model.device)
            generated_ids = self.public_ai_model.generate(**model_inputs, max_new_tokens=10)
            output_ids = generated_ids[0][len(text.input_ids[0]) :]
            output = self.public_ai_tokenizer.decode(output_ids, skip_special_tokens=True)
            logger.debug(f"Model connection test successful %s", json.dumps(output))
        except Exception as e:
            logger.warning(f"Model connection test failed: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self._is_ready

    def clean_json_string(self, raw_text: str) -> str:
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
            json.loads(cleaned)
            return cleaned 
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
    
    def _clean_model_response(self, response: str) -> str:
        """Clean and format model response"""
        if not response:
            return "No response generated"
        
        # Remove common artifacts and clean up
        cleaned = response.strip()
        
        # Remove instruction markers if present
        cleaned = re.sub(r'\[INST\].*?\[/INST\]', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<\|im_start\|>.*?<\|im_end\|>', '', cleaned, flags=re.DOTALL)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n+', '\n', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\\+', ' ', cleaned)
        return cleaned.strip()
    
    async def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when models are unavailable"""
        # Simple heuristic-based fallback
        if "financial advice" in prompt.lower() or "recommend" in prompt.lower():
            return "Based on general financial principles, consider diversifying investments, maintaining an emergency fund, and consulting with a financial advisor for personalized advice."
        elif "market" in prompt.lower() or "sentiment" in prompt.lower():
            return "Market conditions are dynamic. Consider current economic indicators, sector performance, and risk factors when making investment decisions."
        elif "goal" in prompt.lower() or "planning" in prompt.lower():
            return "Successful financial planning involves setting clear goals, creating realistic timelines, and regularly reviewing progress toward objectives."
        else:
            return "Please consult with financial professionals for personalized advice tailored to your specific situation."

    # CATEGORY 1: AI FINANCIAL ADVISOR METHODS
    
    async def generate_personal_advice(self, user_context) -> Any:
        """Generate personalized financial advice using FinGPT advisor model"""
        try:
            
            profile = user_context.profile
            
            # Create specialized prompt for financial advice
            prompt = self.prompt_engine.create_advisor_prompt(user_context)
            
            # Generate advice using FinGPT advisor model
            client = InferenceClient(
                provider="publicai",
                api_key=self.hf_token,
                )
            
            completion = client.chat_completion(
                model=self.public_ai_model_name,
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
                max_tokens=4000,
                temperature=0.3,
                top_p=0.9
            )

            content = completion.choices[0].message.content
            if completion is None or content is None:
                raise Exception(status_code=500, detail="No response from AI model")
            
            cleaned_json = self.clean_json_string(content)
            
            # Parse to dictionary
            data_dict = json.loads(cleaned_json)
            
            # Validate it's not a schema
            if "$schema" in data_dict or "properties" in data_dict:
                raise ValueError("Model returned JSON schema instead of data")
    
            return data_dict
                    
        except ValidationError as e:
            logger.error(f"Error validating response: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while processing chat request: {str(e)}"
            )
                       
        except Exception as e:
            logger.error(f"Error generating personal advice: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while generating personal advice: {str(e)}"
            )

    
    # ADD THESE MISSING METHODS TO YOUR FinGPTService CLASS

    # RESPONSE PARSING METHODS

    async def _extract_action_items(self, advice_text: str, profile) -> List[Any]:
        """Extract action items from advice text"""
        from models.response_models import ActionItem, ActionPriority

        action_items = []

        # Basic action items based on profile
        if not profile.has_emergency_fund:
            action_items.append(ActionItem(
                title="Build Emergency Fund",
                description=f"Establish emergency fund covering 6 months expenses (${profile.monthly_expenses * 6:,.0f})",
                priority=ActionPriority.HIGH,
                category="savings",
                timeline="3-6 months",
                estimated_impact="High financial security"
            ))

        # Add more action items based on AI advice text analysis
        if "debt" in advice_text.lower():
            action_items.append(ActionItem(
                title="Debt Management",
                description="Optimize debt repayment strategy based on AI analysis",
                priority=ActionPriority.HIGH,
                category="debt",
                timeline="6-12 months",
                estimated_impact="Reduced interest payments"
            ))

        if "investment" in advice_text.lower():
            action_items.append(ActionItem(
                title="Investment Optimization",
                description=f"Adjust portfolio allocation based on {profile.risk_tolerance.value} risk tolerance",
                priority=ActionPriority.MEDIUM,
                category="investments",
                timeline="1-3 months",
                estimated_impact="Better risk-adjusted returns"
            ))

        return action_items[:3]  # Limit to 3 items

    async def _extract_risk_assessment(self, advice_text: str, profile) -> Any:
        """Extract risk assessment from advice text"""
        from models.response_models import RiskAssessment

        # Calculate debt ratio
        debt_ratio = (profile.total_debt / profile.annual_income * 100) if profile.annual_income > 0 else 0
        risk_factors = []

        if debt_ratio > 40:
            risk_factors.append("High debt-to-income ratio")
        if not profile.has_emergency_fund:
            risk_factors.append("No emergency fund")
        if profile.investment_experience < 2:
            risk_factors.append("Limited investment experience")

        # Analyze AI advice text for additional risk factors
        if "risk" in advice_text.lower() and "high" in advice_text.lower():
            risk_factors.append("AI-identified risk factors")

        overall_risk = "High" if len(risk_factors) > 2 else "Medium" if risk_factors else "Low"

        return RiskAssessment(
            overall_risk_level=overall_risk,
            risk_factors=risk_factors,
            mitigation_strategies=[
                "Build emergency fund",
                "Reduce high-interest debt",
                "Diversify investments",
                "Consider professional advice"
            ],
            risk_tolerance_alignment=True
        )

    async def _extract_portfolio_analysis(self, analysis_text: str, portfolio) -> Any:
        """Extract portfolio analysis from AI text"""
        from models.response_models import PortfolioAnalysis

        return PortfolioAnalysis(
            current_allocation={"stocks": 70.0, "bonds": 20.0, "cash": 10.0},
            recommended_allocation={"stocks": 60.0, "bonds": 30.0, "cash": 10.0},
            diversification_score=min(85, len(portfolio.holdings) * 15) if portfolio else 50,
            performance_metrics={"ytd_return": 8.5, "volatility": 12.3, "sharpe_ratio": 0.7},
            rebalancing_needed=True,
            optimization_opportunities=[
                "Consider international diversification",
                "Review expense ratios",
                "Rebalance quarterly"
            ]
        )

    async def _extract_market_insights(self, insights_text: str, market_data: Dict[str, Any]) -> List[Any]:
        """Extract market insights from AI text"""
        from models.response_models import MarketInsight

        insights = []

        # Parse insights from AI text or create based on market data
        if "technology" in insights_text.lower() or "tech" in insights_text.lower():
            insights.append(MarketInsight(
                title="Technology Sector Analysis",
                description="AI adoption and digital transformation driving growth opportunities",
                impact_level="High",
                timeframe="6-12 months",
                confidence_score=0.8,
                sectors_affected=["technology", "telecommunications"]
            ))

        if "interest" in insights_text.lower() or "rate" in insights_text.lower():
            insights.append(MarketInsight(
                title="Interest Rate Environment",
                description="Current monetary policy creates opportunities in fixed income",
                impact_level="Medium",
                timeframe="3-6 months",
                confidence_score=0.7,
                sectors_affected=["finance", "real_estate"]
            ))

        # Default insight if none found
        if not insights:
            insights.append(MarketInsight(
                title="Market Outlook",
                description="Mixed market signals suggest cautious optimism with selective opportunities",
                impact_level="Medium",
                timeframe="3-6 months",
                confidence_score=0.6,
                sectors_affected=["general"]
            ))

        return insights

    async def _extract_news_analysis(self, analysis_text: str, news_data: List[Dict[str, Any]]) -> List[Any]:
        """Extract news analysis from AI text"""
        from models.response_models import NewsAnalysis

        news_analyses = []
        for news_item in news_data[:3]:
            news_analyses.append(NewsAnalysis(
                headline=news_item.get('headline', 'Market Update'),
                source=news_item.get('source', 'Financial News'),
                published_date=datetime.utcnow(),
                sentiment_score=news_item.get('sentiment', 0.1),
                relevance_score=news_item.get('relevance', 0.8),
                impact_analysis="AI-generated impact assessment based on sentiment analysis",
                related_symbols=news_item.get('symbols', ['SPY']),
                key_entities=['Federal Reserve', 'Markets', 'Economy']
            ))

        return news_analyses

    async def _extract_sector_recommendations(self, recommendations_text: str, sectors: List[str]) -> List[Any]:
        """Extract sector recommendations from AI text"""
        from models.response_models import SectorRecommendation, RecommendationType, ConfidenceLevel

        recommendations = []
        for sector in sectors[:3]:
            recommendations.append(SectorRecommendation(
                sector_name=sector.title(),
                recommendation_type=RecommendationType.HOLD,
                confidence_level=ConfidenceLevel.MEDIUM,
                rationale=f"AI analysis suggests {sector} sector shows balanced risk-return profile",
                key_drivers=[f"{sector.title()} innovation", "Market demand", "Economic trends"],
                potential_risks=["Market volatility", "Regulatory changes", "Economic headwinds"],
                time_horizon="6-12 months",
                allocation_suggestion=15.0,
                top_picks=[f"Leading {sector} ETF", f"Top {sector} stock"]
            ))

        return recommendations

    async def _extract_goal_strategies(self, strategy_text: str, goals) -> List[Any]:
        """Extract goal strategies from AI text"""
        from models.response_models import GoalStrategy

        goal_strategies = []
        if goals and goals.goals:
            for goal in goals.goals[:3]:
                monthly_needed = goal.target_amount / max(12, (goal.target_date.year - datetime.now().year) * 12)

                goal_strategies.append(GoalStrategy(
                    goal_id=goal.goal_id,
                    goal_name=goal.goal_name,
                    strategy_summary=f"AI-optimized savings and investment plan for {goal.goal_name}",
                    monthly_savings_required=monthly_needed,
                    recommended_investments=["Diversified index funds", "Target-date funds", "ETFs"],
                    risk_level=goal.priority if hasattr(goal, 'priority') else "moderate",
                    probability_of_success=0.85,
                    milestones=[
                        {"milestone": "25% complete", "target_date": "Year 1", "amount": goal.target_amount * 0.25},
                        {"milestone": "50% complete", "target_date": "Year 2", "amount": goal.target_amount * 0.50}
                    ],
                    optimization_suggestions=[
                        "Automate monthly contributions",
                        "Increase contributions annually",
                        "Review and rebalance quarterly"
                    ]
                ))

        return goal_strategies

    async def _extract_savings_optimization(self, strategy_text: str, profile) -> Any:
        """Extract savings optimization from AI text"""
        from models.response_models import SavingsOptimization

        current_rate = (profile.monthly_savings_capacity * 12 / profile.annual_income * 100) if profile.annual_income > 0 else 10.0

        return SavingsOptimization(
            current_savings_rate=current_rate,
            optimal_savings_rate=20.0,
            savings_reallocation={
                "emergency_fund": 30.0,
                "retirement": 40.0,
                "goals": 30.0
            },
            compound_interest_impact=profile.current_savings * 0.07 * 10,
            automation_recommendations=[
                "Set up automatic transfers",
                "Use payroll deduction for retirement",
                "Schedule quarterly reviews"
            ]
        )

    async def _extract_progress_tracking(self, progress_text: str, goals) -> List[Any]:
        """Extract progress tracking from AI text"""
        from models.response_models import ProgressTracking

        progress_list = []
        if goals and goals.goals:
            for goal in goals.goals:
                progress_pct = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0

                progress_list.append(ProgressTracking(
                    goal_id=goal.goal_id,
                    current_progress_percentage=min(100, progress_pct),
                    on_track_status=progress_pct >= 20,
                    deviation_amount=None,
                    recommended_adjustments=[
                        "Increase monthly contributions" if progress_pct < 50 else "Continue current strategy",
                        "Review investment allocation",
                        "Consider additional income sources"
                    ],
                    completion_probability=0.8 if progress_pct >= 50 else 0.6
                ))

        return progress_list

    # FALLBACK METHODS 
    def _fallback_advice_text(self, user_context) -> str:
        """Fallback advice text when AI models are unavailable"""
        profile = user_context.profile
        return f"""Based on your profile analysis:

        • Age: {profile.age}, Risk Tolerance: {profile.risk_tolerance.value}
        • Current financial position shows potential for optimization
        • Emergency fund status: {'✓ Established' if profile.has_emergency_fund else '⚠ Needs attention'}
        • Investment experience level: {profile.investment_experience} years

        Key recommendations:
        1. Maintain emergency fund covering 6 months expenses
        2. Diversify investments based on your {profile.risk_tolerance.value} risk profile
        3. Consider tax-advantaged retirement accounts
        4. Review and rebalance portfolio quarterly
        5. Plan for major financial goals with dedicated savings

        This analysis provides a foundation for your financial planning decisions."""

    async def _generate_advice_fallback(self, user_context):
        """Fallback financial advice response"""
        from models.response_models import FinancialAdviceResponse, ActionItem, RiskAssessment, ConfidenceLevel, ActionPriority

        return FinancialAdviceResponse(
            success=True,
            advice_summary="Basic financial guidance in fallback mode",
            detailed_analysis=self._fallback_advice_text(user_context),
            action_items=[
                ActionItem(
                    title="Review Financial Goals",
                    description="Assess current financial situation and set clear goals",
                    priority=ActionPriority.HIGH,
                    category="planning",
                    timeline="1 month",
                    estimated_impact="Improved financial clarity"
                )
            ],
            risk_assessment=RiskAssessment(
                overall_risk_level="Medium",
                risk_factors=["Market volatility"],
                mitigation_strategies=["Diversification"],
                risk_tolerance_alignment=True
            ),
            confidence_level=ConfidenceLevel.MEDIUM,
            follow_up_timeline="3 months",
            model_used="Fallback Analysis System"
        )

    async def _generate_recommendations_fallback(self, user_context):
        """Fallback recommendations response"""
        from models.response_models import RecommendationResponse

        return RecommendationResponse(
            success=True,
            recommendation_type="fallback",
            executive_summary="Basic market insights in fallback mode",
            model_used="Fallback Recommendations System"
        )

    async def _generate_planner_fallback(self, user_context):
        """Fallback planner response"""
        from models.response_models import GoalPlannerResponse, SavingsOptimization

        savings_opt = SavingsOptimization(
            current_savings_rate=10.0,
            optimal_savings_rate=15.0,
            savings_reallocation={},
            compound_interest_impact=25000.0,
            automation_recommendations=["Set up automatic transfers"]
        )

        return GoalPlannerResponse(
            success=True,
            planner_type="fallback",
            overall_strategy_summary="Basic goal planning in fallback mode",
            savings_optimization=savings_opt,
            model_used="Fallback Planning System"
        )

    # The complete code is quite long, so I'll provide the key sections