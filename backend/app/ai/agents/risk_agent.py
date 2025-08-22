"""
Risk Assessment Agent - Specialized in risk profiling, assessment, and management
"""

from crewai import Agent
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np

from app.ai.tools.analysis_tools import RiskAnalysisTool
from app.ai.tools.calculation_tools import PortfolioCalculatorTool


class RiskAssessmentAgent:
    """AI Agent specialized in comprehensive risk assessment and management"""
    
    def __init__(self):
        self.tools = [
            RiskAnalysisTool(),
            PortfolioCalculatorTool()
        ]
        
        self.agent = Agent(
            role="Senior Risk Assessment Specialist",
            goal="Provide comprehensive risk assessment, profiling, and management recommendations for investors and portfolios",
            backstory="""You are a highly experienced risk management specialist with over 18 years 
            of experience in financial risk assessment and portfolio risk management. You have worked 
            with institutional investors, wealth management firms, and individual clients to assess, 
            measure, and manage various types of investment risks. Your expertise includes behavioral 
            finance, risk psychology, quantitative risk modeling, and regulatory risk frameworks. 
            You are known for your ability to translate complex risk concepts into actionable insights 
            for investors of all experience levels.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    def conduct_risk_profiling(self, user_responses: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Conduct comprehensive risk profiling based on questionnaire responses"""
        try:
            risk_assessment = {
                "user_id": user_profile.get("id"),
                "assessment_type": "comprehensive_risk_profiling",
                "assessor": "Risk Assessment Agent",
                "assessment_date": datetime.now().isoformat(),
                "questionnaire_responses": user_responses,
                "risk_dimensions": {},
                "overall_risk_profile": {},
                "recommendations": {},
                "behavioral_insights": {}
            }
            
            # Analyze different risk dimensions
            risk_assessment["risk_dimensions"] = {
                "risk_capacity": self._assess_risk_capacity(user_profile),
                "risk_tolerance": self._assess_risk_tolerance(user_responses),
                "risk_perception": self._assess_risk_perception(user_responses),
                "loss_aversion": self._assess_loss_aversion(user_responses),
                "time_horizon": self._assess_time_horizon_risk(user_profile, user_responses)
            }
            
            # Calculate overall risk profile
            risk_assessment["overall_risk_profile"] = self._calculate_overall_risk_profile(
                risk_assessment["risk_dimensions"]
            )
            
            # Generate recommendations
            risk_assessment["recommendations"] = self._generate_risk_recommendations(
                risk_assessment["overall_risk_profile"], user_profile
            )
            
            # Behavioral insights
            risk_assessment["behavioral_insights"] = self._analyze_behavioral_patterns(
                user_responses, user_profile
            )
            
            # Risk education suggestions
            risk_assessment["education_suggestions"] = self._suggest_risk_education(
                risk_assessment["overall_risk_profile"]
            )
            
            return risk_assessment
            
        except Exception as e:
            return {"error": f"Risk profiling failed: {str(e)}"}
    
    def assess_portfolio_risk(self, portfolio_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Assess comprehensive portfolio risk"""
        try:
            portfolio_risk_assessment = {
                "portfolio_id": portfolio_data.get("id"),
                "assessment_type": "portfolio_risk_analysis",
                "assessor": "Risk Assessment Agent",
                "assessment_date": datetime.now().isoformat(),
                "risk_metrics": {},
                "concentration_analysis": {},
                "correlation_analysis": {},
                "scenario_analysis": {},
                "risk_attribution": {},
                "recommendations": {}
            }
            
            holdings = portfolio_data.get("holdings", [])
            
            # Calculate portfolio risk metrics
            portfolio_tool = PortfolioCalculatorTool()
            portfolio_metrics = portfolio_tool._run(holdings, user_profile)
            portfolio_risk_assessment["risk_metrics"] = portfolio_metrics.get("risk_metrics", {})
            
            # Concentration risk analysis
            portfolio_risk_assessment["concentration_analysis"] = self._analyze_concentration_risk(holdings)
            
            # Correlation analysis
            portfolio_risk_assessment["correlation_analysis"] = self._analyze_correlation_risk(holdings)
            
            # Scenario analysis
            portfolio_risk_assessment["scenario_analysis"] = self._conduct_scenario_analysis(holdings)
            
            # Risk attribution
            portfolio_risk_assessment["risk_attribution"] = self._analyze_risk_attribution(holdings)
            
            # Risk management recommendations
            portfolio_risk_assessment["recommendations"] = self._generate_portfolio_risk_recommendations(
                portfolio_risk_assessment, user_profile
            )
            
            # Risk monitoring plan
            portfolio_risk_assessment["monitoring_plan"] = self._create_risk_monitoring_plan(
                portfolio_risk_assessment
            )
            
            return portfolio_risk_assessment
            
        except Exception as e:
            return {"error": f"Portfolio risk assessment failed: {str(e)}"}
    
    def analyze_investment_risk(self, symbol: str, exchange: str = "NSE", 
                              investment_amount: float = 100000) -> Dict[str, Any]:
        """Analyze risk of specific investment"""
        try:
            investment_risk = {
                "symbol": symbol,
                "exchange": exchange,
                "investment_amount": investment_amount,
                "assessment_type": "individual_investment_risk",
                "assessor": "Risk Assessment Agent",
                "assessment_date": datetime.now().isoformat()
            }
            
            # Get detailed risk analysis
            risk_tool = RiskAnalysisTool()
            risk_analysis = risk_tool._run(symbol, exchange)
            investment_risk["risk_analysis"] = risk_analysis
            
            if "error" in risk_analysis:
                return {"error": f"Risk analysis failed: {risk_analysis['error']}"}
            
            # Calculate position sizing recommendations
            investment_risk["position_sizing"] = self._calculate_position_sizing(
                risk_analysis, investment_amount
            )
            
            # Risk-adjusted return expectations
            investment_risk["return_expectations"] = self._calculate_risk_adjusted_returns(
                risk_analysis
            )
            
            # Risk mitigation strategies
            investment_risk["mitigation_strategies"] = self._suggest_risk_mitigation(
                risk_analysis, symbol
            )
            
            # Stress testing
            investment_risk["stress_testing"] = self._conduct_stress_testing(
                risk_analysis, investment_amount
            )
            
            return investment_risk
            
        except Exception as e:
            return {"error": f"Investment risk analysis failed: {str(e)}"}
    
    def create_risk_management_plan(self, user_profile: Dict, portfolio_data: Dict = None) -> Dict[str, Any]:
        """Create comprehensive risk management plan"""
        try:
            risk_plan = {
                "user_id": user_profile.get("id"),
                "plan_type": "comprehensive_risk_management",
                "assessor": "Risk Assessment Agent",
                "creation_date": datetime.now().isoformat(),
                "risk_framework": {},
                "risk_limits": {},
                "monitoring_procedures": {},
                "contingency_plans": {},
                "review_schedule": {}
            }
            
            # Establish risk framework
            risk_plan["risk_framework"] = self._establish_risk_framework(user_profile)
            
            # Set risk limits
            risk_plan["risk_limits"] = self._set_risk_limits(user_profile)
            
            # Define monitoring procedures
            risk_plan["monitoring_procedures"] = self._define_monitoring_procedures(user_profile)
            
            # Create contingency plans
            risk_plan["contingency_plans"] = self._create_contingency_plans(user_profile)
            
            # Set review schedule
            risk_plan["review_schedule"] = self._set_review_schedule(user_profile)
            
            # Risk education plan
            risk_plan["education_plan"] = self._create_risk_education_plan(user_profile)
            
            return risk_plan
            
        except Exception as e:
            return {"error": f"Risk management plan creation failed: {str(e)}"}
    
    # Risk profiling helper methods
    def _assess_risk_capacity(self, user_profile: Dict) -> Dict[str, Any]:
        """Assess user's financial capacity to take risk"""
        age = user_profile.get("age", 35)
        income = user_profile.get("annual_income", 600000)
        savings = user_profile.get("current_savings", 100000)
        expenses = user_profile.get("monthly_expenses", 30000) * 12
        
        # Calculate financial metrics
        savings_ratio = savings / income if income > 0 else 0
        expense_ratio = expenses / income if income > 0 else 1
        surplus_ratio = max(0, (income - expenses) / income) if income > 0 else 0
        
        # Age-based capacity
        if age < 30:
            age_capacity = "High"
        elif age < 45:
            age_capacity = "Medium-High"
        elif age < 55:
            age_capacity = "Medium"
        else:
            age_capacity = "Low"
        
        # Financial capacity
        if savings_ratio > 0.5 and surplus_ratio > 0.3:
            financial_capacity = "High"
        elif savings_ratio > 0.3 and surplus_ratio > 0.2:
            financial_capacity = "Medium"
        else:
            financial_capacity = "Low"
        
        # Overall capacity
        capacity_scores = {"High": 4, "Medium-High": 3, "Medium": 2, "Low": 1}
        overall_score = (capacity_scores[age_capacity] + capacity_scores[financial_capacity]) / 2
        
        if overall_score >= 3.5:
            overall_capacity = "High"
        elif overall_score >= 2.5:
            overall_capacity = "Medium"
        else:
            overall_capacity = "Low"
        
        return {
            "age_based_capacity": age_capacity,
            "financial_capacity": financial_capacity,
            "overall_capacity": overall_capacity,
            "capacity_score": overall_score,
            "key_factors": {
                "age": age,
                "savings_ratio": savings_ratio,
                "surplus_ratio": surplus_ratio
            }
        }
    
    def _assess_risk_tolerance(self, responses: Dict) -> Dict[str, Any]:
        """Assess user's psychological risk tolerance"""
        # Risk tolerance questions and scoring
        tolerance_score = 0
        max_score = 0
        
        # Market volatility comfort (1-10 scale)
        volatility_comfort = responses.get("market_volatility_comfort", 5)
        tolerance_score += volatility_comfort
        max_score += 10
        
        # Loss tolerance
        loss_tolerance = responses.get("loss_tolerance", 5)
        tolerance_score += loss_tolerance
        max_score += 10
        
        # Investment knowledge
        knowledge_score = responses.get("investment_knowledge_score", 5)
        tolerance_score += knowledge_score
        max_score += 10
        
        # Risk-return preference
        risk_return_pref = responses.get("risk_return_preference", 5)
        tolerance_score += risk_return_pref
        max_score += 10
        
        # Calculate tolerance percentage
        tolerance_percentage = (tolerance_score / max_score) * 100 if max_score > 0 else 50
        
        # Categorize tolerance
        if tolerance_percentage >= 80:
            tolerance_level = "Very High"
        elif tolerance_percentage >= 65:
            tolerance_level = "High"
        elif tolerance_percentage >= 50:
            tolerance_level = "Medium"
        elif tolerance_percentage >= 35:
            tolerance_level = "Low"
        else:
            tolerance_level = "Very Low"
        
        return {
            "tolerance_level": tolerance_level,
            "tolerance_score": tolerance_percentage,
            "component_scores": {
                "volatility_comfort": volatility_comfort,
                "loss_tolerance": loss_tolerance,
                "knowledge_score": knowledge_score,
                "risk_return_preference": risk_return_pref
            }
        }
    
    def _assess_risk_perception(self, responses: Dict) -> Dict[str, Any]:
        """Assess how user perceives different types of risks"""
        risk_perceptions = {}
        
        # Market risk perception
        market_risk_perception = responses.get("market_risk_perception", 5)
        risk_perceptions["market_risk"] = self._categorize_perception(market_risk_perception)
        
        # Inflation risk perception
        inflation_risk_perception = responses.get("inflation_risk_perception", 5)
        risk_perceptions["inflation_risk"] = self._categorize_perception(inflation_risk_perception)
        
        # Liquidity risk perception
        liquidity_risk_perception = responses.get("liquidity_risk_perception", 5)
        risk_perceptions["liquidity_risk"] = self._categorize_perception(liquidity_risk_perception)
        
        # Overall risk perception
        avg_perception = np.mean([market_risk_perception, inflation_risk_perception, liquidity_risk_perception])
        overall_perception = self._categorize_perception(avg_perception)
        
        return {
            "overall_perception": overall_perception,
            "specific_perceptions": risk_perceptions,
            "perception_score": avg_perception
        }
    
    def _assess_loss_aversion(self, responses: Dict) -> Dict[str, Any]:
        """Assess user's loss aversion characteristics"""
        # Loss aversion scenarios
        loss_aversion_score = 0
        
        # Scenario 1: Would you prefer guaranteed 50k or 50% chance of 120k?
        scenario1 = responses.get("loss_aversion_scenario1", "guaranteed")
        if scenario1 == "guaranteed":
            loss_aversion_score += 2
        else:
            loss_aversion_score += 0
        
        # Scenario 2: Reaction to 20% portfolio loss
        loss_reaction = responses.get("loss_reaction", "hold")
        if loss_reaction == "sell_all":
            loss_aversion_score += 3
        elif loss_reaction == "sell_some":
            loss_aversion_score += 2
        elif loss_reaction == "hold":
            loss_aversion_score += 1
        else:  # buy_more
            loss_aversion_score += 0
        
        # Categorize loss aversion
        if loss_aversion_score >= 4:
            aversion_level = "High"
        elif loss_aversion_score >= 2:
            aversion_level = "Medium"
        else:
            aversion_level = "Low"
        
        return {
            "aversion_level": aversion_level,
            "aversion_score": loss_aversion_score,
            "behavioral_implications": self._get_loss_aversion_implications(aversion_level)
        }
    
    def _assess_time_horizon_risk(self, user_profile: Dict, responses: Dict) -> Dict[str, Any]:
        """Assess time horizon and its impact on risk capacity"""
        investment_horizon = user_profile.get("investment_horizon_years", 10)
        age = user_profile.get("age", 35)
        
        # Time horizon categories
        if investment_horizon >= 15:
            horizon_category = "Very Long Term"
            risk_capacity = "High"
        elif investment_horizon >= 10:
            horizon_category = "Long Term"
            risk_capacity = "Medium-High"
        elif investment_horizon >= 5:
            horizon_category = "Medium Term"
            risk_capacity = "Medium"
        elif investment_horizon >= 2:
            horizon_category = "Short Term"
            risk_capacity = "Low"
        else:
            horizon_category = "Very Short Term"
            risk_capacity = "Very Low"
        
        return {
            "investment_horizon_years": investment_horizon,
            "horizon_category": horizon_category,
            "time_based_risk_capacity": risk_capacity,
            "retirement_years_remaining": max(0, 60 - age),
            "time_diversification_benefit": "High" if investment_horizon >= 10 else "Low"
        }
    
    def _calculate_overall_risk_profile(self, risk_dimensions: Dict) -> Dict[str, Any]:
        """Calculate overall risk profile from all dimensions"""
        # Extract scores from different dimensions
        capacity_score = self._convert_to_score(risk_dimensions["risk_capacity"]["overall_capacity"])
        tolerance_score = risk_dimensions["risk_tolerance"]["tolerance_score"]
        perception_score = risk_dimensions["risk_perception"]["perception_score"] * 10
        
        # Loss aversion adjustment (higher aversion reduces overall risk score)
        aversion_level = risk_dimensions["loss_aversion"]["aversion_level"]
        aversion_adjustment = {"High": -15, "Medium": -5, "Low": 0}[aversion_level]
        
        # Time horizon adjustment
        horizon_capacity = risk_dimensions["time_horizon"]["time_based_risk_capacity"]
        horizon_score = self._convert_to_score(horizon_capacity)
        
        # Calculate weighted overall score
        overall_score = (
            capacity_score * 0.3 +
            tolerance_score * 0.3 +
            perception_score * 0.2 +
            horizon_score * 0.2
        ) + aversion_adjustment
        
        # Ensure score is within bounds
        overall_score = max(0, min(100, overall_score))
        
        # Categorize overall risk profile
        if overall_score >= 80:
            risk_profile = "Very Aggressive"
        elif overall_score >= 65:
            risk_profile = "Aggressive"
        elif overall_score >= 50:
            risk_profile = "Moderate"
        elif overall_score >= 35:
            risk_profile = "Conservative"
        else:
            risk_profile = "Very Conservative"
        
        return {
            "overall_risk_profile": risk_profile,
            "risk_score": overall_score,
            "component_contributions": {
                "risk_capacity": capacity_score * 0.3,
                "risk_tolerance": tolerance_score * 0.3,
                "risk_perception": perception_score * 0.2,
                "time_horizon": horizon_score * 0.2,
                "loss_aversion_adjustment": aversion_adjustment
            },
            "confidence_level": self._calculate_confidence_level(risk_dimensions)
        }
    
    def _generate_risk_recommendations(self, risk_profile: Dict, user_profile: Dict) -> List[str]:
        """Generate personalized risk recommendations"""
        recommendations = []
        
        profile_level = risk_profile["overall_risk_profile"]
        risk_score = risk_profile["risk_score"]
        
        # Asset allocation recommendations
        if profile_level in ["Very Aggressive", "Aggressive"]:
            recommendations.append("Consider 70-90% equity allocation for long-term growth")
            recommendations.append("Include small and mid-cap funds for higher growth potential")
        elif profile_level == "Moderate":
            recommendations.append("Maintain balanced 60-70% equity and 30-40% debt allocation")
            recommendations.append("Focus on diversified large-cap and multi-cap funds")
        else:
            recommendations.append("Prefer conservative 30-50% equity allocation")
            recommendations.append("Emphasize debt funds and fixed deposits for stability")
        
        # Risk management recommendations
        recommendations.append("Maintain emergency fund of 6-12 months expenses")
        recommendations.append("Review and rebalance portfolio quarterly")
        recommendations.append("Consider systematic investment plans (SIP) to average market volatility")
        
        # Behavioral recommendations
        if risk_profile.get("component_contributions", {}).get("loss_aversion_adjustment", 0) < -10:
            recommendations.append("Practice disciplined investing to overcome loss aversion bias")
            recommendations.append("Consider automated investing to reduce emotional decisions")
        
        return recommendations
    
    # Helper methods
    def _categorize_perception(self, score: float) -> str:
        """Categorize risk perception score"""
        if score >= 8:
            return "Very High Concern"
        elif score >= 6:
            return "High Concern"
        elif score >= 4:
            return "Moderate Concern"
        elif score >= 2:
            return "Low Concern"
        else:
            return "Very Low Concern"
    
    def _convert_to_score(self, level: str) -> float:
        """Convert risk level to numerical score"""
        level_scores = {
            "Very Low": 10, "Low": 25, "Medium": 50, 
            "Medium-High": 65, "High": 80, "Very High": 95
        }
        return level_scores.get(level, 50)
    
    def _get_loss_aversion_implications(self, aversion_level: str) -> List[str]:
        """Get behavioral implications of loss aversion level"""
        implications = {
            "High": [
                "May avoid necessary risks for long-term growth",
                "Tendency to sell during market downturns",
                "May prefer guaranteed returns over potentially higher volatile returns"
            ],
            "Medium": [
                "Balanced approach to risk and return",
                "May need encouragement during market volatility",
                "Generally makes rational investment decisions"
            ],
            "Low": [
                "Comfortable with market volatility",
                "May take excessive risks without proper analysis",
                "Good at staying invested during market downturns"
            ]
        }
        return implications.get(aversion_level, [])
    
    def _calculate_confidence_level(self, risk_dimensions: Dict) -> str:
        """Calculate confidence level in risk assessment"""
        # This would analyze consistency across different risk dimensions
        return "High"  # Simplified for now
    
    # Placeholder methods for portfolio risk analysis
    def _analyze_concentration_risk(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Analyze concentration risk in portfolio"""
        return {"concentration_score": 25, "risk_level": "Low"}
    
    def _analyze_correlation_risk(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Analyze correlation risk between holdings"""
        return {"correlation_risk": "Medium", "diversification_benefit": 0.8}
    
    def _conduct_scenario_analysis(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Conduct scenario analysis on portfolio"""
        return {
            "bear_market_impact": -25,
            "bull_market_impact": 35,
            "recession_impact": -30
        }
    
    def _analyze_risk_attribution(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Analyze risk attribution by holdings"""
        return {"top_risk_contributors": ["STOCK1", "STOCK2"]}
    
    def _generate_portfolio_risk_recommendations(self, assessment: Dict, user_profile: Dict) -> List[str]:
        """Generate portfolio-specific risk recommendations"""
        return [
            "Consider reducing concentration in top holdings",
            "Add international diversification",
            "Review correlation between holdings"
        ]
