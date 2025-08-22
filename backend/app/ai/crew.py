"""
InvestAI Crew - Multi-agent system orchestration using CrewAI
"""

from crewai import Crew, Task, Process
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.ai.agents.analyst_agent import FundamentalAnalystAgent
from app.ai.agents.advisor_agent import InvestmentAdvisorAgent
from app.ai.agents.risk_agent import RiskAssessmentAgent
from app.ai.agents.tax_agent import TaxPlanningAgent


class InvestAICrew:
    """Main orchestrator for InvestAI multi-agent system"""
    
    def __init__(self):
        # Initialize all agents
        self.analyst_agent = FundamentalAnalystAgent()
        self.advisor_agent = InvestmentAdvisorAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.tax_agent = TaxPlanningAgent()
        
        # Create the crew
        self.crew = Crew(
            agents=[
                self.analyst_agent.agent,
                self.advisor_agent.agent,
                self.risk_agent.agent,
                self.tax_agent.agent
            ],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def comprehensive_investment_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive investment analysis using all agents"""
        try:
            analysis_result = {
                "request_id": request.get("request_id", f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "analysis_type": "comprehensive_investment_analysis",
                "request_details": request,
                "analysis_date": datetime.now().isoformat(),
                "agent_analyses": {},
                "integrated_recommendations": {},
                "executive_summary": ""
            }
            
            symbol = request.get("symbol")
            exchange = request.get("exchange", "NSE")
            user_profile = request.get("user_profile", {})
            investment_amount = request.get("investment_amount", 100000)
            
            if not symbol:
                return {"error": "Symbol is required for analysis"}
            
            # Task 1: Fundamental Analysis
            fundamental_task = Task(
                description=f"""Perform comprehensive fundamental analysis of {symbol} listed on {exchange}.
                Analyze the company's financial health, business model, competitive position, and growth prospects.
                Provide detailed valuation assessment and investment recommendation with rationale.""",
                agent=self.analyst_agent.agent,
                expected_output="Detailed fundamental analysis report with recommendation and key metrics"
            )
            
            # Task 2: Risk Assessment
            risk_task = Task(
                description=f"""Conduct thorough risk analysis of {symbol} investment.
                Assess volatility, beta, downside risk, and various risk metrics.
                Consider the investment amount of ₹{investment_amount:,.0f} and provide position sizing recommendations.""",
                agent=self.risk_agent.agent,
                expected_output="Comprehensive risk assessment with risk metrics and mitigation strategies"
            )
            
            # Task 3: Investment Advisory
            advisory_task = Task(
                description=f"""Based on the fundamental analysis and risk assessment, provide personalized 
                investment advice for {symbol}. Consider the user's risk profile, investment goals, and 
                current portfolio context. Recommend optimal allocation and investment strategy.""",
                agent=self.advisor_agent.agent,
                expected_output="Personalized investment recommendation with allocation strategy"
            )
            
            # Task 4: Tax Planning
            tax_task = Task(
                description=f"""Analyze tax implications of investing ₹{investment_amount:,.0f} in {symbol}.
                Consider capital gains tax, holding period optimization, and integration with overall tax strategy.
                Provide tax-efficient investment approach.""",
                agent=self.tax_agent.agent,
                expected_output="Tax analysis and optimization recommendations"
            )
            
            # Execute tasks
            tasks = [fundamental_task, risk_task, advisory_task, tax_task]
            
            # For now, execute agents individually (CrewAI integration can be enhanced)
            analysis_result["agent_analyses"]["fundamental"] = self.analyst_agent.analyze_stock(
                symbol, exchange, "comprehensive"
            )
            
            analysis_result["agent_analyses"]["risk"] = self.risk_agent.analyze_investment_risk(
                symbol, exchange, investment_amount
            )
            
            analysis_result["agent_analyses"]["advisory"] = self.advisor_agent.recommend_investments(
                user_profile, investment_amount, "medium_term"
            )
            
            # Integrate all analyses
            analysis_result["integrated_recommendations"] = self._integrate_agent_recommendations(
                analysis_result["agent_analyses"], user_profile, request
            )
            
            # Generate executive summary
            analysis_result["executive_summary"] = self._generate_executive_summary(
                analysis_result["integrated_recommendations"], symbol
            )
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"Comprehensive analysis failed: {str(e)}"}
    
    def portfolio_optimization_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform portfolio optimization using multiple agents"""
        try:
            optimization_result = {
                "request_id": request.get("request_id", f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "analysis_type": "portfolio_optimization",
                "request_details": request,
                "analysis_date": datetime.now().isoformat(),
                "current_portfolio_analysis": {},
                "optimization_recommendations": {},
                "implementation_plan": {}
            }
            
            portfolio_data = request.get("portfolio_data", {})
            user_profile = request.get("user_profile", {})
            goals = request.get("goals", [])
            
            if not portfolio_data:
                return {"error": "Portfolio data is required for optimization"}
            
            # Analyze current portfolio
            optimization_result["current_portfolio_analysis"] = {
                "advisor_analysis": self.advisor_agent.analyze_current_portfolio(portfolio_data, user_profile),
                "risk_analysis": self.risk_agent.assess_portfolio_risk(portfolio_data, user_profile),
                "tax_analysis": self.tax_agent.analyze_tax_harvesting_opportunities(portfolio_data, user_profile)
            }
            
            # Generate optimization recommendations
            optimization_result["optimization_recommendations"] = self._generate_portfolio_optimization(
                optimization_result["current_portfolio_analysis"], user_profile, goals
            )
            
            # Create implementation plan
            optimization_result["implementation_plan"] = self._create_portfolio_implementation_plan(
                optimization_result["optimization_recommendations"], user_profile
            )
            
            return optimization_result
            
        except Exception as e:
            return {"error": f"Portfolio optimization failed: {str(e)}"}
    
    def financial_planning_consultation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive financial planning consultation"""
        try:
            consultation_result = {
                "request_id": request.get("request_id", f"planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "consultation_type": "comprehensive_financial_planning",
                "request_details": request,
                "consultation_date": datetime.now().isoformat(),
                "financial_health_assessment": {},
                "goal_based_planning": {},
                "investment_strategy": {},
                "risk_management_plan": {},
                "tax_optimization_plan": {}
            }
            
            user_profile = request.get("user_profile", {})
            goals = request.get("goals", [])
            current_portfolio = request.get("current_portfolio", {})
            transactions = request.get("transactions", [])
            
            # Financial health assessment
            consultation_result["financial_health_assessment"] = self._assess_financial_health(
                user_profile, current_portfolio, transactions
            )
            
            # Goal-based planning
            consultation_result["goal_based_planning"] = self.advisor_agent.create_investment_plan(
                user_profile, goals
            )
            
            # Risk management plan
            consultation_result["risk_management_plan"] = self.risk_agent.create_risk_management_plan(
                user_profile, current_portfolio
            )
            
            # Tax optimization plan
            consultation_result["tax_optimization_plan"] = self.tax_agent.create_comprehensive_tax_plan(
                user_profile, transactions
            )
            
            # Integrated recommendations
            consultation_result["integrated_strategy"] = self._create_integrated_financial_strategy(
                consultation_result, user_profile
            )
            
            return consultation_result
            
        except Exception as e:
            return {"error": f"Financial planning consultation failed: {str(e)}"}
    
    def market_outlook_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive market outlook and investment themes"""
        try:
            market_analysis = {
                "request_id": request.get("request_id", f"market_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "analysis_type": "market_outlook",
                "analysis_date": datetime.now().isoformat(),
                "market_outlook": {},
                "sector_analysis": {},
                "investment_themes": {},
                "risk_factors": {}
            }
            
            time_horizon = request.get("time_horizon", "medium_term")
            sectors = request.get("sectors", ["Technology", "Banking", "Pharmaceuticals", "FMCG"])
            
            # Market outlook
            market_analysis["market_outlook"] = self.advisor_agent.provide_market_outlook(time_horizon)
            
            # Sector analysis
            for sector in sectors:
                sector_data = self.analyst_agent.sector_analysis(sector)
                market_analysis["sector_analysis"][sector] = sector_data
            
            # Investment themes and recommendations
            market_analysis["investment_recommendations"] = self._generate_market_based_recommendations(
                market_analysis["market_outlook"], market_analysis["sector_analysis"]
            )
            
            return market_analysis
            
        except Exception as e:
            return {"error": f"Market outlook analysis failed: {str(e)}"}
    
    # Integration and synthesis methods
    def _integrate_agent_recommendations(self, agent_analyses: Dict, user_profile: Dict, 
                                       request: Dict) -> Dict[str, Any]:
        """Integrate recommendations from all agents"""
        integrated = {
            "overall_recommendation": "HOLD",
            "confidence_level": "Medium",
            "key_factors": [],
            "risk_considerations": [],
            "implementation_strategy": {},
            "monitoring_plan": {}
        }
        
        # Extract key recommendations
        fundamental = agent_analyses.get("fundamental", {})
        risk = agent_analyses.get("risk", {})
        advisory = agent_analyses.get("advisory", {})
        
        # Determine overall recommendation
        fund_rec = fundamental.get("recommendation", {}).get("recommendation", "HOLD")
        risk_category = risk.get("risk_analysis", {}).get("risk_category", "Moderate Risk")
        
        # Simple integration logic
        if fund_rec in ["STRONG BUY", "BUY"] and "High Risk" not in risk_category:
            integrated["overall_recommendation"] = fund_rec
            integrated["confidence_level"] = "High"
        elif fund_rec in ["HOLD"] or "High Risk" in risk_category:
            integrated["overall_recommendation"] = "HOLD"
            integrated["confidence_level"] = "Medium"
        else:
            integrated["overall_recommendation"] = "AVOID"
            integrated["confidence_level"] = "High"
        
        # Key factors
        integrated["key_factors"] = [
            f"Fundamental analysis: {fund_rec}",
            f"Risk assessment: {risk_category}",
            "Consider user risk profile and investment horizon"
        ]
        
        return integrated
    
    def _generate_executive_summary(self, integrated_recommendations: Dict, symbol: str) -> str:
        """Generate executive summary of analysis"""
        recommendation = integrated_recommendations.get("overall_recommendation", "HOLD")
        confidence = integrated_recommendations.get("confidence_level", "Medium")
        
        summary = f"""
        Executive Summary for {symbol}:
        
        Overall Recommendation: {recommendation}
        Confidence Level: {confidence}
        
        Based on comprehensive analysis involving fundamental research, risk assessment, 
        and personalized advisory, we recommend a {recommendation.lower()} position in {symbol}.
        
        Key considerations include the company's fundamental strength, risk-return profile,
        and alignment with your investment objectives and risk tolerance.
        
        Please review the detailed analysis and consult with your financial advisor 
        before making investment decisions.
        """
        
        return summary.strip()
    
    def _generate_portfolio_optimization(self, current_analysis: Dict, user_profile: Dict, 
                                       goals: List[Dict]) -> Dict[str, Any]:
        """Generate portfolio optimization recommendations"""
        return {
            "rebalancing_required": True,
            "recommended_changes": [
                "Reduce concentration in top holdings",
                "Add international diversification",
                "Increase debt allocation for stability"
            ],
            "expected_improvement": {
                "risk_reduction": "15%",
                "return_enhancement": "2-3%",
                "tax_efficiency": "Improved"
            }
        }
    
    def _create_portfolio_implementation_plan(self, optimization: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Create implementation plan for portfolio optimization"""
        return {
            "phase_1": {
                "timeline": "Next 30 days",
                "actions": ["Review current positions", "Identify rebalancing opportunities"]
            },
            "phase_2": {
                "timeline": "Next 60 days", 
                "actions": ["Execute rebalancing trades", "Add recommended positions"]
            },
            "monitoring": {
                "frequency": "Monthly",
                "key_metrics": ["Asset allocation drift", "Performance vs benchmark"]
            }
        }
    
    def _assess_financial_health(self, user_profile: Dict, portfolio: Dict, 
                                transactions: List[Dict]) -> Dict[str, Any]:
        """Assess overall financial health"""
        return {
            "health_score": 75,
            "strengths": ["Good savings rate", "Diversified portfolio"],
            "areas_for_improvement": ["Emergency fund", "Tax optimization"],
            "overall_assessment": "Good financial health with room for optimization"
        }
    
    def _create_integrated_financial_strategy(self, consultation: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Create integrated financial strategy"""
        return {
            "strategic_priorities": [
                "Build emergency fund",
                "Optimize tax-saving investments", 
                "Diversify portfolio",
                "Plan for long-term goals"
            ],
            "implementation_timeline": "12-18 months",
            "expected_outcomes": {
                "improved_financial_security": "High",
                "tax_savings": "₹25,000-50,000 annually",
                "goal_achievement_probability": "85%"
            }
        }
    
    def _generate_market_based_recommendations(self, market_outlook: Dict, 
                                             sector_analysis: Dict) -> List[Dict]:
        """Generate investment recommendations based on market analysis"""
        recommendations = []
        
        # Extract market sentiment
        market_assessment = market_outlook.get("market_assessment", {})
        outlook = market_assessment.get("outlook", "Neutral")
        
        if outlook == "Positive":
            recommendations.append({
                "recommendation": "Increase equity allocation",
                "rationale": "Positive market outlook supports equity investments",
                "allocation": "70-80% equity"
            })
        elif outlook == "Negative":
            recommendations.append({
                "recommendation": "Defensive positioning",
                "rationale": "Negative outlook suggests defensive approach",
                "allocation": "40-50% equity, increase cash/debt"
            })
        else:
            recommendations.append({
                "recommendation": "Balanced approach",
                "rationale": "Neutral outlook supports balanced allocation",
                "allocation": "60-65% equity"
            })
        
        return recommendations
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        return {
            "fundamental_analyst": "Active",
            "investment_advisor": "Active", 
            "risk_assessor": "Active",
            "tax_planner": "Active",
            "crew_status": "Operational"
        }
    
    def get_available_analyses(self) -> List[str]:
        """Get list of available analysis types"""
        return [
            "comprehensive_investment_analysis",
            "portfolio_optimization_analysis", 
            "financial_planning_consultation",
            "market_outlook_analysis",
            "individual_stock_analysis",
            "mutual_fund_analysis",
            "risk_profiling",
            "tax_planning"
        ]
