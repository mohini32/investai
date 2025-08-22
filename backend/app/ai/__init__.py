"""
AI module for InvestAI - Multi-agent system for financial analysis and recommendations
"""

from app.ai.crew import InvestAICrew
from app.ai.agents.analyst_agent import FundamentalAnalystAgent
from app.ai.agents.advisor_agent import InvestmentAdvisorAgent
from app.ai.agents.risk_agent import RiskAssessmentAgent
from app.ai.agents.tax_agent import TaxPlanningAgent

__all__ = [
    "InvestAICrew",
    "FundamentalAnalystAgent",
    "InvestmentAdvisorAgent", 
    "RiskAssessmentAgent",
    "TaxPlanningAgent",
]
