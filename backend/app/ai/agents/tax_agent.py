"""
Tax Planning Agent - Specialized in Indian tax planning and optimization
"""

from crewai import Agent
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import calendar

from app.ai.tools.calculation_tools import TaxCalculatorTool


class TaxPlanningAgent:
    """AI Agent specialized in comprehensive tax planning and optimization for Indian investors"""
    
    def __init__(self):
        self.tools = [
            TaxCalculatorTool()
        ]
        
        self.agent = Agent(
            role="Senior Tax Planning Specialist",
            goal="Provide comprehensive tax planning, optimization strategies, and compliance guidance for Indian investors",
            backstory="""You are a highly experienced tax planning specialist with over 20 years of 
            expertise in Indian taxation, particularly focusing on investment taxation, capital gains, 
            and tax-saving strategies. You have worked with individual investors, HNIs, and corporate 
            clients to optimize their tax liabilities while ensuring full compliance with Indian tax laws. 
            Your deep understanding of Income Tax Act, SEBI regulations, and various tax-saving instruments 
            makes you the go-to expert for investment-related tax planning. You stay updated with the 
            latest tax law changes and budget announcements to provide current and relevant advice.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    def create_comprehensive_tax_plan(self, user_profile: Dict, transactions: List[Dict], 
                                    financial_year: str = "2024-25") -> Dict[str, Any]:
        """Create comprehensive tax planning strategy"""
        try:
            tax_plan = {
                "user_id": user_profile.get("id"),
                "financial_year": financial_year,
                "plan_type": "comprehensive_tax_planning",
                "advisor": "Tax Planning Agent",
                "creation_date": datetime.now().isoformat(),
                "current_tax_position": {},
                "optimization_opportunities": {},
                "tax_saving_strategies": {},
                "compliance_requirements": {},
                "action_plan": {}
            }
            
            # Analyze current tax position
            tax_calculator = TaxCalculatorTool()
            current_position = tax_calculator._run(transactions, user_profile, financial_year)
            tax_plan["current_tax_position"] = current_position
            
            if "error" in current_position:
                return {"error": f"Tax calculation failed: {current_position['error']}"}
            
            # Identify optimization opportunities
            tax_plan["optimization_opportunities"] = self._identify_optimization_opportunities(
                current_position, user_profile, financial_year
            )
            
            # Generate tax-saving strategies
            tax_plan["tax_saving_strategies"] = self._generate_tax_saving_strategies(
                user_profile, current_position, financial_year
            )
            
            # Compliance requirements
            tax_plan["compliance_requirements"] = self._assess_compliance_requirements(
                user_profile, current_position, financial_year
            )
            
            # Create action plan
            tax_plan["action_plan"] = self._create_tax_action_plan(
                tax_plan["optimization_opportunities"], 
                tax_plan["tax_saving_strategies"],
                financial_year
            )
            
            # Tax calendar
            tax_plan["tax_calendar"] = self._create_tax_calendar(financial_year)
            
            # Projected tax savings
            tax_plan["projected_savings"] = self._calculate_projected_savings(
                tax_plan["tax_saving_strategies"], user_profile
            )
            
            return tax_plan
            
        except Exception as e:
            return {"error": f"Tax planning failed: {str(e)}"}
    
    def optimize_capital_gains(self, transactions: List[Dict], user_profile: Dict, 
                             target_date: str = None) -> Dict[str, Any]:
        """Optimize capital gains tax through strategic planning"""
        try:
            optimization = {
                "optimization_type": "capital_gains_optimization",
                "advisor": "Tax Planning Agent",
                "analysis_date": datetime.now().isoformat(),
                "target_date": target_date or self._get_financial_year_end(),
                "current_gains_position": {},
                "optimization_strategies": {},
                "recommended_actions": {},
                "tax_impact_analysis": {}
            }
            
            # Analyze current gains position
            optimization["current_gains_position"] = self._analyze_current_gains_position(transactions)
            
            # Generate optimization strategies
            optimization["optimization_strategies"] = self._generate_capital_gains_strategies(
                transactions, user_profile, target_date
            )
            
            # Recommend specific actions
            optimization["recommended_actions"] = self._recommend_capital_gains_actions(
                optimization["optimization_strategies"], transactions
            )
            
            # Calculate tax impact
            optimization["tax_impact_analysis"] = self._analyze_tax_impact(
                optimization["recommended_actions"], user_profile
            )
            
            return optimization
            
        except Exception as e:
            return {"error": f"Capital gains optimization failed: {str(e)}"}
    
    def plan_section_80c_investments(self, user_profile: Dict, current_investments: Dict = None,
                                   financial_year: str = "2024-25") -> Dict[str, Any]:
        """Plan Section 80C investments for maximum tax benefit"""
        try:
            section_80c_plan = {
                "financial_year": financial_year,
                "plan_type": "section_80c_optimization",
                "advisor": "Tax Planning Agent",
                "planning_date": datetime.now().isoformat(),
                "current_utilization": {},
                "available_options": {},
                "recommended_allocation": {},
                "implementation_strategy": {}
            }
            
            # Analyze current 80C utilization
            section_80c_plan["current_utilization"] = self._analyze_80c_utilization(
                current_investments or {}, user_profile
            )
            
            # List available 80C options
            section_80c_plan["available_options"] = self._get_80c_investment_options()
            
            # Recommend optimal allocation
            section_80c_plan["recommended_allocation"] = self._recommend_80c_allocation(
                user_profile, section_80c_plan["current_utilization"]
            )
            
            # Create implementation strategy
            section_80c_plan["implementation_strategy"] = self._create_80c_implementation_strategy(
                section_80c_plan["recommended_allocation"], user_profile
            )
            
            # Calculate tax savings
            section_80c_plan["tax_savings_analysis"] = self._calculate_80c_tax_savings(
                section_80c_plan["recommended_allocation"], user_profile
            )
            
            return section_80c_plan
            
        except Exception as e:
            return {"error": f"Section 80C planning failed: {str(e)}"}
    
    def analyze_tax_harvesting_opportunities(self, portfolio_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Analyze tax loss harvesting opportunities"""
        try:
            harvesting_analysis = {
                "portfolio_id": portfolio_data.get("id"),
                "analysis_type": "tax_loss_harvesting",
                "advisor": "Tax Planning Agent",
                "analysis_date": datetime.now().isoformat(),
                "loss_opportunities": {},
                "gain_realization_strategy": {},
                "wash_sale_considerations": {},
                "implementation_timeline": {}
            }
            
            holdings = portfolio_data.get("holdings", [])
            
            # Identify loss harvesting opportunities
            harvesting_analysis["loss_opportunities"] = self._identify_loss_opportunities(holdings)
            
            # Strategy for gain realization
            harvesting_analysis["gain_realization_strategy"] = self._plan_gain_realization(holdings)
            
            # Wash sale rule considerations
            harvesting_analysis["wash_sale_considerations"] = self._assess_wash_sale_rules(holdings)
            
            # Implementation timeline
            harvesting_analysis["implementation_timeline"] = self._create_harvesting_timeline(
                harvesting_analysis["loss_opportunities"]
            )
            
            # Tax impact calculation
            harvesting_analysis["tax_impact"] = self._calculate_harvesting_tax_impact(
                harvesting_analysis, user_profile
            )
            
            return harvesting_analysis
            
        except Exception as e:
            return {"error": f"Tax harvesting analysis failed: {str(e)}"}
    
    def provide_tax_compliance_guidance(self, user_profile: Dict, transactions: List[Dict],
                                      financial_year: str = "2024-25") -> Dict[str, Any]:
        """Provide comprehensive tax compliance guidance"""
        try:
            compliance_guidance = {
                "user_id": user_profile.get("id"),
                "financial_year": financial_year,
                "guidance_type": "tax_compliance",
                "advisor": "Tax Planning Agent",
                "guidance_date": datetime.now().isoformat(),
                "filing_requirements": {},
                "documentation_needed": {},
                "important_deadlines": {},
                "compliance_checklist": {},
                "audit_preparedness": {}
            }
            
            # Assess filing requirements
            compliance_guidance["filing_requirements"] = self._assess_filing_requirements(
                user_profile, transactions
            )
            
            # List required documentation
            compliance_guidance["documentation_needed"] = self._list_required_documentation(
                transactions, user_profile
            )
            
            # Important deadlines
            compliance_guidance["important_deadlines"] = self._get_important_deadlines(financial_year)
            
            # Compliance checklist
            compliance_guidance["compliance_checklist"] = self._create_compliance_checklist(
                user_profile, transactions
            )
            
            # Audit preparedness
            compliance_guidance["audit_preparedness"] = self._prepare_audit_guidance(
                user_profile, transactions
            )
            
            return compliance_guidance
            
        except Exception as e:
            return {"error": f"Tax compliance guidance failed: {str(e)}"}
    
    # Helper methods for tax optimization
    def _identify_optimization_opportunities(self, current_position: Dict, user_profile: Dict, 
                                           financial_year: str) -> Dict[str, Any]:
        """Identify tax optimization opportunities"""
        opportunities = {
            "capital_gains_optimization": [],
            "section_80c_opportunities": [],
            "other_deductions": [],
            "timing_strategies": []
        }
        
        # Capital gains opportunities
        capital_gains = current_position.get("capital_gains", {})
        stcg = capital_gains.get("stcg_total", 0)
        ltcg = capital_gains.get("ltcg_total", 0)
        
        if stcg > 0:
            opportunities["capital_gains_optimization"].append(
                "Consider booking losses to offset short-term capital gains"
            )
        
        if ltcg > 100000:
            opportunities["capital_gains_optimization"].append(
                "LTCG exceeds ₹1 lakh exemption - consider tax planning"
            )
        
        # Section 80C opportunities
        section_80c = current_position.get("section_80c", {})
        remaining_limit = section_80c.get("remaining_limit", 150000)
        
        if remaining_limit > 0:
            opportunities["section_80c_opportunities"].append(
                f"₹{remaining_limit:,.0f} remaining in Section 80C limit"
            )
        
        # Other deductions
        annual_income = user_profile.get("annual_income", 0)
        if annual_income > 250000:
            opportunities["other_deductions"].extend([
                "Consider Section 80D for health insurance premium",
                "Explore Section 80E for education loan interest",
                "Look into Section 80G for charitable donations"
            ])
        
        # Timing strategies
        current_month = datetime.now().month
        if current_month >= 10:  # October onwards
            opportunities["timing_strategies"].append(
                "Consider year-end tax planning strategies"
            )
        
        return opportunities
    
    def _generate_tax_saving_strategies(self, user_profile: Dict, current_position: Dict, 
                                      financial_year: str) -> Dict[str, Any]:
        """Generate comprehensive tax-saving strategies"""
        strategies = {
            "immediate_actions": [],
            "medium_term_strategies": [],
            "long_term_planning": [],
            "investment_strategies": []
        }
        
        annual_income = user_profile.get("annual_income", 0)
        tax_bracket = self._determine_tax_bracket(annual_income)
        
        # Immediate actions (current FY)
        strategies["immediate_actions"] = [
            "Maximize Section 80C investments before March 31",
            "Consider additional health insurance for Section 80D",
            "Plan capital gains realization strategically"
        ]
        
        # Medium-term strategies (1-3 years)
        strategies["medium_term_strategies"] = [
            "Build tax-efficient investment portfolio",
            "Consider ELSS funds for dual benefit",
            "Plan major purchases for tax benefits"
        ]
        
        # Long-term planning (3+ years)
        strategies["long_term_planning"] = [
            "Optimize retirement planning for tax efficiency",
            "Consider NPS for additional tax benefits",
            "Plan estate and succession for tax efficiency"
        ]
        
        # Investment strategies
        if tax_bracket >= 20:
            strategies["investment_strategies"].extend([
                "Prefer tax-free bonds over taxable fixed deposits",
                "Consider equity investments for LTCG tax advantage",
                "Use debt mutual funds for tax-efficient fixed income"
            ])
        
        return strategies
    
    def _assess_compliance_requirements(self, user_profile: Dict, current_position: Dict, 
                                      financial_year: str) -> Dict[str, Any]:
        """Assess tax compliance requirements"""
        annual_income = user_profile.get("annual_income", 0)
        capital_gains = current_position.get("capital_gains", {})
        
        requirements = {
            "itr_form_required": self._determine_itr_form(user_profile, current_position),
            "advance_tax_applicable": annual_income > 1000000,
            "audit_requirements": self._check_audit_requirements(user_profile, current_position),
            "tds_considerations": self._assess_tds_requirements(user_profile),
            "foreign_asset_reporting": self._check_foreign_asset_reporting(user_profile)
        }
        
        return requirements
    
    def _create_tax_action_plan(self, opportunities: Dict, strategies: Dict, 
                              financial_year: str) -> Dict[str, Any]:
        """Create actionable tax planning timeline"""
        current_date = datetime.now()
        fy_end = datetime(int(financial_year.split('-')[1]) + 2000, 3, 31)
        days_remaining = (fy_end - current_date).days
        
        action_plan = {
            "immediate_actions": {
                "timeline": "Next 30 days",
                "actions": []
            },
            "quarter_end_actions": {
                "timeline": "By December 31",
                "actions": []
            },
            "year_end_actions": {
                "timeline": "By March 31",
                "actions": []
            }
        }
        
        # Populate actions based on remaining time
        if days_remaining > 90:
            action_plan["immediate_actions"]["actions"] = [
                "Review current tax position",
                "Plan Section 80C investments",
                "Consider tax loss harvesting"
            ]
        else:
            action_plan["immediate_actions"]["actions"] = [
                "Urgent: Complete pending tax-saving investments",
                "Finalize capital gains strategy",
                "Prepare for tax filing"
            ]
        
        return action_plan
    
    def _create_tax_calendar(self, financial_year: str) -> Dict[str, List[str]]:
        """Create tax calendar with important dates"""
        fy_start_year = int(financial_year.split('-')[0])
        fy_end_year = fy_start_year + 1
        
        tax_calendar = {
            "April": [
                "New financial year begins",
                "Plan annual tax strategy"
            ],
            "June": [
                "First advance tax installment due (15th)",
                "File previous year ITR if not done"
            ],
            "September": [
                "Second advance tax installment due (15th)"
            ],
            "December": [
                "Third advance tax installment due (15th)",
                "Review tax-saving investments"
            ],
            "March": [
                "Fourth advance tax installment due (15th)",
                "Last date for tax-saving investments (31st)",
                "Financial year ends (31st)"
            ],
            "July": [
                "ITR filing due date (31st) for most taxpayers"
            ]
        }
        
        return tax_calendar
    
    def _calculate_projected_savings(self, strategies: Dict, user_profile: Dict) -> Dict[str, float]:
        """Calculate projected tax savings from strategies"""
        annual_income = user_profile.get("annual_income", 0)
        tax_rate = self._determine_tax_bracket(annual_income) / 100
        
        projected_savings = {
            "section_80c_savings": 150000 * tax_rate,  # Maximum 80C benefit
            "section_80d_savings": 25000 * tax_rate,   # Health insurance
            "capital_gains_optimization": 10000,        # Estimated from loss harvesting
            "total_projected_savings": 0
        }
        
        projected_savings["total_projected_savings"] = sum(projected_savings.values()) - projected_savings["total_projected_savings"]
        
        return projected_savings
    
    # Helper methods for capital gains optimization
    def _analyze_current_gains_position(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze current capital gains position"""
        stcg_total = 0
        ltcg_total = 0
        unrealized_gains = 0
        unrealized_losses = 0
        
        # This would analyze transactions to calculate gains/losses
        # Simplified for now
        
        return {
            "realized_stcg": stcg_total,
            "realized_ltcg": ltcg_total,
            "unrealized_gains": unrealized_gains,
            "unrealized_losses": unrealized_losses,
            "net_position": stcg_total + ltcg_total
        }
    
    def _generate_capital_gains_strategies(self, transactions: List[Dict], user_profile: Dict, 
                                         target_date: str) -> List[Dict]:
        """Generate capital gains optimization strategies"""
        strategies = [
            {
                "strategy": "Loss Harvesting",
                "description": "Book losses to offset capital gains",
                "potential_benefit": "Reduce taxable capital gains",
                "implementation": "Sell loss-making investments before year-end"
            },
            {
                "strategy": "Gain Realization",
                "description": "Realize LTCG up to ₹1 lakh exemption",
                "potential_benefit": "Tax-free capital gains",
                "implementation": "Sell profitable long-term investments"
            },
            {
                "strategy": "Timing Optimization",
                "description": "Time sales to optimize between STCG and LTCG",
                "potential_benefit": "Lower tax rate on gains",
                "implementation": "Hold investments for >1 year when possible"
            }
        ]
        
        return strategies
    
    # Helper methods for Section 80C planning
    def _analyze_80c_utilization(self, current_investments: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Analyze current Section 80C utilization"""
        total_invested = sum(current_investments.values())
        max_limit = 150000
        remaining = max(0, max_limit - total_invested)
        
        return {
            "total_invested": total_invested,
            "max_limit": max_limit,
            "remaining_limit": remaining,
            "utilization_percentage": (total_invested / max_limit) * 100,
            "current_investments": current_investments
        }
    
    def _get_80c_investment_options(self) -> Dict[str, Dict]:
        """Get available Section 80C investment options"""
        return {
            "ELSS": {
                "description": "Equity Linked Savings Scheme",
                "lock_in": "3 years",
                "expected_return": "10-15%",
                "risk": "High",
                "liquidity": "Low"
            },
            "PPF": {
                "description": "Public Provident Fund",
                "lock_in": "15 years",
                "expected_return": "7-8%",
                "risk": "Low",
                "liquidity": "Very Low"
            },
            "NSC": {
                "description": "National Savings Certificate",
                "lock_in": "5 years",
                "expected_return": "6-7%",
                "risk": "Low",
                "liquidity": "Low"
            },
            "Tax Saver FD": {
                "description": "Tax Saving Fixed Deposit",
                "lock_in": "5 years",
                "expected_return": "5-6%",
                "risk": "Very Low",
                "liquidity": "Very Low"
            }
        }
    
    def _recommend_80c_allocation(self, user_profile: Dict, current_utilization: Dict) -> Dict[str, float]:
        """Recommend optimal Section 80C allocation"""
        remaining_amount = current_utilization.get("remaining_limit", 150000)
        risk_profile = user_profile.get("risk_profile", "moderate")
        age = user_profile.get("age", 35)
        
        if risk_profile in ["aggressive", "very_aggressive"] and age < 40:
            # Aggressive allocation
            allocation = {
                "ELSS": remaining_amount * 0.7,
                "PPF": remaining_amount * 0.3
            }
        elif risk_profile == "moderate":
            # Balanced allocation
            allocation = {
                "ELSS": remaining_amount * 0.5,
                "PPF": remaining_amount * 0.3,
                "NSC": remaining_amount * 0.2
            }
        else:
            # Conservative allocation
            allocation = {
                "PPF": remaining_amount * 0.5,
                "NSC": remaining_amount * 0.3,
                "Tax Saver FD": remaining_amount * 0.2
            }
        
        return allocation
    
    # Utility methods
    def _determine_tax_bracket(self, annual_income: float) -> float:
        """Determine tax bracket based on income"""
        if annual_income <= 250000:
            return 0
        elif annual_income <= 500000:
            return 5
        elif annual_income <= 750000:
            return 10
        elif annual_income <= 1000000:
            return 15
        elif annual_income <= 1250000:
            return 20
        elif annual_income <= 1500000:
            return 25
        else:
            return 30
    
    def _get_financial_year_end(self) -> str:
        """Get current financial year end date"""
        current_date = datetime.now()
        if current_date.month >= 4:
            fy_end = f"{current_date.year + 1}-03-31"
        else:
            fy_end = f"{current_date.year}-03-31"
        return fy_end
    
    def _determine_itr_form(self, user_profile: Dict, current_position: Dict) -> str:
        """Determine appropriate ITR form"""
        annual_income = user_profile.get("annual_income", 0)
        has_capital_gains = current_position.get("capital_gains", {}).get("net_capital_gains", 0) != 0
        
        if has_capital_gains or annual_income > 5000000:
            return "ITR-2"
        else:
            return "ITR-1"
    
    def _check_audit_requirements(self, user_profile: Dict, current_position: Dict) -> bool:
        """Check if audit is required"""
        # Simplified - actual requirements are more complex
        return user_profile.get("annual_income", 0) > 10000000
    
    def _assess_tds_requirements(self, user_profile: Dict) -> Dict[str, Any]:
        """Assess TDS requirements and considerations"""
        return {
            "salary_tds": "Applicable if salaried",
            "investment_tds": "May apply on interest/dividends",
            "tds_refund_expected": "Check if excess TDS deducted"
        }
    
    def _check_foreign_asset_reporting(self, user_profile: Dict) -> bool:
        """Check if foreign asset reporting is required"""
        # This would check for foreign investments/assets
        return False  # Simplified
    
    # Placeholder methods for remaining functionality
    def _identify_loss_opportunities(self, holdings: List[Dict]) -> Dict[str, Any]:
        return {"potential_losses": 50000, "holdings_to_sell": ["STOCK1"]}
    
    def _plan_gain_realization(self, holdings: List[Dict]) -> Dict[str, Any]:
        return {"ltcg_to_realize": 100000, "holdings_to_sell": ["STOCK2"]}
    
    def _assess_wash_sale_rules(self, holdings: List[Dict]) -> Dict[str, Any]:
        return {"wash_sale_risk": "Low", "recommendations": ["Wait 30 days before repurchasing"]}
    
    def _create_harvesting_timeline(self, opportunities: Dict) -> Dict[str, str]:
        return {"optimal_timing": "Before March 31", "execution_window": "January-March"}
    
    def _calculate_harvesting_tax_impact(self, analysis: Dict, user_profile: Dict) -> Dict[str, float]:
        return {"tax_savings": 15000, "net_benefit": 12000}
