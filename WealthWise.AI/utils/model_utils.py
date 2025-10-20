"""
Model management and prompt engineering utilities for FinGPT service
"""

import logging
from typing import Dict, Any, List

from models.response_models import FinancialAdviceResponse
from models.user_models import UserProfile

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages FinGPT model lifecycle"""

    def __init__(self):
        self.model_performance = {}

    def track_model_performance(self, model_name: str, latency: float, success: bool):
        """Track model performance metrics"""
        if model_name not in self.model_performance:
            self.model_performance[model_name] = {
                'total_requests': 0,
                'successful_requests': 0
            }

        stats = self.model_performance[model_name]
        stats['total_requests'] += 1
        if success:
            stats['successful_requests'] += 1

class PromptEngine:
    """Creates optimized prompts for FinGPT models"""

    def create_advisor_prompt(self, user_context) -> str:
        """Create prompt for financial advisor model"""

        prompt = f"""You are WealthWise AI, an expert financial advisor specializing in personalized financial planning and investment advice.
## USER PROFILE ANALYSIS
### Demographics & Employment
- Age: {user_context.profile.age} years old
- Location: {user_context.profile.location or 'Not specified'}
- Employment Status: {user_context.profile.employment_status.value}
- Family Dependents: {user_context.profile.family_dependents}
### Financial Snapshot
- Annual Income: ₹{user_context.profile.annual_income:,.2f}
- Monthly Expenses: ₹{user_context.profile.monthly_expenses:,.2f}
- Current Savings: ₹{user_context.profile.current_savings:,.2f}
- Current Investments: ₹{user_context.profile.current_investments:,.2f}
- Monthly Savings Capacity: ₹{user_context.profile.monthly_savings_capacity:,.2f}
### Debt Profile
- Total Outstanding Debt: ₹{user_context.profile.total_debt:,.2f}
- Monthly Debt Payments: ₹{user_context.profile.monthly_debt_payments:,.2f}
### Investment Profile
- Risk Tolerance: {user_context.profile.risk_tolerance.value}
- Investment Experience: {user_context.profile.investment_experience} years
- Preferred Sectors: {', '.join([s.value for s in user_context.profile.preferred_sectors]) if user_context.profile.preferred_sectors else 'No specific preferences'}
- Emergency Fund: {'Yes' if user_context.profile.has_emergency_fund else 'No'}
- Monthly Retirement Contributions: ₹{user_context.profile.retirement_contributions:,.2f}
### Investment Horizons
- Short-term ({user_context.profile.short_term_horizon or 'Not specified'} years): Goals within 1-5 years
- Medium-term ({user_context.profile.medium_term_horizon or 'Not specified'} years): Goals within 5-15 years
- Long-term ({user_context.profile.long_term_horizon or 'Not specified'} years): Retirement and wealth building
### Preferences & Constraints
- ESG Preference: {'Yes' if user_context.profile.esg_preference else 'No'}
- Cryptocurrency Tolerance: {'Yes' if user_context.profile.crypto_tolerance else 'No'}
- Additional Constraints: {', '.join(user_context.profile.investment_constraints) if user_context.profile.investment_constraints else 'None'}
---
## YOUR TASK
Provide comprehensive, actionable financial advice based on this profile. Your response MUST be valid JSON matching the exact structure below.
Generate a detailed analysis covering:
1. **Overall Financial Health Assessment**: Evaluate income vs expenses, savings rate, debt burden, emergency fund status
2. **Personalized Action Items**: Specific, actionable steps prioritized by urgency and impact
3. **Risk Analysis**: Assess current financial risks and provide mitigation strategies
4. **Portfolio Recommendations**: If applicable, suggest optimal asset allocation based on risk tolerance
5. **Future Projections**: Project net worth and savings growth over 1, 3, and 5 years
6. **Retirement Readiness**: Evaluate preparedness for retirement based on age and savings
## REQUIRED JSON OUTPUT FORMAT
You MUST respond with ONLY valid JSON data (no schema definitions, no explanations outside JSON).
{{
  "advice_summary": "A concise 2-3 sentence executive summary of your key recommendations",
  "detailed_analysis": "A comprehensive 3-4 paragraph analysis of the user's financial situation, covering income/expense ratio, savings capacity, debt management, investment readiness, and overall financial health",
  "action_items": [
    {{
      "title": "Clear, actionable title",
      "description": "Detailed description explaining what to do and why",
      "priority": "urgent|high|medium|low",
      "category": "savings|debt|investment|insurance|tax|retirement",
      "timeline": "immediate|1-3 months|3-6 months|6-12 months|1+ years",
      "estimated_impact": "Quantified impact (e.g., +10% annual returns, -₹50,000 debt)",
      "resources_needed": ["List of tools, accounts, or resources needed"],
      "success_metrics": ["How to measure success"]
    }}
  ],
  "risk_assessment": {{
    "overall_risk_level": "low|moderate|high|very_high",
    "risk_factors": ["List specific financial risks identified"],
    "mitigation_strategies": ["Specific strategies to reduce each risk"],
    "risk_tolerance_alignment": true,
    "stress_test_results": {{
      "recession_impact": "Description of portfolio impact in recession",
      "inflation_impact": "Impact of high inflation scenario",
      "job_loss_resilience": "Months of expenses covered"
    }}
  }},
  "portfolio_analysis": {{
    "current_allocation": {{
      "cash": 10.0,
      "fixed_income": 30.0,
      "equities": 50.0,
      "alternatives": 10.0
    }},
    "recommended_allocation": {{
      "cash": 15.0,
      "fixed_income": 35.0,
      "equities": 45.0,
      "alternatives": 5.0
    }},
    "diversification_score": 75,
    "performance_metrics": {{
      "expected_annual_return": 8.5,
      "volatility": 12.3,
      "sharpe_ratio": 1.2
    }},
    "rebalancing_needed": true,
    "underperforming_assets": ["List any underperforming holdings"],
    "optimization_opportunities": ["Specific ways to improve portfolio"]
  }},
  "confidence_level": "very_high|high|medium|low|very_low",
  "follow_up_timeline": "Recommend when to review (e.g., 'Review in 3 months, reassess portfolio quarterly, annual comprehensive review')",
  "additional_resources": [
    "https://investopedia.com/relevant-article",
    "https://nseindia.com/education",
    "Specific book or course recommendations"
  ],
  "projected_net_worth": {{
    "2025": 520000.0,
    "2026": 595000.0,
    "2027": 680000.0,
    "2030": 950000.0
  }},
  "savings_projections": {{
    "2025": 85000.0,
    "2026": 100000.0,
    "2027": 118000.0,
    "2030": 175000.0
  }},
  "retirement_readiness": {{
    "current_retirement_score": 65,
    "target_retirement_age": 60,
    "projected_retirement_corpus": 15000000.0,
    "monthly_retirement_income": 125000.0,
    "gap_analysis": "Description of any gaps between target and projection",
    "recommendations": ["Specific steps to improve retirement readiness"]
  }}
}}

