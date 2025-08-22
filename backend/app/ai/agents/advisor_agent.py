"""
Investment Advisor Agent - Provides personalized investment recommendations and portfolio advice
"""

from crewai import Agent
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.ai.tools.market_tools import MarketDataTool, StockAnalysisTool, MutualFundAnalysisTool
from app.ai.tools.calculation_tools import PortfolioCalculatorTool, GoalCalculatorTool
from app.ai.agents.analyst_agent import FundamentalAnalystAgent


class InvestmentAdvisorAgent:
    """AI Agent specialized in providing personalized investment advice and portfolio recommendations"""
    
    def __init__(self):
        self.tools = [
            MarketDataTool(),
            StockAnalysisTool(),
            MutualFundAnalysisTool(),
            PortfolioCalculatorTool(),
            GoalCalculatorTool()
        ]
        
        self.analyst_agent = FundamentalAnalystAgent()
        
        self.agent = Agent(
            role="Senior Investment Advisor",
            goal="Provide personalized investment advice and portfolio recommendations based on individual investor profiles, goals, and risk tolerance",
            backstory="""You are an experienced investment advisor with over 20 years of experience 
            in wealth management and financial planning. You specialize in creating personalized 
            investment strategies for Indian investors across different life stages and financial goals. 
            Your expertise includes asset allocation, goal-based investing, tax-efficient planning, 
            and risk management. You have helped thousands of clients achieve their financial objectives 
            through disciplined investing and strategic portfolio construction.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=True,
            max_iter=3
        )
    
    def create_investment_plan(self, user_profile: Dict, goals: List[Dict]) -> Dict[str, Any]:
        """Create comprehensive investment plan based on user profile and goals"""
        try:
            investment_plan = {
                "user_id": user_profile.get("id"),
                "plan_type": "comprehensive_investment_plan",
                "advisor": "Investment Advisor Agent",
                "creation_date": datetime.now().isoformat(),
                "user_profile_summary": self._summarize_user_profile(user_profile),
                "risk_assessment": self._assess_user_risk_profile(user_profile),
                "asset_allocation": self._recommend_asset_allocation(user_profile),
                "goal_based_planning": {},
                "investment_recommendations": {},
                "implementation_strategy": {},
                "monitoring_plan": {}
            }
            
            # Goal-based planning
            for goal in goals:
                goal_plan = self._create_goal_based_plan(goal, user_profile)
                investment_plan["goal_based_planning"][goal.get("name", "Goal")] = goal_plan
            
            # Investment recommendations
            investment_plan["investment_recommendations"] = self._generate_investment_recommendations(
                user_profile, goals
            )
            
            # Implementation strategy
            investment_plan["implementation_strategy"] = self._create_implementation_strategy(
                user_profile, investment_plan["investment_recommendations"]
            )
            
            # Monitoring plan
            investment_plan["monitoring_plan"] = self._create_monitoring_plan(user_profile, goals)
            
            # Summary and next steps
            investment_plan["executive_summary"] = self._create_executive_summary(investment_plan)
            investment_plan["next_steps"] = self._define_next_steps(investment_plan)
            
            return investment_plan
            
        except Exception as e:
            return {"error": f"Investment plan creation failed: {str(e)}"}
    
    def analyze_current_portfolio(self, portfolio_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Analyze current portfolio and provide recommendations"""
        try:
            portfolio_analysis = {
                "portfolio_id": portfolio_data.get("id"),
                "analysis_type": "current_portfolio_review",
                "advisor": "Investment Advisor Agent",
                "analysis_date": datetime.now().isoformat()
            }
            
            # Get portfolio calculations
            portfolio_tool = PortfolioCalculatorTool()
            holdings = portfolio_data.get("holdings", [])
            portfolio_metrics = portfolio_tool._run(holdings, user_profile)
            portfolio_analysis["portfolio_metrics"] = portfolio_metrics
            
            # Portfolio health assessment
            portfolio_analysis["health_assessment"] = self._assess_portfolio_health(
                portfolio_metrics, user_profile
            )
            
            # Rebalancing recommendations
            portfolio_analysis["rebalancing_recommendations"] = self._generate_rebalancing_advice(
                portfolio_metrics, user_profile
            )
            
            # Individual holding analysis
            portfolio_analysis["holding_analysis"] = self._analyze_individual_holdings(holdings)
            
            # Performance attribution
            portfolio_analysis["performance_review"] = self._review_portfolio_performance(
                portfolio_metrics, user_profile
            )
            
            # Improvement suggestions
            portfolio_analysis["improvement_suggestions"] = self._suggest_portfolio_improvements(
                portfolio_analysis, user_profile
            )
            
            return portfolio_analysis
            
        except Exception as e:
            return {"error": f"Portfolio analysis failed: {str(e)}"}
    
    def recommend_investments(self, user_profile: Dict, investment_amount: float, 
                            investment_horizon: str = "medium_term") -> Dict[str, Any]:
        """Recommend specific investments based on user profile and amount"""
        try:
            recommendations = {
                "user_id": user_profile.get("id"),
                "investment_amount": investment_amount,
                "investment_horizon": investment_horizon,
                "advisor": "Investment Advisor Agent",
                "recommendation_date": datetime.now().isoformat(),
                "recommended_allocation": {},
                "specific_recommendations": {},
                "alternative_options": {},
                "implementation_guide": {}
            }
            
            # Determine allocation based on user profile
            risk_profile = user_profile.get("risk_profile", "moderate")
            age = user_profile.get("age", 35)
            
            allocation = self._calculate_optimal_allocation(
                risk_profile, age, investment_horizon, investment_amount
            )
            recommendations["recommended_allocation"] = allocation
            
            # Generate specific investment recommendations
            for asset_class, percentage in allocation.items():
                amount = investment_amount * (percentage / 100)
                specific_recs = self._recommend_specific_investments(
                    asset_class, amount, user_profile, investment_horizon
                )
                recommendations["specific_recommendations"][asset_class] = specific_recs
            
            # Alternative options
            recommendations["alternative_options"] = self._suggest_alternative_options(
                recommendations["specific_recommendations"], user_profile
            )
            
            # Implementation guide
            recommendations["implementation_guide"] = self._create_investment_implementation_guide(
                recommendations, user_profile
            )
            
            # Risk warnings and disclaimers
            recommendations["risk_warnings"] = self._generate_risk_warnings(
                recommendations, user_profile
            )
            
            return recommendations
            
        except Exception as e:
            return {"error": f"Investment recommendation failed: {str(e)}"}
    
    def create_sip_strategy(self, user_profile: Dict, monthly_amount: float, 
                          goals: List[Dict] = None) -> Dict[str, Any]:
        """Create systematic investment plan (SIP) strategy"""
        try:
            sip_strategy = {
                "user_id": user_profile.get("id"),
                "monthly_sip_amount": monthly_amount,
                "strategy_type": "systematic_investment_plan",
                "advisor": "Investment Advisor Agent",
                "creation_date": datetime.now().isoformat(),
                "sip_allocation": {},
                "fund_recommendations": {},
                "timing_strategy": {},
                "review_schedule": {}
            }
            
            # Determine SIP allocation
            risk_profile = user_profile.get("risk_profile", "moderate")
            sip_allocation = self._determine_sip_allocation(risk_profile, monthly_amount, goals)
            sip_strategy["sip_allocation"] = sip_allocation
            
            # Recommend specific funds for SIP
            for category, amount in sip_allocation.items():
                fund_recs = self._recommend_sip_funds(category, amount, user_profile)
                sip_strategy["fund_recommendations"][category] = fund_recs
            
            # Timing and execution strategy
            sip_strategy["timing_strategy"] = self._create_sip_timing_strategy(user_profile)
            
            # Review and adjustment schedule
            sip_strategy["review_schedule"] = self._create_sip_review_schedule()
            
            # SIP optimization tips
            sip_strategy["optimization_tips"] = self._provide_sip_optimization_tips(user_profile)
            
            return sip_strategy
            
        except Exception as e:
            return {"error": f"SIP strategy creation failed: {str(e)}"}
    
    def provide_market_outlook(self, time_horizon: str = "medium_term") -> Dict[str, Any]:
        """Provide market outlook and investment implications"""
        try:
            market_outlook = {
                "outlook_type": "market_analysis",
                "time_horizon": time_horizon,
                "advisor": "Investment Advisor Agent",
                "analysis_date": datetime.now().isoformat(),
                "market_assessment": {},
                "sector_outlook": {},
                "investment_themes": {},
                "risk_factors": {},
                "opportunities": {}
            }
            
            # Overall market assessment
            market_outlook["market_assessment"] = self._assess_overall_market(time_horizon)
            
            # Sector-wise outlook
            sectors = ["Technology", "Banking", "Pharmaceuticals", "FMCG", "Infrastructure"]
            for sector in sectors:
                sector_view = self.analyst_agent._get_sector_outlook(sector)
                market_outlook["sector_outlook"][sector] = sector_view
            
            # Investment themes
            market_outlook["investment_themes"] = self._identify_investment_themes(time_horizon)
            
            # Risk factors
            market_outlook["risk_factors"] = self._identify_market_risks(time_horizon)
            
            # Investment opportunities
            market_outlook["opportunities"] = self._identify_market_opportunities(time_horizon)
            
            # Strategic recommendations
            market_outlook["strategic_recommendations"] = self._provide_strategic_recommendations(
                market_outlook
            )
            
            return market_outlook
            
        except Exception as e:
            return {"error": f"Market outlook analysis failed: {str(e)}"}
    
    # Helper methods for user profile analysis
    def _summarize_user_profile(self, user_profile: Dict) -> Dict[str, Any]:
        """Summarize user profile for investment planning"""
        return {
            "age": user_profile.get("age"),
            "income": user_profile.get("annual_income"),
            "risk_profile": user_profile.get("risk_profile"),
            "investment_experience": user_profile.get("investment_experience"),
            "investment_horizon": user_profile.get("investment_horizon_years"),
            "current_savings": user_profile.get("current_savings"),
            "monthly_surplus": user_profile.get("annual_income", 0) / 12 - user_profile.get("monthly_expenses", 0)
        }
    
    def _assess_user_risk_profile(self, user_profile: Dict) -> Dict[str, Any]:
        """Assess user's risk profile comprehensively"""
        risk_profile = user_profile.get("risk_profile", "moderate")
        age = user_profile.get("age", 35)
        experience = user_profile.get("investment_experience", "intermediate")
        
        # Risk capacity based on age
        risk_capacity = "High" if age < 35 else "Medium" if age < 50 else "Low"
        
        # Risk tolerance based on profile
        risk_tolerance_map = {
            "conservative": "Low",
            "moderate": "Medium", 
            "aggressive": "High",
            "very_aggressive": "Very High"
        }
        risk_tolerance = risk_tolerance_map.get(risk_profile, "Medium")
        
        return {
            "stated_risk_profile": risk_profile,
            "risk_capacity": risk_capacity,
            "risk_tolerance": risk_tolerance,
            "overall_risk_assessment": self._determine_overall_risk_level(risk_capacity, risk_tolerance),
            "risk_recommendations": self._provide_risk_recommendations(age, risk_profile, experience)
        }
    
    def _recommend_asset_allocation(self, user_profile: Dict) -> Dict[str, float]:
        """Recommend asset allocation based on user profile"""
        risk_profile = user_profile.get("risk_profile", "moderate")
        age = user_profile.get("age", 35)
        
        # Base allocation templates
        allocations = {
            "conservative": {"equity": 30, "debt": 60, "gold": 5, "cash": 5},
            "moderate": {"equity": 60, "debt": 30, "gold": 5, "cash": 5},
            "aggressive": {"equity": 80, "debt": 15, "gold": 3, "cash": 2},
            "very_aggressive": {"equity": 90, "debt": 8, "gold": 1, "cash": 1}
        }
        
        base_allocation = allocations.get(risk_profile, allocations["moderate"])
        
        # Age-based adjustment (reduce equity by 1% for every year above 35)
        if age > 35:
            equity_reduction = min(20, age - 35)  # Max 20% reduction
            base_allocation["equity"] -= equity_reduction
            base_allocation["debt"] += equity_reduction
        
        return base_allocation
    
    def _create_goal_based_plan(self, goal: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Create plan for specific financial goal"""
        goal_calculator = GoalCalculatorTool()
        goal_calculation = goal_calculator._run(goal, user_profile)
        
        if "error" in goal_calculation:
            return {"error": goal_calculation["error"]}
        
        # Add advisor recommendations
        goal_plan = goal_calculation.copy()
        goal_plan["advisor_recommendations"] = self._provide_goal_specific_advice(goal, goal_calculation)
        goal_plan["investment_strategy"] = self._suggest_goal_investment_strategy(goal, user_profile)
        goal_plan["monitoring_metrics"] = self._define_goal_monitoring_metrics(goal)
        
        return goal_plan
    
    def _generate_investment_recommendations(self, user_profile: Dict, goals: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive investment recommendations"""
        recommendations = {
            "core_portfolio": self._recommend_core_portfolio(user_profile),
            "satellite_investments": self._recommend_satellite_investments(user_profile),
            "tax_saving_investments": self._recommend_tax_saving_investments(user_profile),
            "goal_specific_investments": {}
        }
        
        # Goal-specific recommendations
        for goal in goals:
            goal_name = goal.get("name", "Goal")
            goal_investments = self._recommend_goal_specific_investments(goal, user_profile)
            recommendations["goal_specific_investments"][goal_name] = goal_investments
        
        return recommendations
    
    def _create_implementation_strategy(self, user_profile: Dict, recommendations: Dict) -> Dict[str, Any]:
        """Create implementation strategy for investment recommendations"""
        return {
            "phase_1": {
                "timeline": "Month 1-2",
                "actions": [
                    "Set up investment accounts",
                    "Complete KYC and documentation",
                    "Start emergency fund building",
                    "Begin core portfolio SIPs"
                ]
            },
            "phase_2": {
                "timeline": "Month 3-6", 
                "actions": [
                    "Add satellite investments",
                    "Optimize tax-saving investments",
                    "Review and adjust allocations",
                    "Set up goal-based investments"
                ]
            },
            "phase_3": {
                "timeline": "Month 6+",
                "actions": [
                    "Regular portfolio review",
                    "Rebalancing as needed",
                    "Goal progress monitoring",
                    "Strategy refinement"
                ]
            },
            "automation_setup": self._suggest_automation_setup(user_profile),
            "documentation_required": self._list_required_documentation()
        }
    
    def _create_monitoring_plan(self, user_profile: Dict, goals: List[Dict]) -> Dict[str, Any]:
        """Create monitoring and review plan"""
        return {
            "review_frequency": {
                "portfolio_review": "Quarterly",
                "goal_progress": "Monthly",
                "rebalancing_check": "Semi-annually",
                "strategy_review": "Annually"
            },
            "key_metrics_to_track": [
                "Portfolio returns vs benchmark",
                "Asset allocation drift",
                "Goal progress percentage",
                "Risk metrics",
                "Tax efficiency"
            ],
            "trigger_events": [
                "Major life events",
                "Significant market movements",
                "Goal timeline changes",
                "Income changes",
                "Risk profile changes"
            ],
            "review_checklist": self._create_review_checklist()
        }
    
    def _create_executive_summary(self, investment_plan: Dict) -> str:
        """Create executive summary of investment plan"""
        return """
        Executive Summary:
        
        Based on your financial profile and goals, we recommend a diversified investment 
        approach with systematic investing through SIPs. The strategy focuses on long-term 
        wealth creation while managing risk appropriately for your profile.
        
        Key recommendations include building a core portfolio of equity and debt funds,
        maintaining adequate emergency funds, and implementing goal-based investing for 
        specific objectives.
        
        Regular monitoring and periodic rebalancing will ensure the strategy remains 
        aligned with your evolving needs and market conditions.
        """
    
    def _define_next_steps(self, investment_plan: Dict) -> List[str]:
        """Define immediate next steps for implementation"""
        return [
            "Review and approve the investment plan",
            "Complete necessary account openings and KYC",
            "Set up emergency fund in liquid instruments",
            "Start core portfolio SIPs",
            "Schedule first quarterly review"
        ]
    
    # Additional helper methods would continue here...
    # Due to length constraints, I'll include key methods and indicate where others would go
    
    def _assess_portfolio_health(self, portfolio_metrics: Dict, user_profile: Dict) -> Dict[str, str]:
        """Assess overall portfolio health"""
        return {
            "diversification": "Good" if portfolio_metrics.get("portfolio_metrics", {}).get("concentration_risk", 0) < 30 else "Needs Improvement",
            "risk_alignment": "Appropriate" if portfolio_metrics.get("risk_metrics", {}).get("risk_category") == user_profile.get("risk_profile") else "Misaligned",
            "performance": "Satisfactory" if portfolio_metrics.get("portfolio_metrics", {}).get("returns_percentage", 0) > 0 else "Below Expectations",
            "overall_health": "Healthy"
        }
    
    def _determine_overall_risk_level(self, risk_capacity: str, risk_tolerance: str) -> str:
        """Determine overall risk level"""
        # Simple logic - take the lower of capacity and tolerance
        risk_levels = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}
        capacity_level = risk_levels.get(risk_capacity, 2)
        tolerance_level = risk_levels.get(risk_tolerance, 2)
        
        overall_level = min(capacity_level, tolerance_level)
        level_names = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
        return level_names.get(overall_level, "Medium")
    
    def _provide_risk_recommendations(self, age: int, risk_profile: str, experience: str) -> List[str]:
        """Provide risk-related recommendations"""
        recommendations = []
        
        if age < 30:
            recommendations.append("Young age allows for higher risk tolerance - consider equity-heavy allocation")
        elif age > 55:
            recommendations.append("Approaching retirement - consider reducing risk gradually")
        
        if experience == "beginner":
            recommendations.append("Start with diversified mutual funds before individual stocks")
        
        return recommendations
    
    # Placeholder methods for remaining functionality
    def _recommend_core_portfolio(self, user_profile: Dict) -> Dict[str, Any]:
        return {"large_cap_fund": "Recommended", "debt_fund": "Recommended"}
    
    def _recommend_satellite_investments(self, user_profile: Dict) -> Dict[str, Any]:
        return {"mid_cap_fund": "Optional", "international_fund": "Optional"}
    
    def _recommend_tax_saving_investments(self, user_profile: Dict) -> Dict[str, Any]:
        return {"elss_fund": "Recommended", "ppf": "Recommended"}
    
    def _assess_overall_market(self, time_horizon: str) -> Dict[str, str]:
        return {"outlook": "Cautiously Optimistic", "rationale": "Mixed signals in market"}
    
    def _identify_investment_themes(self, time_horizon: str) -> List[str]:
        return ["Digital transformation", "Healthcare innovation", "Sustainable investing"]
    
    def _identify_market_risks(self, time_horizon: str) -> List[str]:
        return ["Inflation concerns", "Geopolitical tensions", "Interest rate changes"]
    
    def _identify_market_opportunities(self, time_horizon: str) -> List[str]:
        return ["Emerging market growth", "Technology adoption", "Infrastructure development"]
