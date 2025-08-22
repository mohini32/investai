"""
Tax Dashboard Service - Comprehensive tax analytics and dashboard
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging

from app.models.tax import (
    TaxProfile, TaxCalculation, TaxSavingInvestment, CapitalGain, 
    TaxOptimizationSuggestion, TaxRegime
)
from app.models.user import User
from app.services.tax_service import TaxPlanningService

logger = logging.getLogger(__name__)


class TaxDashboardService:
    """Service for tax analytics dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tax_service = TaxPlanningService(db)
    
    def get_tax_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive tax planning dashboard"""
        try:
            dashboard_data = {
                "user_id": user_id,
                "dashboard_type": "tax_planning",
                "generated_at": datetime.now().isoformat(),
                "tax_overview": {},
                "tax_calculation_summary": {},
                "tax_savings_summary": {},
                "capital_gains_summary": {},
                "optimization_summary": {},
                "tax_calendar": {},
                "recommendations": []
            }
            
            # Tax Overview
            dashboard_data["tax_overview"] = self._get_tax_overview(user_id)
            
            # Tax Calculation Summary
            dashboard_data["tax_calculation_summary"] = self._get_tax_calculation_summary(user_id)
            
            # Tax Savings Summary
            dashboard_data["tax_savings_summary"] = self._get_tax_savings_summary(user_id)
            
            # Capital Gains Summary
            dashboard_data["capital_gains_summary"] = self._get_capital_gains_summary(user_id)
            
            # Optimization Summary
            dashboard_data["optimization_summary"] = self._get_optimization_summary(user_id)
            
            # Tax Calendar
            dashboard_data["tax_calendar"] = self._get_tax_calendar_summary(user_id)
            
            # Recommendations
            dashboard_data["recommendations"] = self._get_tax_recommendations(user_id)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate tax dashboard: {str(e)}")
            raise
    
    def get_tax_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed tax analytics"""
        try:
            analytics_data = {
                "user_id": user_id,
                "analytics_type": "detailed_tax",
                "generated_at": datetime.now().isoformat(),
                "regime_analysis": {},
                "deduction_analysis": {},
                "capital_gains_analysis": {},
                "tax_efficiency_analysis": {},
                "year_over_year_analysis": {},
                "optimization_opportunities": {}
            }
            
            # Regime Analysis
            analytics_data["regime_analysis"] = self._analyze_tax_regimes(user_id)
            
            # Deduction Analysis
            analytics_data["deduction_analysis"] = self._analyze_deductions(user_id)
            
            # Capital Gains Analysis
            analytics_data["capital_gains_analysis"] = self._analyze_capital_gains(user_id)
            
            # Tax Efficiency Analysis
            analytics_data["tax_efficiency_analysis"] = self._analyze_tax_efficiency(user_id)
            
            # Year over Year Analysis
            analytics_data["year_over_year_analysis"] = self._analyze_year_over_year(user_id)
            
            # Optimization Opportunities
            analytics_data["optimization_opportunities"] = self._identify_optimization_opportunities(user_id)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to generate tax analytics: {str(e)}")
            raise
    
    def get_tax_insights(self, user_id: int) -> Dict[str, Any]:
        """Get AI-powered tax insights"""
        try:
            insights_data = {
                "user_id": user_id,
                "insights_type": "tax_planning",
                "generated_at": datetime.now().isoformat(),
                "tax_health_score": 0,
                "key_tax_insights": [],
                "tax_action_items": [],
                "tax_opportunities": [],
                "tax_warnings": []
            }
            
            # Get tax profile
            tax_profile = self.tax_service.get_tax_profile(user_id)
            if not tax_profile:
                return insights_data
            
            # Calculate tax health score
            insights_data["tax_health_score"] = self._calculate_tax_health_score(tax_profile)
            
            # Generate insights
            insights_data["key_tax_insights"] = self._generate_key_tax_insights(tax_profile)
            insights_data["tax_action_items"] = self._generate_tax_action_items(tax_profile)
            insights_data["tax_opportunities"] = self._identify_tax_opportunities(tax_profile)
            insights_data["tax_warnings"] = self._identify_tax_warnings(tax_profile)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Failed to generate tax insights: {str(e)}")
            raise
    
    # Helper methods for dashboard components
    def _get_tax_overview(self, user_id: int) -> Dict[str, Any]:
        """Get tax overview for dashboard"""
        try:
            tax_profile = self.tax_service.get_tax_profile(user_id)
            if not tax_profile:
                return {"error": "Tax profile not found"}
            
            # Get latest tax calculation
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()
            
            overview_data = {
                "tax_regime": tax_profile.tax_regime.value,
                "annual_income": tax_profile.annual_income,
                "assessment_year": tax_profile.assessment_year,
                "is_senior_citizen": tax_profile.is_senior_citizen,
                "profile_created": tax_profile.created_at.isoformat(),
                "last_updated": tax_profile.updated_at.isoformat() if tax_profile.updated_at else None
            }
            
            if latest_calculation:
                overview_data.update({
                    "taxable_income": latest_calculation.taxable_income,
                    "total_tax": latest_calculation.total_tax,
                    "effective_tax_rate": (latest_calculation.total_tax / tax_profile.annual_income) * 100,
                    "recommended_regime": latest_calculation.recommended_regime.value,
                    "potential_savings": latest_calculation.tax_savings_amount,
                    "last_calculated": latest_calculation.calculation_date.isoformat()
                })
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Failed to get tax overview: {str(e)}")
            return {}
    
    def _get_tax_calculation_summary(self, user_id: int) -> Dict[str, Any]:
        """Get tax calculation summary"""
        try:
            tax_profile = self.tax_service.get_tax_profile(user_id)
            if not tax_profile:
                return {}
            
            # Get latest calculation
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()
            
            if not latest_calculation:
                return {"status": "no_calculation"}
            
            # Calculate breakdown
            total_deductions = (latest_calculation.standard_deduction + 
                              latest_calculation.total_80c_deduction + 
                              latest_calculation.total_80d_deduction + 
                              latest_calculation.total_80ccd_1b_deduction + 
                              latest_calculation.total_other_deductions)
            
            return {
                "gross_income": latest_calculation.gross_income,
                "total_deductions": total_deductions,
                "taxable_income": latest_calculation.taxable_income,
                "income_tax": latest_calculation.income_tax,
                "surcharge": latest_calculation.surcharge,
                "health_education_cess": latest_calculation.health_education_cess,
                "total_tax": latest_calculation.total_tax,
                "effective_tax_rate": (latest_calculation.total_tax / latest_calculation.gross_income) * 100,
                "deduction_breakdown": {
                    "standard_deduction": latest_calculation.standard_deduction,
                    "section_80c": latest_calculation.total_80c_deduction,
                    "section_80d": latest_calculation.total_80d_deduction,
                    "section_80ccd_1b": latest_calculation.total_80ccd_1b_deduction,
                    "other_deductions": latest_calculation.total_other_deductions
                },
                "regime_comparison": {
                    "old_regime_tax": latest_calculation.old_regime_tax,
                    "new_regime_tax": latest_calculation.new_regime_tax,
                    "recommended_regime": latest_calculation.recommended_regime.value,
                    "savings_amount": latest_calculation.tax_savings_amount
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get tax calculation summary: {str(e)}")
            return {}
    
    def _get_tax_savings_summary(self, user_id: int) -> Dict[str, Any]:
        """Get tax savings summary"""
        try:
            tax_profile = self.tax_service.get_tax_profile(user_id)
            if not tax_profile:
                return {}
            
            # Calculate current utilization
            section_80c_limit = 150000
            section_80d_limit = 25000 * (2 if tax_profile.is_senior_citizen else 1)
            section_80ccd_1b_limit = 50000
            
            current_80c = (tax_profile.section_80c_investments + 
                          tax_profile.employer_pf_contribution + 
                          tax_profile.home_loan_principal)
            
            current_80d = tax_profile.section_80d_premium
            current_80ccd_1b = tax_profile.employer_nps_contribution
            
            # Calculate remaining limits
            remaining_80c = max(0, section_80c_limit - current_80c)
            remaining_80d = max(0, section_80d_limit - current_80d)
            remaining_80ccd_1b = max(0, section_80ccd_1b_limit - current_80ccd_1b)
            
            # Calculate potential savings
            marginal_rate = self.tax_service._get_marginal_tax_rate(tax_profile)
            potential_80c_savings = remaining_80c * marginal_rate * 1.04
            potential_80d_savings = remaining_80d * marginal_rate * 1.04
            potential_80ccd_1b_savings = remaining_80ccd_1b * marginal_rate * 1.04
            
            return {
                "section_80c": {
                    "limit": section_80c_limit,
                    "utilized": current_80c,
                    "remaining": remaining_80c,
                    "utilization_percentage": (current_80c / section_80c_limit) * 100,
                    "potential_savings": potential_80c_savings
                },
                "section_80d": {
                    "limit": section_80d_limit,
                    "utilized": current_80d,
                    "remaining": remaining_80d,
                    "utilization_percentage": (current_80d / section_80d_limit) * 100 if section_80d_limit > 0 else 0,
                    "potential_savings": potential_80d_savings
                },
                "section_80ccd_1b": {
                    "limit": section_80ccd_1b_limit,
                    "utilized": current_80ccd_1b,
                    "remaining": remaining_80ccd_1b,
                    "utilization_percentage": (current_80ccd_1b / section_80ccd_1b_limit) * 100,
                    "potential_savings": potential_80ccd_1b_savings
                },
                "total_potential_savings": potential_80c_savings + potential_80d_savings + potential_80ccd_1b_savings,
                "marginal_tax_rate": marginal_rate * 100
            }
            
        except Exception as e:
            logger.error(f"Failed to get tax savings summary: {str(e)}")
            return {}
    
    def _get_capital_gains_summary(self, user_id: int) -> Dict[str, Any]:
        """Get capital gains summary"""
        try:
            tax_profile = self.tax_service.get_tax_profile(user_id)
            if not tax_profile:
                return {}
            
            # Get capital gains
            capital_gains = self.db.query(CapitalGain).filter(
                CapitalGain.tax_profile_id == tax_profile.id
            ).all()
            
            if not capital_gains:
                return {"status": "no_capital_gains"}
            
            # Aggregate by type
            gains_by_type = {}
            total_gains = 0
            total_losses = 0
            total_tax = 0
            
            for cg in capital_gains:
                gain_type = cg.gain_type.value
                if gain_type not in gains_by_type:
                    gains_by_type[gain_type] = {
                        "count": 0,
                        "total_gain_loss": 0,
                        "total_tax": 0
                    }
                
                gains_by_type[gain_type]["count"] += 1
                gains_by_type[gain_type]["total_gain_loss"] += cg.capital_gain_loss
                gains_by_type[gain_type]["total_tax"] += cg.tax_on_gain
                
                if cg.capital_gain_loss > 0:
                    total_gains += cg.capital_gain_loss
                else:
                    total_losses += abs(cg.capital_gain_loss)
                
                total_tax += cg.tax_on_gain
            
            return {
                "total_transactions": len(capital_gains),
                "total_gains": total_gains,
                "total_losses": total_losses,
                "net_gains": total_gains - total_losses,
                "total_tax": total_tax,
                "gains_by_type": gains_by_type,
                "tax_efficiency": (total_gains - total_tax) / total_gains * 100 if total_gains > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get capital gains summary: {str(e)}")
            return {}
    
    def _get_optimization_summary(self, user_id: int) -> Dict[str, Any]:
        """Get optimization summary"""
        try:
            tax_profile = self.tax_service.get_tax_profile(user_id)
            if not tax_profile:
                return {}
            
            # Get active suggestions
            active_suggestions = self.db.query(TaxOptimizationSuggestion).filter(
                and_(
                    TaxOptimizationSuggestion.tax_profile_id == tax_profile.id,
                    TaxOptimizationSuggestion.is_active == True,
                    TaxOptimizationSuggestion.is_implemented == False
                )
            ).all()
            
            # Categorize by priority
            priority_distribution = {}
            total_potential_savings = 0
            
            for suggestion in active_suggestions:
                priority = suggestion.priority
                priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
                total_potential_savings += suggestion.potential_tax_savings
            
            # Categorize by type
            type_distribution = {}
            for suggestion in active_suggestions:
                suggestion_type = suggestion.suggestion_type
                type_distribution[suggestion_type] = type_distribution.get(suggestion_type, 0) + 1
            
            return {
                "total_suggestions": len(active_suggestions),
                "total_potential_savings": total_potential_savings,
                "priority_distribution": priority_distribution,
                "type_distribution": type_distribution,
                "high_priority_count": priority_distribution.get("high", 0) + priority_distribution.get("critical", 0),
                "immediate_actions": len([s for s in active_suggestions if s.timeline == "immediate"]),
                "this_month_actions": len([s for s in active_suggestions if s.timeline == "this_month"])
            }
            
        except Exception as e:
            logger.error(f"Failed to get optimization summary: {str(e)}")
            return {}
    
    def _get_tax_calendar_summary(self, user_id: int) -> Dict[str, Any]:
        """Get tax calendar summary"""
        try:
            calendar_events = self.tax_service.get_tax_calendar(user_id)
            
            # Categorize events
            critical_events = [e for e in calendar_events if e["priority"] == "critical"]
            upcoming_actions = [e for e in calendar_events if e["action_required"]]
            
            # Find next critical deadline
            current_date = datetime.now().strftime("%Y-%m-%d")
            upcoming_critical = [e for e in critical_events if e["date"] >= current_date]
            next_deadline = min(upcoming_critical, key=lambda x: x["date"]) if upcoming_critical else None
            
            return {
                "total_events": len(calendar_events),
                "critical_events": len(critical_events),
                "upcoming_actions": len(upcoming_actions),
                "next_critical_deadline": next_deadline,
                "events_this_quarter": len([e for e in calendar_events if e["date"] >= current_date])
            }
            
        except Exception as e:
            logger.error(f"Failed to get tax calendar summary: {str(e)}")
            return {}
    
    def _get_tax_recommendations(self, user_id: int) -> List[str]:
        """Get tax recommendations"""
        try:
            recommendations = []
            
            tax_profile = self.tax_service.get_tax_profile(user_id)
            if not tax_profile:
                return recommendations
            
            # Get tax savings recommendations
            tax_recommendations = self.tax_service.get_tax_saving_recommendations(user_id)
            
            # Convert to simple recommendations
            for rec in tax_recommendations[:3]:  # Top 3
                recommendations.append(
                    f"Invest ₹{rec['recommended_amount']:,.0f} in {rec['name']} to save ₹{rec['tax_savings']:,.0f} in taxes"
                )
            
            # Add regime recommendation if applicable
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()
            
            if latest_calculation and latest_calculation.recommended_regime != tax_profile.tax_regime:
                recommendations.append(
                    f"Consider switching to {latest_calculation.recommended_regime.value.replace('_', ' ')} regime to save ₹{latest_calculation.tax_savings_amount:,.0f}"
                )
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to get tax recommendations: {str(e)}")
            return []

    # Helper methods for analytics
    def _calculate_tax_health_score(self, tax_profile: TaxProfile) -> float:
        """Calculate overall tax health score"""
        try:
            score = 0
            max_score = 100

            # Tax regime optimization (20 points)
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()

            if latest_calculation:
                if latest_calculation.recommended_regime == tax_profile.tax_regime:
                    score += 20
                else:
                    # Partial score based on savings potential
                    savings_ratio = latest_calculation.tax_savings_amount / latest_calculation.total_tax
                    score += max(0, 20 - (savings_ratio * 20))

            # Deduction utilization (30 points)
            section_80c_limit = 150000
            current_80c = (tax_profile.section_80c_investments +
                          tax_profile.employer_pf_contribution +
                          tax_profile.home_loan_principal)
            utilization_80c = min(1.0, current_80c / section_80c_limit)
            score += utilization_80c * 20

            section_80d_limit = 25000 * (2 if tax_profile.is_senior_citizen else 1)
            utilization_80d = min(1.0, tax_profile.section_80d_premium / section_80d_limit) if section_80d_limit > 0 else 0
            score += utilization_80d * 10

            # Tax planning proactiveness (25 points)
            # Check if user has recent calculations
            if latest_calculation and (datetime.now() - latest_calculation.calculation_date).days < 90:
                score += 15

            # Check for optimization suggestions implementation
            active_suggestions = self.db.query(TaxOptimizationSuggestion).filter(
                and_(
                    TaxOptimizationSuggestion.tax_profile_id == tax_profile.id,
                    TaxOptimizationSuggestion.is_active == True
                )
            ).count()

            if active_suggestions < 3:
                score += 10  # Good if few pending suggestions

            # Capital gains management (25 points)
            capital_gains = self.db.query(CapitalGain).filter(
                CapitalGain.tax_profile_id == tax_profile.id
            ).all()

            if capital_gains:
                total_gains = sum(cg.capital_gain_loss for cg in capital_gains if cg.capital_gain_loss > 0)
                total_tax = sum(cg.tax_on_gain for cg in capital_gains)

                if total_gains > 0:
                    tax_efficiency = (total_gains - total_tax) / total_gains
                    score += tax_efficiency * 25
                else:
                    score += 15  # Neutral score for no gains
            else:
                score += 15  # Neutral score for no capital gains

            return min(max_score, max(0, score))

        except Exception as e:
            logger.error(f"Failed to calculate tax health score: {str(e)}")
            return 50.0

    def _generate_key_tax_insights(self, tax_profile: TaxProfile) -> List[str]:
        """Generate key tax insights"""
        try:
            insights = []

            # Get latest calculation
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()

            if latest_calculation:
                effective_rate = (latest_calculation.total_tax / tax_profile.annual_income) * 100
                insights.append(f"Your effective tax rate is {effective_rate:.1f}% on annual income of ₹{tax_profile.annual_income:,.0f}")

                if latest_calculation.recommended_regime != tax_profile.tax_regime:
                    insights.append(f"Switching to {latest_calculation.recommended_regime.value.replace('_', ' ')} regime could save ₹{latest_calculation.tax_savings_amount:,.0f} annually")

            # Deduction insights
            section_80c_limit = 150000
            current_80c = (tax_profile.section_80c_investments +
                          tax_profile.employer_pf_contribution +
                          tax_profile.home_loan_principal)
            remaining_80c = max(0, section_80c_limit - current_80c)

            if remaining_80c > 0:
                marginal_rate = self.tax_service._get_marginal_tax_rate(tax_profile)
                potential_savings = remaining_80c * marginal_rate * 1.04
                insights.append(f"You can save up to ₹{potential_savings:,.0f} by utilizing remaining ₹{remaining_80c:,.0f} under Section 80C")

            # Capital gains insights
            capital_gains = self.db.query(CapitalGain).filter(
                CapitalGain.tax_profile_id == tax_profile.id
            ).all()

            if capital_gains:
                total_gains = sum(cg.capital_gain_loss for cg in capital_gains if cg.capital_gain_loss > 0)
                total_losses = sum(abs(cg.capital_gain_loss) for cg in capital_gains if cg.capital_gain_loss < 0)

                if total_losses > 0:
                    insights.append(f"You have ₹{total_losses:,.0f} in capital losses that can offset future gains")

            return insights[:5]  # Limit to 5 insights

        except Exception as e:
            logger.error(f"Failed to generate key tax insights: {str(e)}")
            return []

    def _generate_tax_action_items(self, tax_profile: TaxProfile) -> List[str]:
        """Generate tax action items"""
        try:
            action_items = []

            # Check for pending optimizations
            active_suggestions = self.db.query(TaxOptimizationSuggestion).filter(
                and_(
                    TaxOptimizationSuggestion.tax_profile_id == tax_profile.id,
                    TaxOptimizationSuggestion.is_active == True,
                    TaxOptimizationSuggestion.is_implemented == False,
                    TaxOptimizationSuggestion.priority.in_(["high", "critical"])
                )
            ).all()

            for suggestion in active_suggestions[:3]:  # Top 3
                action_items.append(suggestion.title)

            # Check for regime optimization
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()

            if latest_calculation and latest_calculation.recommended_regime != tax_profile.tax_regime:
                action_items.append(f"Review switching to {latest_calculation.recommended_regime.value.replace('_', ' ')} tax regime")

            # Check for outdated calculations
            if latest_calculation and (datetime.now() - latest_calculation.calculation_date).days > 90:
                action_items.append("Update tax calculation with latest financial information")

            # General actions
            if not action_items:
                action_items.extend([
                    "Review and update tax profile information",
                    "Plan tax-saving investments for current financial year",
                    "Consider tax-loss harvesting opportunities"
                ])

            return action_items[:5]  # Limit to 5 action items

        except Exception as e:
            logger.error(f"Failed to generate tax action items: {str(e)}")
            return []

    def _identify_tax_opportunities(self, tax_profile: TaxProfile) -> List[str]:
        """Identify tax optimization opportunities"""
        try:
            opportunities = []

            # Deduction opportunities
            section_80c_limit = 150000
            current_80c = (tax_profile.section_80c_investments +
                          tax_profile.employer_pf_contribution +
                          tax_profile.home_loan_principal)
            remaining_80c = max(0, section_80c_limit - current_80c)

            if remaining_80c > 50000:
                opportunities.append(f"Significant Section 80C opportunity: ₹{remaining_80c:,.0f} remaining limit")

            # NPS opportunity
            if tax_profile.employer_nps_contribution < 50000:
                remaining_nps = 50000 - tax_profile.employer_nps_contribution
                opportunities.append(f"Additional NPS investment opportunity: ₹{remaining_nps:,.0f} under Section 80CCD(1B)")

            # Health insurance opportunity
            section_80d_limit = 25000 * (2 if tax_profile.is_senior_citizen else 1)
            if tax_profile.section_80d_premium < section_80d_limit:
                remaining_80d = section_80d_limit - tax_profile.section_80d_premium
                opportunities.append(f"Health insurance premium opportunity: ₹{remaining_80d:,.0f} under Section 80D")

            # Capital gains optimization
            capital_gains = self.db.query(CapitalGain).filter(
                CapitalGain.tax_profile_id == tax_profile.id
            ).all()

            if capital_gains:
                total_losses = sum(abs(cg.capital_gain_loss) for cg in capital_gains if cg.capital_gain_loss < 0)
                if total_losses > 0:
                    opportunities.append(f"Tax-loss harvesting opportunity: ₹{total_losses:,.0f} in losses available")

            return opportunities[:5]  # Limit to 5 opportunities

        except Exception as e:
            logger.error(f"Failed to identify tax opportunities: {str(e)}")
            return []

    def _identify_tax_warnings(self, tax_profile: TaxProfile) -> List[str]:
        """Identify tax warnings"""
        try:
            warnings = []

            # High tax rate warning
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()

            if latest_calculation:
                effective_rate = (latest_calculation.total_tax / tax_profile.annual_income) * 100
                if effective_rate > 25:
                    warnings.append(f"High effective tax rate: {effective_rate:.1f}% - consider optimization strategies")

            # Suboptimal regime warning
            if latest_calculation and latest_calculation.recommended_regime != tax_profile.tax_regime:
                savings_percentage = (latest_calculation.tax_savings_amount / latest_calculation.total_tax) * 100
                if savings_percentage > 10:
                    warnings.append(f"Suboptimal tax regime: Missing {savings_percentage:.1f}% tax savings")

            # Underutilized deductions
            section_80c_limit = 150000
            current_80c = (tax_profile.section_80c_investments +
                          tax_profile.employer_pf_contribution +
                          tax_profile.home_loan_principal)
            utilization_80c = (current_80c / section_80c_limit) * 100

            if utilization_80c < 50:
                warnings.append(f"Low Section 80C utilization: Only {utilization_80c:.1f}% of limit used")

            # Outdated information
            if latest_calculation and (datetime.now() - latest_calculation.calculation_date).days > 180:
                warnings.append("Tax calculation is outdated - update with current financial information")

            # Capital gains tax burden
            capital_gains = self.db.query(CapitalGain).filter(
                CapitalGain.tax_profile_id == tax_profile.id
            ).all()

            if capital_gains:
                total_gains = sum(cg.capital_gain_loss for cg in capital_gains if cg.capital_gain_loss > 0)
                total_tax = sum(cg.tax_on_gain for cg in capital_gains)

                if total_gains > 0:
                    tax_percentage = (total_tax / total_gains) * 100
                    if tax_percentage > 20:
                        warnings.append(f"High capital gains tax burden: {tax_percentage:.1f}% of gains")

            return warnings[:5]  # Limit to 5 warnings

        except Exception as e:
            logger.error(f"Failed to identify tax warnings: {str(e)}")
            return []

    # Placeholder methods for detailed analytics (would be implemented based on specific requirements)
    def _analyze_tax_regimes(self, user_id: int) -> Dict[str, Any]:
        """Analyze tax regimes for user"""
        return {"analysis": "tax_regimes", "user_id": user_id}

    def _analyze_deductions(self, user_id: int) -> Dict[str, Any]:
        """Analyze deductions utilization"""
        return {"analysis": "deductions", "user_id": user_id}

    def _analyze_capital_gains(self, user_id: int) -> Dict[str, Any]:
        """Analyze capital gains patterns"""
        return {"analysis": "capital_gains", "user_id": user_id}

    def _analyze_tax_efficiency(self, user_id: int) -> Dict[str, Any]:
        """Analyze tax efficiency"""
        return {"analysis": "tax_efficiency", "user_id": user_id}

    def _analyze_year_over_year(self, user_id: int) -> Dict[str, Any]:
        """Analyze year-over-year tax trends"""
        return {"analysis": "year_over_year", "user_id": user_id}

    def _identify_optimization_opportunities(self, user_id: int) -> Dict[str, Any]:
        """Identify optimization opportunities"""
        return {"analysis": "optimization_opportunities", "user_id": user_id}
