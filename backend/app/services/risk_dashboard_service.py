"""
Risk Dashboard Service - Comprehensive risk analytics and dashboard
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging
import numpy as np

from app.models.risk import PortfolioRiskProfile, RiskAlert, StressTestResult, RiskLevel
from app.models.portfolio import Portfolio
from app.models.user import User
from app.services.risk_service import RiskManagementService

logger = logging.getLogger(__name__)


class RiskDashboardService:
    """Service for risk analytics dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = RiskManagementService(db)
    
    def get_risk_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive risk dashboard"""
        try:
            dashboard_data = {
                "user_id": user_id,
                "dashboard_type": "risk_management",
                "generated_at": datetime.now().isoformat(),
                "risk_overview": {},
                "portfolio_risk_summary": {},
                "stress_test_summary": {},
                "risk_alerts_summary": {},
                "risk_trends": {},
                "recommendations": []
            }
            
            # Risk Overview
            dashboard_data["risk_overview"] = self._get_risk_overview(user_id)
            
            # Portfolio Risk Summary
            dashboard_data["portfolio_risk_summary"] = self._get_portfolio_risk_summary(user_id)
            
            # Stress Test Summary
            dashboard_data["stress_test_summary"] = self._get_stress_test_summary(user_id)
            
            # Risk Alerts Summary
            dashboard_data["risk_alerts_summary"] = self._get_risk_alerts_summary(user_id)
            
            # Risk Trends
            dashboard_data["risk_trends"] = self._get_risk_trends(user_id)
            
            # Recommendations
            dashboard_data["recommendations"] = self._get_risk_recommendations(user_id)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate risk dashboard: {str(e)}")
            raise
    
    def get_risk_analytics(self, user_id: int, portfolio_id: Optional[int] = None) -> Dict[str, Any]:
        """Get detailed risk analytics"""
        try:
            analytics_data = {
                "user_id": user_id,
                "portfolio_id": portfolio_id,
                "analytics_type": "detailed_risk",
                "generated_at": datetime.now().isoformat(),
                "risk_decomposition": {},
                "correlation_analysis": {},
                "concentration_analysis": {},
                "var_analysis": {},
                "stress_test_analysis": {},
                "benchmark_comparison": {}
            }
            
            if portfolio_id:
                # Single portfolio analysis
                analytics_data["risk_decomposition"] = self._analyze_single_portfolio_risk(portfolio_id, user_id)
                analytics_data["correlation_analysis"] = self._analyze_single_portfolio_correlation(portfolio_id, user_id)
                analytics_data["concentration_analysis"] = self._analyze_single_portfolio_concentration(portfolio_id, user_id)
                analytics_data["var_analysis"] = self._analyze_single_portfolio_var(portfolio_id, user_id)
                analytics_data["stress_test_analysis"] = self._analyze_single_portfolio_stress_tests(portfolio_id, user_id)
                analytics_data["benchmark_comparison"] = self._compare_single_portfolio_to_benchmark(portfolio_id, user_id)
            else:
                # All portfolios analysis
                analytics_data["risk_decomposition"] = self._analyze_all_portfolios_risk(user_id)
                analytics_data["correlation_analysis"] = self._analyze_all_portfolios_correlation(user_id)
                analytics_data["concentration_analysis"] = self._analyze_all_portfolios_concentration(user_id)
                analytics_data["var_analysis"] = self._analyze_all_portfolios_var(user_id)
                analytics_data["stress_test_analysis"] = self._analyze_all_portfolios_stress_tests(user_id)
                analytics_data["benchmark_comparison"] = self._compare_all_portfolios_to_benchmark(user_id)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to generate risk analytics: {str(e)}")
            raise
    
    def get_risk_insights(self, user_id: int) -> Dict[str, Any]:
        """Get AI-powered risk insights"""
        try:
            insights_data = {
                "user_id": user_id,
                "insights_type": "risk_management",
                "generated_at": datetime.now().isoformat(),
                "overall_risk_health": 0,
                "key_risk_insights": [],
                "risk_action_items": [],
                "risk_opportunities": [],
                "risk_warnings": []
            }
            
            # Get all user portfolios with risk profiles
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            risk_profiles = []
            
            for portfolio in portfolios:
                risk_profile = self.risk_service.get_portfolio_risk_profile(portfolio.id, user_id)
                if risk_profile:
                    risk_profiles.append(risk_profile)
            
            if not risk_profiles:
                return insights_data
            
            # Calculate overall risk health
            insights_data["overall_risk_health"] = self._calculate_overall_risk_health(risk_profiles)
            
            # Generate insights
            insights_data["key_risk_insights"] = self._generate_key_risk_insights(risk_profiles)
            insights_data["risk_action_items"] = self._generate_risk_action_items(risk_profiles)
            insights_data["risk_opportunities"] = self._identify_risk_opportunities(risk_profiles)
            insights_data["risk_warnings"] = self._identify_risk_warnings(risk_profiles)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Failed to generate risk insights: {str(e)}")
            raise
    
    # Helper methods for dashboard components
    def _get_risk_overview(self, user_id: int) -> Dict[str, Any]:
        """Get risk overview for dashboard"""
        try:
            # Get all portfolios with risk profiles
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            
            risk_data = {
                "total_portfolios": len(portfolios),
                "portfolios_with_risk_assessment": 0,
                "average_risk_score": 0,
                "risk_level_distribution": {},
                "highest_risk_portfolio": None,
                "lowest_risk_portfolio": None
            }
            
            risk_profiles = []
            risk_scores = []
            
            for portfolio in portfolios:
                risk_profile = self.risk_service.get_portfolio_risk_profile(portfolio.id, user_id)
                if risk_profile:
                    risk_profiles.append(risk_profile)
                    risk_scores.append(risk_profile.risk_score)
            
            risk_data["portfolios_with_risk_assessment"] = len(risk_profiles)
            
            if risk_scores:
                risk_data["average_risk_score"] = sum(risk_scores) / len(risk_scores)
                
                # Find highest and lowest risk portfolios
                highest_risk_profile = max(risk_profiles, key=lambda rp: rp.risk_score)
                lowest_risk_profile = min(risk_profiles, key=lambda rp: rp.risk_score)
                
                risk_data["highest_risk_portfolio"] = {
                    "portfolio_id": highest_risk_profile.portfolio_id,
                    "risk_score": highest_risk_profile.risk_score,
                    "risk_level": highest_risk_profile.overall_risk_level.value
                }
                
                risk_data["lowest_risk_portfolio"] = {
                    "portfolio_id": lowest_risk_profile.portfolio_id,
                    "risk_score": lowest_risk_profile.risk_score,
                    "risk_level": lowest_risk_profile.overall_risk_level.value
                }
            
            # Risk level distribution
            risk_levels = {}
            for risk_profile in risk_profiles:
                level = risk_profile.overall_risk_level.value
                risk_levels[level] = risk_levels.get(level, 0) + 1
            
            risk_data["risk_level_distribution"] = risk_levels
            
            return risk_data
            
        except Exception as e:
            logger.error(f"Failed to get risk overview: {str(e)}")
            return {}
    
    def _get_portfolio_risk_summary(self, user_id: int) -> Dict[str, Any]:
        """Get portfolio risk summary"""
        try:
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            
            portfolio_summaries = []
            total_value = 0
            weighted_risk_score = 0
            
            for portfolio in portfolios:
                risk_profile = self.risk_service.get_portfolio_risk_profile(portfolio.id, user_id)
                
                if risk_profile:
                    portfolio_value = portfolio.current_value or 0
                    total_value += portfolio_value
                    weighted_risk_score += risk_profile.risk_score * portfolio_value
                    
                    portfolio_summaries.append({
                        "portfolio_id": portfolio.id,
                        "portfolio_name": portfolio.name,
                        "portfolio_value": portfolio_value,
                        "risk_score": risk_profile.risk_score,
                        "risk_level": risk_profile.overall_risk_level.value,
                        "volatility": risk_profile.portfolio_volatility,
                        "beta": risk_profile.portfolio_beta,
                        "var_1d_99": risk_profile.var_1_day_99,
                        "max_drawdown": risk_profile.maximum_drawdown,
                        "concentration_score": risk_profile.concentration_score,
                        "assessment_date": risk_profile.assessment_date.isoformat()
                    })
            
            # Calculate portfolio-weighted average risk score
            avg_weighted_risk_score = weighted_risk_score / total_value if total_value > 0 else 0
            
            return {
                "portfolio_summaries": portfolio_summaries,
                "total_portfolio_value": total_value,
                "average_weighted_risk_score": avg_weighted_risk_score,
                "portfolios_count": len(portfolio_summaries)
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio risk summary: {str(e)}")
            return {}
    
    def _get_stress_test_summary(self, user_id: int) -> Dict[str, Any]:
        """Get stress test summary"""
        try:
            # Get all stress test results for user
            stress_tests = self.db.query(StressTestResult).join(PortfolioRiskProfile).filter(
                PortfolioRiskProfile.user_id == user_id
            ).all()
            
            if not stress_tests:
                return {"total_tests": 0, "scenarios_tested": 0}
            
            # Analyze stress test results
            scenario_impacts = {}
            worst_case_scenario = None
            best_case_scenario = None
            
            for test in stress_tests:
                scenario = test.scenario_type.value
                impact = test.portfolio_impact_percentage
                
                if scenario not in scenario_impacts:
                    scenario_impacts[scenario] = []
                scenario_impacts[scenario].append(impact)
                
                if worst_case_scenario is None or impact < worst_case_scenario["impact"]:
                    worst_case_scenario = {
                        "scenario": test.scenario_name,
                        "impact": impact,
                        "recovery_days": test.estimated_recovery_days
                    }
                
                if best_case_scenario is None or impact > best_case_scenario["impact"]:
                    best_case_scenario = {
                        "scenario": test.scenario_name,
                        "impact": impact,
                        "recovery_days": test.estimated_recovery_days
                    }
            
            # Calculate average impacts by scenario
            avg_scenario_impacts = {}
            for scenario, impacts in scenario_impacts.items():
                avg_scenario_impacts[scenario] = sum(impacts) / len(impacts)
            
            return {
                "total_tests": len(stress_tests),
                "scenarios_tested": len(scenario_impacts),
                "average_scenario_impacts": avg_scenario_impacts,
                "worst_case_scenario": worst_case_scenario,
                "best_case_scenario": best_case_scenario,
                "stress_test_coverage": list(scenario_impacts.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to get stress test summary: {str(e)}")
            return {}
    
    def _get_risk_alerts_summary(self, user_id: int) -> Dict[str, Any]:
        """Get risk alerts summary"""
        try:
            # Get all risk alerts for user
            all_alerts = self.db.query(RiskAlert).filter(RiskAlert.user_id == user_id).all()
            active_alerts = [a for a in all_alerts if not a.is_resolved]
            
            # Categorize by level
            alert_levels = {}
            for alert in active_alerts:
                level = alert.alert_level.value
                alert_levels[level] = alert_levels.get(level, 0) + 1
            
            # Categorize by type
            alert_types = {}
            for alert in active_alerts:
                alert_type = alert.alert_type
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
            
            # Recent alerts (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_alerts = [a for a in all_alerts if a.created_at >= seven_days_ago]
            
            return {
                "total_alerts": len(all_alerts),
                "active_alerts": len(active_alerts),
                "recent_alerts_7d": len(recent_alerts),
                "alert_levels": alert_levels,
                "alert_types": alert_types,
                "critical_alerts": len([a for a in active_alerts if a.alert_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]]),
                "unacknowledged_alerts": len([a for a in active_alerts if not a.is_acknowledged])
            }
            
        except Exception as e:
            logger.error(f"Failed to get risk alerts summary: {str(e)}")
            return {}
    
    def _get_risk_trends(self, user_id: int) -> Dict[str, Any]:
        """Get risk trends over time"""
        try:
            # This would typically analyze historical risk profiles
            # For now, return mock trend data
            
            return {
                "trend_period_days": 90,
                "risk_score_trend": "stable",
                "volatility_trend": "increasing",
                "concentration_trend": "improving",
                "overall_trend": "stable",
                "trend_analysis": {
                    "improving_metrics": ["concentration", "correlation"],
                    "deteriorating_metrics": ["volatility"],
                    "stable_metrics": ["risk_score", "beta"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get risk trends: {str(e)}")
            return {}
    
    def _get_risk_recommendations(self, user_id: int) -> List[str]:
        """Get risk management recommendations"""
        try:
            recommendations = []
            
            # Get risk profiles
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            high_risk_portfolios = 0
            high_concentration_portfolios = 0
            
            for portfolio in portfolios:
                risk_profile = self.risk_service.get_portfolio_risk_profile(portfolio.id, user_id)
                if risk_profile:
                    if risk_profile.risk_score > 75:
                        high_risk_portfolios += 1
                    if risk_profile.concentration_score and risk_profile.concentration_score > 70:
                        high_concentration_portfolios += 1
            
            # Generate recommendations
            if high_risk_portfolios > 0:
                recommendations.append(f"Review {high_risk_portfolios} high-risk portfolio(s) for risk reduction opportunities")
            
            if high_concentration_portfolios > 0:
                recommendations.append(f"Diversify {high_concentration_portfolios} concentrated portfolio(s) to reduce risk")
            
            # Get active alerts
            active_alerts = self.db.query(RiskAlert).filter(
                and_(RiskAlert.user_id == user_id, RiskAlert.is_resolved == False)
            ).count()
            
            if active_alerts > 5:
                recommendations.append(f"Address {active_alerts} active risk alerts")
            
            # Default recommendations
            if not recommendations:
                recommendations.extend([
                    "Regular portfolio rebalancing helps maintain optimal risk levels",
                    "Consider stress testing portfolios quarterly",
                    "Monitor correlation between holdings to ensure diversification"
                ])
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to get risk recommendations: {str(e)}")
            return []

    # Helper methods for analytics
    def _calculate_overall_risk_health(self, risk_profiles: List[PortfolioRiskProfile]) -> float:
        """Calculate overall risk health score"""
        try:
            if not risk_profiles:
                return 0

            # Calculate weighted average based on portfolio values
            total_score = 0
            total_weight = 0

            for risk_profile in risk_profiles:
                portfolio_value = risk_profile.portfolio.current_value or 0
                # Invert risk score for health (lower risk = higher health)
                health_score = 100 - risk_profile.risk_score

                total_score += health_score * portfolio_value
                total_weight += portfolio_value

            return total_score / total_weight if total_weight > 0 else 0

        except Exception as e:
            logger.error(f"Failed to calculate overall risk health: {str(e)}")
            return 50

    def _generate_key_risk_insights(self, risk_profiles: List[PortfolioRiskProfile]) -> List[str]:
        """Generate key risk insights"""
        try:
            insights = []

            if not risk_profiles:
                return ["No risk assessments available"]

            # Average risk score insight
            avg_risk_score = sum(rp.risk_score for rp in risk_profiles) / len(risk_profiles)
            if avg_risk_score > 70:
                insights.append(f"Portfolio risk is elevated with average score of {avg_risk_score:.1f}")
            elif avg_risk_score < 40:
                insights.append(f"Portfolio risk is well-controlled with average score of {avg_risk_score:.1f}")
            else:
                insights.append(f"Portfolio risk is moderate with average score of {avg_risk_score:.1f}")

            # Volatility insight
            volatilities = [rp.portfolio_volatility for rp in risk_profiles if rp.portfolio_volatility]
            if volatilities:
                avg_volatility = sum(volatilities) / len(volatilities)
                if avg_volatility > 0.3:
                    insights.append(f"High portfolio volatility detected ({avg_volatility:.1%} average)")
                elif avg_volatility < 0.15:
                    insights.append(f"Low portfolio volatility indicates conservative positioning ({avg_volatility:.1%})")

            # Concentration insight
            concentrations = [rp.concentration_score for rp in risk_profiles if rp.concentration_score]
            if concentrations:
                avg_concentration = sum(concentrations) / len(concentrations)
                if avg_concentration > 70:
                    insights.append(f"High portfolio concentration increases risk ({avg_concentration:.1f} average score)")
                elif avg_concentration < 40:
                    insights.append(f"Good portfolio diversification reduces risk ({avg_concentration:.1f} concentration score)")

            # Beta insight
            betas = [rp.portfolio_beta for rp in risk_profiles if rp.portfolio_beta]
            if betas:
                avg_beta = sum(betas) / len(betas)
                if avg_beta > 1.3:
                    insights.append(f"Portfolios are more volatile than market (average beta: {avg_beta:.2f})")
                elif avg_beta < 0.7:
                    insights.append(f"Portfolios are less volatile than market (average beta: {avg_beta:.2f})")

            return insights[:5]  # Limit to 5 insights

        except Exception as e:
            logger.error(f"Failed to generate key risk insights: {str(e)}")
            return []

    def _generate_risk_action_items(self, risk_profiles: List[PortfolioRiskProfile]) -> List[str]:
        """Generate risk action items"""
        try:
            action_items = []

            for risk_profile in risk_profiles:
                portfolio_name = risk_profile.portfolio.name

                # High risk score actions
                if risk_profile.risk_score > 80:
                    action_items.append(f"Reduce risk in '{portfolio_name}' portfolio (risk score: {risk_profile.risk_score:.1f})")

                # High concentration actions
                if risk_profile.concentration_score and risk_profile.concentration_score > 75:
                    action_items.append(f"Diversify '{portfolio_name}' portfolio to reduce concentration risk")

                # High volatility actions
                if risk_profile.portfolio_volatility and risk_profile.portfolio_volatility > 0.35:
                    action_items.append(f"Consider adding defensive assets to '{portfolio_name}' to reduce volatility")

                # Large drawdown actions
                if risk_profile.maximum_drawdown and risk_profile.maximum_drawdown < -0.3:
                    action_items.append(f"Review risk management strategy for '{portfolio_name}' due to large drawdowns")

            # General actions if no specific issues
            if not action_items:
                action_items.extend([
                    "Continue monitoring portfolio risk metrics regularly",
                    "Consider quarterly portfolio rebalancing",
                    "Review and update risk tolerance periodically"
                ])

            return action_items[:5]  # Limit to 5 action items

        except Exception as e:
            logger.error(f"Failed to generate risk action items: {str(e)}")
            return []

    def _identify_risk_opportunities(self, risk_profiles: List[PortfolioRiskProfile]) -> List[str]:
        """Identify risk optimization opportunities"""
        try:
            opportunities = []

            for risk_profile in risk_profiles:
                portfolio_name = risk_profile.portfolio.name

                # Low risk utilization
                if risk_profile.risk_score < 30:
                    opportunities.append(f"'{portfolio_name}' may be too conservative - consider higher-return assets")

                # Good Sharpe ratio
                if risk_profile.sharpe_ratio and risk_profile.sharpe_ratio > 1.5:
                    opportunities.append(f"'{portfolio_name}' shows excellent risk-adjusted returns")

                # Low correlation opportunity
                if risk_profile.avg_correlation and risk_profile.avg_correlation < 0.3:
                    opportunities.append(f"'{portfolio_name}' has good diversification - maintain current strategy")

                # Beta optimization
                if risk_profile.portfolio_beta and 0.8 <= risk_profile.portfolio_beta <= 1.2:
                    opportunities.append(f"'{portfolio_name}' has optimal market exposure (beta: {risk_profile.portfolio_beta:.2f})")

            return opportunities[:5]  # Limit to 5 opportunities

        except Exception as e:
            logger.error(f"Failed to identify risk opportunities: {str(e)}")
            return []

    def _identify_risk_warnings(self, risk_profiles: List[PortfolioRiskProfile]) -> List[str]:
        """Identify risk warnings"""
        try:
            warnings = []

            for risk_profile in risk_profiles:
                portfolio_name = risk_profile.portfolio.name

                # Critical risk level
                if risk_profile.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                    warnings.append(f"'{portfolio_name}' has {risk_profile.overall_risk_level.value} risk level")

                # Extreme VaR
                if risk_profile.var_1_day_99 and risk_profile.var_1_day_99 < -0.08:
                    warnings.append(f"'{portfolio_name}' has high daily loss potential ({risk_profile.var_1_day_99:.1%})")

                # High correlation warning
                if risk_profile.max_correlation and risk_profile.max_correlation > 0.9:
                    warnings.append(f"'{portfolio_name}' has highly correlated assets reducing diversification")

                # Extreme beta warning
                if risk_profile.portfolio_beta and (risk_profile.portfolio_beta > 2.0 or risk_profile.portfolio_beta < 0.3):
                    warnings.append(f"'{portfolio_name}' has extreme market sensitivity (beta: {risk_profile.portfolio_beta:.2f})")

            return warnings[:5]  # Limit to 5 warnings

        except Exception as e:
            logger.error(f"Failed to identify risk warnings: {str(e)}")
            return []

    # Placeholder methods for detailed analytics (would be implemented based on specific requirements)
    def _analyze_single_portfolio_risk(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze risk decomposition for single portfolio"""
        return {"analysis": "single_portfolio_risk", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_correlation(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze correlation for single portfolio"""
        return {"analysis": "single_portfolio_correlation", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_concentration(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze concentration for single portfolio"""
        return {"analysis": "single_portfolio_concentration", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_var(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze VaR for single portfolio"""
        return {"analysis": "single_portfolio_var", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_stress_tests(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze stress tests for single portfolio"""
        return {"analysis": "single_portfolio_stress_tests", "portfolio_id": portfolio_id}

    def _compare_single_portfolio_to_benchmark(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Compare single portfolio to benchmark"""
        return {"analysis": "single_portfolio_benchmark", "portfolio_id": portfolio_id}

    def _analyze_all_portfolios_risk(self, user_id: int) -> Dict[str, Any]:
        """Analyze risk decomposition for all portfolios"""
        return {"analysis": "all_portfolios_risk", "user_id": user_id}

    def _analyze_all_portfolios_correlation(self, user_id: int) -> Dict[str, Any]:
        """Analyze correlation for all portfolios"""
        return {"analysis": "all_portfolios_correlation", "user_id": user_id}

    def _analyze_all_portfolios_concentration(self, user_id: int) -> Dict[str, Any]:
        """Analyze concentration for all portfolios"""
        return {"analysis": "all_portfolios_concentration", "user_id": user_id}

    def _analyze_all_portfolios_var(self, user_id: int) -> Dict[str, Any]:
        """Analyze VaR for all portfolios"""
        return {"analysis": "all_portfolios_var", "user_id": user_id}

    def _analyze_all_portfolios_stress_tests(self, user_id: int) -> Dict[str, Any]:
        """Analyze stress tests for all portfolios"""
        return {"analysis": "all_portfolios_stress_tests", "user_id": user_id}

    def _compare_all_portfolios_to_benchmark(self, user_id: int) -> Dict[str, Any]:
        """Compare all portfolios to benchmark"""
        return {"analysis": "all_portfolios_benchmark", "user_id": user_id}
