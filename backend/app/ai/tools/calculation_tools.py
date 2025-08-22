"""
Financial calculation tools for AI agents
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from crewai_tools import BaseTool
import math


class PortfolioCalculatorTool(BaseTool):
    """Tool for portfolio calculations and optimization"""
    
    name: str = "Portfolio Calculator Tool"
    description: str = "Performs portfolio calculations including returns, risk metrics, asset allocation, and rebalancing recommendations"
    
    def _run(self, holdings: List[Dict], user_profile: Dict = None) -> Dict[str, Any]:
        """Calculate comprehensive portfolio metrics"""
        try:
            if not holdings:
                return {"error": "No holdings provided"}
            
            # Calculate basic portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(holdings)
            
            # Calculate asset allocation
            asset_allocation = self._calculate_asset_allocation(holdings)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_portfolio_risk(holdings)
            
            # Generate rebalancing recommendations
            rebalancing = self._generate_rebalancing_recommendations(holdings, user_profile)
            
            # Calculate performance attribution
            performance = self._calculate_performance_attribution(holdings)
            
            result = {
                "calculation_type": "portfolio_analysis",
                "calculation_date": datetime.now().isoformat(),
                "portfolio_metrics": portfolio_metrics,
                "asset_allocation": asset_allocation,
                "risk_metrics": risk_metrics,
                "rebalancing": rebalancing,
                "performance": performance,
                "recommendations": self._generate_portfolio_recommendations(portfolio_metrics, risk_metrics, user_profile)
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Portfolio calculation failed: {str(e)}"}
    
    def _calculate_portfolio_metrics(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Calculate basic portfolio metrics"""
        total_invested = sum(holding.get('invested_amount', 0) for holding in holdings)
        total_current = sum(holding.get('current_value', 0) for holding in holdings)
        
        total_returns = total_current - total_invested
        returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0
        
        # Calculate weighted returns
        weighted_returns = []
        for holding in holdings:
            weight = holding.get('current_value', 0) / total_current if total_current > 0 else 0
            holding_return = holding.get('unrealized_pnl_percentage', 0)
            weighted_returns.append(weight * holding_return)
        
        portfolio_return = sum(weighted_returns)
        
        return {
            "total_invested": total_invested,
            "current_value": total_current,
            "total_returns": total_returns,
            "returns_percentage": returns_percentage,
            "portfolio_return": portfolio_return,
            "number_of_holdings": len(holdings),
            "largest_holding_weight": max((h.get('current_value', 0) / total_current * 100) for h in holdings) if total_current > 0 else 0,
            "concentration_risk": self._calculate_concentration_risk(holdings, total_current)
        }
    
    def _calculate_asset_allocation(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Calculate asset allocation breakdown"""
        total_value = sum(holding.get('current_value', 0) for holding in holdings)
        
        if total_value == 0:
            return {"error": "No portfolio value"}
        
        allocation = {}
        sector_allocation = {}
        
        for holding in holdings:
            asset_type = holding.get('asset_type', 'other')
            sector = holding.get('sector', 'Unknown')
            value = holding.get('current_value', 0)
            percentage = (value / total_value) * 100
            
            # Asset type allocation
            if asset_type in allocation:
                allocation[asset_type] += percentage
            else:
                allocation[asset_type] = percentage
            
            # Sector allocation
            if sector in sector_allocation:
                sector_allocation[sector] += percentage
            else:
                sector_allocation[sector] = percentage
        
        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(allocation)
        
        return {
            "asset_allocation": allocation,
            "sector_allocation": sector_allocation,
            "diversification_score": diversification_score,
            "allocation_analysis": self._analyze_allocation(allocation)
        }
    
    def _calculate_portfolio_risk(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        total_value = sum(holding.get('current_value', 0) for holding in holdings)
        
        if total_value == 0:
            return {"error": "No portfolio value"}
        
        # Calculate weighted beta
        weighted_beta = 0
        weighted_volatility = 0
        
        for holding in holdings:
            weight = holding.get('current_value', 0) / total_value
            beta = holding.get('beta', 1.0)
            volatility = holding.get('volatility', 0.2)
            
            weighted_beta += weight * beta
            weighted_volatility += weight * volatility
        
        # Estimate portfolio volatility (simplified)
        portfolio_volatility = weighted_volatility * 0.8  # Assuming some diversification benefit
        
        # Calculate VaR (simplified)
        daily_var_95 = portfolio_volatility / math.sqrt(252) * 1.645  # 95% confidence
        portfolio_var_95 = total_value * daily_var_95
        
        return {
            "portfolio_beta": weighted_beta,
            "portfolio_volatility": portfolio_volatility,
            "value_at_risk_95": portfolio_var_95,
            "risk_score": self._calculate_portfolio_risk_score(weighted_beta, portfolio_volatility),
            "risk_category": self._categorize_portfolio_risk(portfolio_volatility)
        }
    
    def _generate_rebalancing_recommendations(self, holdings: List[Dict], user_profile: Dict = None) -> Dict[str, Any]:
        """Generate rebalancing recommendations"""
        if not user_profile:
            return {"message": "User profile required for rebalancing recommendations"}
        
        risk_profile = user_profile.get('risk_profile', 'moderate')
        target_allocation = self._get_target_allocation(risk_profile)
        
        current_allocation = {}
        total_value = sum(holding.get('current_value', 0) for holding in holdings)
        
        for holding in holdings:
            asset_type = holding.get('asset_type', 'other')
            value = holding.get('current_value', 0)
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            
            if asset_type in current_allocation:
                current_allocation[asset_type] += percentage
            else:
                current_allocation[asset_type] = percentage
        
        # Calculate deviations
        rebalancing_needed = False
        recommendations = []
        
        for asset_type, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_type, 0)
            deviation = current_pct - target_pct
            
            if abs(deviation) > 5:  # 5% threshold
                rebalancing_needed = True
                if deviation > 0:
                    recommendations.append(f"Reduce {asset_type} allocation by {deviation:.1f}%")
                else:
                    recommendations.append(f"Increase {asset_type} allocation by {abs(deviation):.1f}%")
        
        return {
            "rebalancing_needed": rebalancing_needed,
            "target_allocation": target_allocation,
            "current_allocation": current_allocation,
            "recommendations": recommendations,
            "rebalancing_urgency": "High" if any(abs(current_allocation.get(k, 0) - v) > 10 for k, v in target_allocation.items()) else "Low"
        }
    
    def _calculate_performance_attribution(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Calculate performance attribution"""
        total_returns = sum(holding.get('unrealized_pnl', 0) for holding in holdings)
        
        # Attribution by asset type
        asset_attribution = {}
        sector_attribution = {}
        
        for holding in holdings:
            asset_type = holding.get('asset_type', 'other')
            sector = holding.get('sector', 'Unknown')
            returns = holding.get('unrealized_pnl', 0)
            
            if asset_type in asset_attribution:
                asset_attribution[asset_type] += returns
            else:
                asset_attribution[asset_type] = returns
            
            if sector in sector_attribution:
                sector_attribution[sector] += returns
            else:
                sector_attribution[sector] = returns
        
        # Find top contributors
        top_contributors = sorted(holdings, key=lambda x: x.get('unrealized_pnl', 0), reverse=True)[:5]
        worst_performers = sorted(holdings, key=lambda x: x.get('unrealized_pnl', 0))[:5]
        
        return {
            "total_returns": total_returns,
            "asset_attribution": asset_attribution,
            "sector_attribution": sector_attribution,
            "top_contributors": [{"symbol": h.get('symbol'), "returns": h.get('unrealized_pnl', 0)} for h in top_contributors],
            "worst_performers": [{"symbol": h.get('symbol'), "returns": h.get('unrealized_pnl', 0)} for h in worst_performers]
        }
    
    def _generate_portfolio_recommendations(self, metrics: Dict, risk_metrics: Dict, user_profile: Dict = None) -> List[str]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        # Concentration risk
        if metrics.get('concentration_risk', 0) > 30:
            recommendations.append("Consider diversifying - portfolio is highly concentrated")
        
        # Risk level
        risk_score = risk_metrics.get('risk_score', 50)
        if user_profile and user_profile.get('risk_profile') == 'conservative' and risk_score > 60:
            recommendations.append("Portfolio risk is higher than your risk profile - consider reducing exposure to volatile assets")
        
        # Returns
        if metrics.get('returns_percentage', 0) < 0:
            recommendations.append("Portfolio is underperforming - review individual holdings and consider rebalancing")
        
        # Number of holdings
        if metrics.get('number_of_holdings', 0) < 5:
            recommendations.append("Consider adding more holdings for better diversification")
        elif metrics.get('number_of_holdings', 0) > 30:
            recommendations.append("Portfolio may be over-diversified - consider consolidating positions")
        
        return recommendations
    
    # Helper methods
    def _calculate_concentration_risk(self, holdings: List[Dict], total_value: float) -> float:
        """Calculate concentration risk (Herfindahl index)"""
        if total_value == 0:
            return 0
        
        weights = [(holding.get('current_value', 0) / total_value) for holding in holdings]
        hhi = sum(w**2 for w in weights) * 100
        return hhi
    
    def _calculate_diversification_score(self, allocation: Dict) -> float:
        """Calculate diversification score (0-100)"""
        if not allocation:
            return 0
        
        # Higher score for more even distribution
        values = list(allocation.values())
        ideal_weight = 100 / len(values)
        deviations = [abs(v - ideal_weight) for v in values]
        avg_deviation = sum(deviations) / len(deviations)
        
        return max(0, 100 - avg_deviation * 2)
    
    def _analyze_allocation(self, allocation: Dict) -> str:
        """Analyze asset allocation"""
        equity_pct = allocation.get('stock', 0) + allocation.get('etf', 0)
        debt_pct = allocation.get('bond', 0) + allocation.get('cash', 0)
        
        if equity_pct > 80:
            return "Aggressive allocation with high equity exposure"
        elif equity_pct > 60:
            return "Moderate to aggressive allocation"
        elif equity_pct > 40:
            return "Balanced allocation"
        else:
            return "Conservative allocation with low equity exposure"
    
    def _calculate_portfolio_risk_score(self, beta: float, volatility: float) -> float:
        """Calculate portfolio risk score"""
        beta_score = abs(beta - 1) * 30
        vol_score = volatility * 100
        return min(100, beta_score + vol_score)
    
    def _categorize_portfolio_risk(self, volatility: float) -> str:
        """Categorize portfolio risk"""
        if volatility < 0.15:
            return "Low Risk"
        elif volatility < 0.25:
            return "Moderate Risk"
        elif volatility < 0.35:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _get_target_allocation(self, risk_profile: str) -> Dict[str, float]:
        """Get target allocation based on risk profile"""
        allocations = {
            'conservative': {'stock': 30, 'bond': 50, 'cash': 20},
            'moderate': {'stock': 60, 'bond': 30, 'cash': 10},
            'aggressive': {'stock': 80, 'bond': 15, 'cash': 5},
            'very_aggressive': {'stock': 90, 'bond': 8, 'cash': 2}
        }
        return allocations.get(risk_profile, allocations['moderate'])


class TaxCalculatorTool(BaseTool):
    """Tool for tax calculations specific to Indian tax laws"""
    
    name: str = "Tax Calculator Tool"
    description: str = "Calculates taxes on investments including capital gains, dividend tax, and provides tax optimization suggestions for Indian investors"
    
    def _run(self, transactions: List[Dict], user_profile: Dict, financial_year: str = "2024-25") -> Dict[str, Any]:
        """Calculate comprehensive tax implications"""
        try:
            # Calculate capital gains
            capital_gains = self._calculate_capital_gains(transactions)
            
            # Calculate dividend tax
            dividend_tax = self._calculate_dividend_tax(transactions, user_profile)
            
            # Calculate tax liability
            tax_liability = self._calculate_tax_liability(capital_gains, dividend_tax, user_profile, financial_year)
            
            # Generate tax optimization suggestions
            optimization = self._generate_tax_optimization(capital_gains, user_profile, financial_year)
            
            # Calculate Section 80C utilization
            section_80c = self._calculate_section_80c_utilization(transactions, user_profile)
            
            result = {
                "calculation_type": "tax_analysis",
                "financial_year": financial_year,
                "calculation_date": datetime.now().isoformat(),
                "capital_gains": capital_gains,
                "dividend_tax": dividend_tax,
                "tax_liability": tax_liability,
                "section_80c": section_80c,
                "optimization": optimization,
                "tax_summary": self._generate_tax_summary(capital_gains, dividend_tax, tax_liability)
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Tax calculation failed: {str(e)}"}
    
    def _calculate_capital_gains(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Calculate capital gains (STCG and LTCG)"""
        stcg = 0  # Short-term capital gains
        ltcg = 0  # Long-term capital gains
        stcg_details = []
        ltcg_details = []
        
        # Group transactions by symbol
        holdings = {}
        for txn in transactions:
            symbol = txn.get('symbol')
            if symbol not in holdings:
                holdings[symbol] = []
            holdings[symbol].append(txn)
        
        # Calculate gains for each holding
        for symbol, txns in holdings.items():
            # Sort by date
            txns.sort(key=lambda x: x.get('transaction_date', ''))
            
            # FIFO method for calculating gains
            buy_queue = []
            
            for txn in txns:
                if txn.get('transaction_type') == 'buy':
                    buy_queue.append(txn)
                elif txn.get('transaction_type') == 'sell':
                    sell_qty = txn.get('quantity', 0)
                    sell_price = txn.get('price', 0)
                    sell_date = datetime.fromisoformat(txn.get('transaction_date', ''))
                    
                    while sell_qty > 0 and buy_queue:
                        buy_txn = buy_queue[0]
                        buy_qty = buy_txn.get('quantity', 0)
                        buy_price = buy_txn.get('price', 0)
                        buy_date = datetime.fromisoformat(buy_txn.get('transaction_date', ''))
                        
                        # Determine quantity to sell from this buy lot
                        qty_to_sell = min(sell_qty, buy_qty)
                        
                        # Calculate gain/loss
                        gain = (sell_price - buy_price) * qty_to_sell
                        
                        # Determine if STCG or LTCG
                        holding_period = (sell_date - buy_date).days
                        
                        if holding_period <= 365:  # STCG
                            stcg += gain
                            stcg_details.append({
                                'symbol': symbol,
                                'quantity': qty_to_sell,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'gain': gain,
                                'holding_period': holding_period
                            })
                        else:  # LTCG
                            ltcg += gain
                            ltcg_details.append({
                                'symbol': symbol,
                                'quantity': qty_to_sell,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'gain': gain,
                                'holding_period': holding_period
                            })
                        
                        # Update quantities
                        sell_qty -= qty_to_sell
                        buy_txn['quantity'] = buy_qty - qty_to_sell
                        
                        if buy_txn['quantity'] <= 0:
                            buy_queue.pop(0)
        
        return {
            "stcg_total": stcg,
            "ltcg_total": ltcg,
            "stcg_details": stcg_details,
            "ltcg_details": ltcg_details,
            "net_capital_gains": stcg + ltcg
        }
    
    def _calculate_dividend_tax(self, transactions: List[Dict], user_profile: Dict) -> Dict[str, Any]:
        """Calculate dividend tax"""
        total_dividends = sum(txn.get('total_amount', 0) for txn in transactions if txn.get('transaction_type') == 'dividend')
        
        # Dividend tax rate based on income slab
        annual_income = user_profile.get('annual_income', 0)
        tax_rate = self._get_dividend_tax_rate(annual_income)
        
        dividend_tax = total_dividends * tax_rate / 100
        
        return {
            "total_dividends": total_dividends,
            "tax_rate": tax_rate,
            "dividend_tax": dividend_tax
        }
    
    def _calculate_tax_liability(self, capital_gains: Dict, dividend_tax: Dict, user_profile: Dict, financial_year: str) -> Dict[str, Any]:
        """Calculate total tax liability"""
        # STCG tax (15% for equity, as per income slab for others)
        stcg = capital_gains.get('stcg_total', 0)
        stcg_tax = max(0, stcg * 0.15)  # 15% for equity STCG
        
        # LTCG tax (10% above 1 lakh for equity)
        ltcg = capital_gains.get('ltcg_total', 0)
        ltcg_exempt = 100000  # 1 lakh exemption
        ltcg_taxable = max(0, ltcg - ltcg_exempt)
        ltcg_tax = ltcg_taxable * 0.10  # 10% for equity LTCG
        
        # Dividend tax
        div_tax = dividend_tax.get('dividend_tax', 0)
        
        total_tax = stcg_tax + ltcg_tax + div_tax
        
        return {
            "stcg_tax": stcg_tax,
            "ltcg_tax": ltcg_tax,
            "ltcg_exempt_amount": min(ltcg, ltcg_exempt),
            "dividend_tax": div_tax,
            "total_investment_tax": total_tax,
            "effective_tax_rate": (total_tax / (stcg + ltcg + dividend_tax.get('total_dividends', 0))) * 100 if (stcg + ltcg + dividend_tax.get('total_dividends', 0)) > 0 else 0
        }
    
    def _calculate_section_80c_utilization(self, transactions: List[Dict], user_profile: Dict) -> Dict[str, Any]:
        """Calculate Section 80C utilization"""
        # ELSS investments
        elss_investments = sum(txn.get('total_amount', 0) for txn in transactions 
                              if txn.get('transaction_type') == 'buy' and 
                              txn.get('category') == 'ELSS')
        
        # Other 80C investments (would come from user profile)
        other_80c = user_profile.get('other_80c_investments', 0)
        
        total_80c = elss_investments + other_80c
        max_limit = 150000  # 1.5 lakh limit
        
        utilized = min(total_80c, max_limit)
        remaining = max_limit - utilized
        tax_saved = utilized * (user_profile.get('tax_bracket', 30) / 100)
        
        return {
            "elss_investments": elss_investments,
            "other_80c_investments": other_80c,
            "total_80c_investments": total_80c,
            "utilized_amount": utilized,
            "remaining_limit": remaining,
            "tax_saved": tax_saved,
            "utilization_percentage": (utilized / max_limit) * 100
        }
    
    def _generate_tax_optimization(self, capital_gains: Dict, user_profile: Dict, financial_year: str) -> Dict[str, Any]:
        """Generate tax optimization suggestions"""
        suggestions = []
        
        # LTCG optimization
        ltcg = capital_gains.get('ltcg_total', 0)
        if ltcg > 100000:
            suggestions.append("Consider harvesting LTCG up to ₹1 lakh exemption limit")
        
        # Loss harvesting
        stcg = capital_gains.get('stcg_total', 0)
        if stcg > 0:
            suggestions.append("Consider booking losses to offset short-term capital gains")
        
        # Section 80C
        annual_income = user_profile.get('annual_income', 0)
        if annual_income > 250000:
            suggestions.append("Maximize Section 80C investments to save up to ₹46,800 in taxes")
        
        # ELSS vs other options
        suggestions.append("Consider ELSS mutual funds for dual benefit of tax saving and equity exposure")
        
        # Timing of transactions
        suggestions.append("Plan sale transactions to optimize between STCG and LTCG rates")
        
        return {
            "optimization_suggestions": suggestions,
            "potential_tax_savings": self._calculate_potential_savings(capital_gains, user_profile),
            "recommended_actions": self._get_recommended_actions(capital_gains, user_profile)
        }
    
    def _generate_tax_summary(self, capital_gains: Dict, dividend_tax: Dict, tax_liability: Dict) -> str:
        """Generate tax summary"""
        total_gains = capital_gains.get('net_capital_gains', 0)
        total_tax = tax_liability.get('total_investment_tax', 0)
        
        return f"Total capital gains: ₹{total_gains:,.2f}, Total tax liability: ₹{total_tax:,.2f}, " \
               f"Effective tax rate: {tax_liability.get('effective_tax_rate', 0):.2f}%"
    
    # Helper methods
    def _get_dividend_tax_rate(self, annual_income: float) -> float:
        """Get dividend tax rate based on income"""
        if annual_income <= 250000:
            return 0
        elif annual_income <= 500000:
            return 5
        elif annual_income <= 1000000:
            return 20
        else:
            return 30
    
    def _calculate_potential_savings(self, capital_gains: Dict, user_profile: Dict) -> float:
        """Calculate potential tax savings"""
        # Simplified calculation
        return 25000  # Placeholder
    
    def _get_recommended_actions(self, capital_gains: Dict, user_profile: Dict) -> List[str]:
        """Get recommended tax actions"""
        return [
            "Review portfolio for tax loss harvesting opportunities",
            "Consider timing of future transactions",
            "Maximize tax-saving investments"
        ]


class GoalCalculatorTool(BaseTool):
    """Tool for financial goal calculations"""
    
    name: str = "Goal Calculator Tool"
    description: str = "Calculates financial goals including SIP amounts, target corpus, retirement planning, and goal tracking"
    
    def _run(self, goal_data: Dict, user_profile: Dict = None) -> Dict[str, Any]:
        """Calculate financial goal requirements"""
        try:
            goal_type = goal_data.get('goal_type', 'retirement')
            
            if goal_type == 'retirement':
                return self._calculate_retirement_goal(goal_data, user_profile)
            elif goal_type == 'education':
                return self._calculate_education_goal(goal_data, user_profile)
            elif goal_type == 'home_purchase':
                return self._calculate_home_goal(goal_data, user_profile)
            elif goal_type == 'emergency_fund':
                return self._calculate_emergency_fund(goal_data, user_profile)
            else:
                return self._calculate_generic_goal(goal_data, user_profile)
                
        except Exception as e:
            return {"error": f"Goal calculation failed: {str(e)}"}
    
    def _calculate_retirement_goal(self, goal_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Calculate retirement planning requirements"""
        current_age = user_profile.get('age', 30)
        retirement_age = goal_data.get('retirement_age', 60)
        current_monthly_expenses = user_profile.get('monthly_expenses', 50000)
        inflation_rate = goal_data.get('inflation_rate', 6) / 100
        expected_return = goal_data.get('expected_return', 12) / 100
        life_expectancy = goal_data.get('life_expectancy', 80)
        
        years_to_retirement = retirement_age - current_age
        retirement_years = life_expectancy - retirement_age
        
        # Calculate future monthly expenses at retirement
        future_monthly_expenses = current_monthly_expenses * ((1 + inflation_rate) ** years_to_retirement)
        
        # Calculate corpus required at retirement (considering inflation during retirement)
        annual_expenses_at_retirement = future_monthly_expenses * 12
        
        # Present value of annuity for retirement years
        real_return_during_retirement = (expected_return - inflation_rate) / (1 + inflation_rate)
        if real_return_during_retirement > 0:
            corpus_required = annual_expenses_at_retirement * (1 - (1 + real_return_during_retirement) ** (-retirement_years)) / real_return_during_retirement
        else:
            corpus_required = annual_expenses_at_retirement * retirement_years
        
        # Calculate monthly SIP required
        monthly_return = expected_return / 12
        months_to_retirement = years_to_retirement * 12
        
        if monthly_return > 0:
            sip_required = corpus_required * monthly_return / (((1 + monthly_return) ** months_to_retirement) - 1)
        else:
            sip_required = corpus_required / months_to_retirement
        
        return {
            "goal_type": "retirement",
            "calculation_date": datetime.now().isoformat(),
            "inputs": {
                "current_age": current_age,
                "retirement_age": retirement_age,
                "current_monthly_expenses": current_monthly_expenses,
                "inflation_rate": inflation_rate * 100,
                "expected_return": expected_return * 100,
                "years_to_retirement": years_to_retirement
            },
            "results": {
                "corpus_required": corpus_required,
                "future_monthly_expenses": future_monthly_expenses,
                "monthly_sip_required": sip_required,
                "total_investment": sip_required * months_to_retirement,
                "wealth_multiplier": corpus_required / (sip_required * months_to_retirement) if sip_required > 0 else 0
            },
            "milestones": self._create_retirement_milestones(corpus_required, years_to_retirement),
            "recommendations": self._get_retirement_recommendations(sip_required, user_profile)
        }
    
    def _calculate_education_goal(self, goal_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Calculate education goal requirements"""
        current_cost = goal_data.get('current_cost', 500000)
        years_to_goal = goal_data.get('years_to_goal', 15)
        education_inflation = goal_data.get('education_inflation', 8) / 100
        expected_return = goal_data.get('expected_return', 12) / 100
        
        # Calculate future cost
        future_cost = current_cost * ((1 + education_inflation) ** years_to_goal)
        
        # Calculate monthly SIP required
        monthly_return = expected_return / 12
        months_to_goal = years_to_goal * 12
        
        if monthly_return > 0:
            sip_required = future_cost * monthly_return / (((1 + monthly_return) ** months_to_goal) - 1)
        else:
            sip_required = future_cost / months_to_goal
        
        return {
            "goal_type": "education",
            "calculation_date": datetime.now().isoformat(),
            "inputs": {
                "current_cost": current_cost,
                "years_to_goal": years_to_goal,
                "education_inflation": education_inflation * 100,
                "expected_return": expected_return * 100
            },
            "results": {
                "future_cost": future_cost,
                "monthly_sip_required": sip_required,
                "total_investment": sip_required * months_to_goal,
                "cost_multiplier": future_cost / current_cost
            },
            "milestones": self._create_goal_milestones(future_cost, years_to_goal),
            "recommendations": self._get_education_recommendations(sip_required, years_to_goal)
        }
    
    def _calculate_home_goal(self, goal_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Calculate home purchase goal"""
        home_cost = goal_data.get('home_cost', 5000000)
        down_payment_pct = goal_data.get('down_payment_percentage', 20) / 100
        years_to_goal = goal_data.get('years_to_goal', 10)
        real_estate_appreciation = goal_data.get('real_estate_appreciation', 5) / 100
        expected_return = goal_data.get('expected_return', 12) / 100
        
        # Calculate future home cost
        future_home_cost = home_cost * ((1 + real_estate_appreciation) ** years_to_goal)
        down_payment_required = future_home_cost * down_payment_pct
        
        # Calculate monthly SIP required
        monthly_return = expected_return / 12
        months_to_goal = years_to_goal * 12
        
        if monthly_return > 0:
            sip_required = down_payment_required * monthly_return / (((1 + monthly_return) ** months_to_goal) - 1)
        else:
            sip_required = down_payment_required / months_to_goal
        
        # Calculate loan details
        loan_amount = future_home_cost - down_payment_required
        loan_rate = goal_data.get('loan_rate', 8.5) / 100 / 12
        loan_tenure = goal_data.get('loan_tenure', 20) * 12
        
        if loan_rate > 0:
            emi = loan_amount * loan_rate * ((1 + loan_rate) ** loan_tenure) / (((1 + loan_rate) ** loan_tenure) - 1)
        else:
            emi = loan_amount / loan_tenure
        
        return {
            "goal_type": "home_purchase",
            "calculation_date": datetime.now().isoformat(),
            "inputs": {
                "current_home_cost": home_cost,
                "down_payment_percentage": down_payment_pct * 100,
                "years_to_goal": years_to_goal,
                "real_estate_appreciation": real_estate_appreciation * 100,
                "expected_return": expected_return * 100
            },
            "results": {
                "future_home_cost": future_home_cost,
                "down_payment_required": down_payment_required,
                "monthly_sip_required": sip_required,
                "total_investment": sip_required * months_to_goal,
                "loan_amount": loan_amount,
                "monthly_emi": emi,
                "total_cost_of_ownership": down_payment_required + (emi * loan_tenure)
            },
            "milestones": self._create_goal_milestones(down_payment_required, years_to_goal),
            "recommendations": self._get_home_recommendations(sip_required, emi, user_profile)
        }
    
    def _calculate_emergency_fund(self, goal_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Calculate emergency fund requirements"""
        monthly_expenses = user_profile.get('monthly_expenses', 50000)
        months_of_expenses = goal_data.get('months_of_expenses', 6)
        time_to_build = goal_data.get('time_to_build_months', 12)
        expected_return = goal_data.get('expected_return', 6) / 100  # Conservative return for emergency fund
        
        target_amount = monthly_expenses * months_of_expenses
        monthly_investment = target_amount / time_to_build
        
        return {
            "goal_type": "emergency_fund",
            "calculation_date": datetime.now().isoformat(),
            "inputs": {
                "monthly_expenses": monthly_expenses,
                "months_of_expenses": months_of_expenses,
                "time_to_build_months": time_to_build,
                "expected_return": expected_return * 100
            },
            "results": {
                "target_amount": target_amount,
                "monthly_investment_required": monthly_investment,
                "total_investment": monthly_investment * time_to_build,
                "safety_ratio": target_amount / monthly_expenses
            },
            "recommendations": self._get_emergency_fund_recommendations(target_amount, monthly_investment, user_profile)
        }
    
    def _calculate_generic_goal(self, goal_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Calculate generic financial goal"""
        target_amount = goal_data.get('target_amount', 1000000)
        years_to_goal = goal_data.get('years_to_goal', 5)
        expected_return = goal_data.get('expected_return', 12) / 100
        current_amount = goal_data.get('current_amount', 0)
        
        # Calculate required monthly SIP
        remaining_amount = target_amount - current_amount
        monthly_return = expected_return / 12
        months_to_goal = years_to_goal * 12
        
        if monthly_return > 0:
            sip_required = remaining_amount * monthly_return / (((1 + monthly_return) ** months_to_goal) - 1)
        else:
            sip_required = remaining_amount / months_to_goal
        
        return {
            "goal_type": goal_data.get('goal_type', 'generic'),
            "calculation_date": datetime.now().isoformat(),
            "inputs": {
                "target_amount": target_amount,
                "current_amount": current_amount,
                "years_to_goal": years_to_goal,
                "expected_return": expected_return * 100
            },
            "results": {
                "remaining_amount": remaining_amount,
                "monthly_sip_required": sip_required,
                "total_investment": sip_required * months_to_goal,
                "wealth_multiplier": target_amount / (sip_required * months_to_goal) if sip_required > 0 else 0
            },
            "milestones": self._create_goal_milestones(target_amount, years_to_goal),
            "recommendations": self._get_generic_goal_recommendations(sip_required, years_to_goal)
        }
    
    # Helper methods for creating milestones and recommendations
    def _create_retirement_milestones(self, corpus_required: float, years: int) -> List[Dict]:
        """Create retirement milestones"""
        milestones = []
        for i in range(1, min(years + 1, 6)):  # Max 5 milestones
            milestone_years = i * (years // 5) if years >= 5 else i
            milestone_amount = corpus_required * (milestone_years / years)
            milestones.append({
                "year": milestone_years,
                "target_amount": milestone_amount,
                "description": f"Milestone {i}: ₹{milestone_amount:,.0f} by year {milestone_years}"
            })
        return milestones
    
    def _create_goal_milestones(self, target_amount: float, years: int) -> List[Dict]:
        """Create generic goal milestones"""
        milestones = []
        milestone_count = min(years, 5)
        for i in range(1, milestone_count + 1):
            milestone_years = i * (years / milestone_count)
            milestone_amount = target_amount * (i / milestone_count)
            milestones.append({
                "year": milestone_years,
                "target_amount": milestone_amount,
                "description": f"Milestone {i}: ₹{milestone_amount:,.0f} by year {milestone_years:.1f}"
            })
        return milestones
    
    def _get_retirement_recommendations(self, sip_required: float, user_profile: Dict) -> List[str]:
        """Get retirement planning recommendations"""
        recommendations = []
        current_income = user_profile.get('annual_income', 600000)
        sip_percentage = (sip_required * 12 / current_income) * 100
        
        if sip_percentage > 20:
            recommendations.append("Required SIP is high - consider extending retirement age or reducing expenses")
        
        recommendations.extend([
            "Start investing early to benefit from compounding",
            "Consider equity-heavy portfolio for long-term growth",
            "Review and increase SIP amount annually with salary increments",
            "Consider EPF, PPF, and NPS for additional retirement corpus"
        ])
        
        return recommendations
    
    def _get_education_recommendations(self, sip_required: float, years: int) -> List[str]:
        """Get education goal recommendations"""
        recommendations = [
            "Start investing early to reduce monthly burden",
            "Consider child education plans and ELSS for tax benefits"
        ]
        
        if years > 10:
            recommendations.append("Long time horizon allows for equity-heavy allocation")
        else:
            recommendations.append("Shorter time horizon - consider balanced allocation")
        
        return recommendations
    
    def _get_home_recommendations(self, sip_required: float, emi: float, user_profile: Dict) -> List[str]:
        """Get home purchase recommendations"""
        monthly_income = user_profile.get('annual_income', 600000) / 12
        total_monthly_burden = sip_required + emi
        burden_percentage = (total_monthly_burden / monthly_income) * 100
        
        recommendations = []
        
        if burden_percentage > 50:
            recommendations.append("Total monthly burden is high - consider lower home cost or longer tenure")
        
        recommendations.extend([
            "Consider real estate appreciation in location selection",
            "Factor in additional costs like registration, maintenance",
            "Build emergency fund before home purchase",
            "Compare home loan rates from different lenders"
        ])
        
        return recommendations
    
    def _get_emergency_fund_recommendations(self, target_amount: float, monthly_investment: float, user_profile: Dict) -> List[str]:
        """Get emergency fund recommendations"""
        return [
            "Keep emergency fund in liquid, low-risk instruments",
            "Consider savings account, liquid funds, or short-term FDs",
            "Build emergency fund before other investments",
            "Review and adjust amount based on lifestyle changes",
            "Aim for 6-12 months of expenses for adequate coverage"
        ]
    
    def _get_generic_goal_recommendations(self, sip_required: float, years: int) -> List[str]:
        """Get generic goal recommendations"""
        recommendations = [
            "Start investing systematically through SIP",
            "Review progress quarterly and adjust if needed"
        ]
        
        if years > 5:
            recommendations.append("Long-term goal allows for equity exposure")
        else:
            recommendations.append("Short-term goal - prefer debt instruments")
        
        return recommendations