CRITICAL INSTRUCTIONS:
- Output ONLY the JSON object above with actual data
- Do NOT include schema definitions or "$schema" fields
- Do NOT wrap in markdown code blocks
- Do NOT include these fields (they will be added automatically):
  - success, timestamp, request_id, processing_time_ms,model_used
- All monetary values in Indian Rupees (₹)
- Provide realistic, actionable advice based on the user's actual profile
- Consider their risk tolerance, investment experience, and time horizons
- Be specific with numbers and recommendations
"""
    
        return prompt

    def create_portfolio_analysis_prompt(self, user_context) -> str:
        """Create prompt for portfolio analysis"""
        portfolio = user_context.portfolio
        profile = user_context.profile

        prompt = f"""[INST] As a portfolio analyst, analyze this investment portfolio:

                Portfolio Overview:
                - Total Value: ${portfolio.total_value:,.0f}
                - Cash Balance: ${portfolio.cash_balance:,.0f}

                User Profile:
                - Age: {profile.age}
                - Risk Tolerance: {profile.risk_tolerance.value}
                - Investment Experience: {profile.investment_experience} years

                Provide detailed analysis including:
                1. Asset allocation assessment
                2. Diversification analysis
                3. Risk evaluation
                4. Rebalancing recommendations
                5. Optimization opportunities [/INST]"""

        return prompt

    def create_risk_assessment_prompt(self, user_context) -> str:
        """Create prompt for risk assessment"""
        profile = user_context.profile

        prompt = f"""[INST] As a financial risk analyst, evaluate this profile:

                    Financial Situation:
                    - Annual Income: ${profile.annual_income:,.0f}
                    - Total Debt: ${profile.total_debt:,.0f}
                    - Emergency Fund: {'Yes' if profile.has_emergency_fund else 'No'}
                    - Age: {profile.age}
                    - Dependents: {profile.family_dependents}

                    Assess and provide:
                    1. Overall financial risk level
                    2. Key risk factors
                    3. Risk mitigation strategies
                    4. Insurance needs
                    5. Specific action items [/INST]"""

        return prompt

    def create_market_insights_prompt(self, user_context, market_data: Dict[str, Any]) -> str:
        """Create prompt for market insights"""
        symbols = market_data.get('symbols', [])

        prompt = f"""[INST] As a market analyst, provide insights on current conditions:

                Market Data:
                - Symbols: {', '.join(symbols[:5])}
                - Timeframe: {market_data.get('timeframe', '1M')}

                User Profile:
                - Risk Tolerance: {user_context.profile.risk_tolerance.value}
                - Experience: {user_context.profile.investment_experience} years

                Provide insights on:
                1. Market trends and outlook
                2. Sector opportunities
                3. Risk factors
                4. Recommended positioning
                5. Key events to monitor [/INST]"""

        return prompt