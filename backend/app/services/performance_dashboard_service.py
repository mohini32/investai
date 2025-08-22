"""
Performance Dashboard Service - Comprehensive performance analytics dashboard
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging
import numpy as np

from app.models.performance import (
    PortfolioPerformance, BenchmarkComparison, AttributionAnalysis, 
    PerformanceAlert, PerformancePeriod
)
from app.models.portfolio import Portfolio
from app.models.user import User
from app.services.performance_service import PerformanceAnalyticsService

logger = logging.getLogger(__name__)


class PerformanceDashboardService:
    """Service for performance analytics dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
        self.performance_service = PerformanceAnalyticsService(db)
    
    def get_performance_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive performance dashboard"""
        try:
            dashboard_data = {
                "user_id": user_id,
                "dashboard_type": "performance_analytics",
                "generated_at": datetime.now().isoformat(),
                "performance_overview": {},
                "portfolio_performance_summary": {},
                "benchmark_comparison_summary": {},
                "attribution_summary": {},
                "risk_metrics_summary": {},
                "alerts_summary": {},
                "performance_insights": []
            }
            
            # Performance Overview
            dashboard_data["performance_overview"] = self._get_performance_overview(user_id)
            
            # Portfolio Performance Summary
            dashboard_data["portfolio_performance_summary"] = self._get_portfolio_performance_summary(user_id)
            
            # Benchmark Comparison Summary
            dashboard_data["benchmark_comparison_summary"] = self._get_benchmark_comparison_summary(user_id)
            
            # Attribution Summary
            dashboard_data["attribution_summary"] = self._get_attribution_summary(user_id)
            
            # Risk Metrics Summary
            dashboard_data["risk_metrics_summary"] = self._get_risk_metrics_summary(user_id)
            
            # Alerts Summary
            dashboard_data["alerts_summary"] = self._get_alerts_summary(user_id)
            
            # Performance Insights
            dashboard_data["performance_insights"] = self._get_performance_insights(user_id)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate performance dashboard: {str(e)}")
            raise
    
    def get_performance_analytics(self, user_id: int, portfolio_id: Optional[int] = None) -> Dict[str, Any]:
        """Get detailed performance analytics"""
        try:
            analytics_data = {
                "user_id": user_id,
                "portfolio_id": portfolio_id,
                "analytics_type": "detailed_performance",
                "generated_at": datetime.now().isoformat(),
                "return_analysis": {},
                "risk_analysis": {},
                "benchmark_analysis": {},
                "attribution_analysis": {},
                "trend_analysis": {},
                "efficiency_analysis": {}
            }
            
            if portfolio_id:
                # Single portfolio analysis
                analytics_data["return_analysis"] = self._analyze_single_portfolio_returns(portfolio_id, user_id)
                analytics_data["risk_analysis"] = self._analyze_single_portfolio_risk(portfolio_id, user_id)
                analytics_data["benchmark_analysis"] = self._analyze_single_portfolio_benchmarks(portfolio_id, user_id)
                analytics_data["attribution_analysis"] = self._analyze_single_portfolio_attribution(portfolio_id, user_id)
                analytics_data["trend_analysis"] = self._analyze_single_portfolio_trends(portfolio_id, user_id)
                analytics_data["efficiency_analysis"] = self._analyze_single_portfolio_efficiency(portfolio_id, user_id)
            else:
                # All portfolios analysis
                analytics_data["return_analysis"] = self._analyze_all_portfolios_returns(user_id)
                analytics_data["risk_analysis"] = self._analyze_all_portfolios_risk(user_id)
                analytics_data["benchmark_analysis"] = self._analyze_all_portfolios_benchmarks(user_id)
                analytics_data["attribution_analysis"] = self._analyze_all_portfolios_attribution(user_id)
                analytics_data["trend_analysis"] = self._analyze_all_portfolios_trends(user_id)
                analytics_data["efficiency_analysis"] = self._analyze_all_portfolios_efficiency(user_id)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to generate performance analytics: {str(e)}")
            raise
    
    def get_performance_insights(self, user_id: int) -> Dict[str, Any]:
        """Get AI-powered performance insights"""
        try:
            insights_data = {
                "user_id": user_id,
                "insights_type": "performance_analytics",
                "generated_at": datetime.now().isoformat(),
                "performance_health_score": 0,
                "key_performance_insights": [],
                "performance_action_items": [],
                "performance_opportunities": [],
                "performance_warnings": []
            }
            
            # Get all user portfolios with performance data
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            performance_records = []
            
            for portfolio in portfolios:
                performance = self.performance_service.get_portfolio_performance(portfolio.id, user_id)
                if performance:
                    performance_records.append(performance)
            
            if not performance_records:
                return insights_data
            
            # Calculate performance health score
            insights_data["performance_health_score"] = self._calculate_performance_health_score(performance_records)
            
            # Generate insights
            insights_data["key_performance_insights"] = self._generate_key_performance_insights(performance_records)
            insights_data["performance_action_items"] = self._generate_performance_action_items(performance_records)
            insights_data["performance_opportunities"] = self._identify_performance_opportunities(performance_records)
            insights_data["performance_warnings"] = self._identify_performance_warnings(performance_records)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Failed to generate performance insights: {str(e)}")
            raise
    
    # Helper methods for dashboard components
    def _get_performance_overview(self, user_id: int) -> Dict[str, Any]:
        """Get performance overview for dashboard"""
        try:
            # Get all portfolios with performance data
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            
            overview_data = {
                "total_portfolios": len(portfolios),
                "portfolios_with_performance": 0,
                "total_portfolio_value": 0,
                "total_invested_amount": 0,
                "total_absolute_return": 0,
                "weighted_average_return": 0,
                "best_performing_portfolio": None,
                "worst_performing_portfolio": None
            }
            
            performance_records = []
            total_value = 0
            weighted_returns = 0
            
            for portfolio in portfolios:
                performance = self.performance_service.get_portfolio_performance(portfolio.id, user_id)
                if performance:
                    performance_records.append({
                        "portfolio_id": portfolio.id,
                        "portfolio_name": portfolio.name,
                        "performance": performance
                    })
                    
                    total_value += performance.portfolio_value
                    weighted_returns += performance.absolute_return_percentage * performance.portfolio_value
            
            overview_data["portfolios_with_performance"] = len(performance_records)
            
            if performance_records:
                overview_data["total_portfolio_value"] = sum(p["performance"].portfolio_value for p in performance_records)
                overview_data["total_invested_amount"] = sum(p["performance"].invested_amount for p in performance_records)
                overview_data["total_absolute_return"] = overview_data["total_portfolio_value"] - overview_data["total_invested_amount"]
                overview_data["weighted_average_return"] = (weighted_returns / total_value) if total_value > 0 else 0
                
                # Find best and worst performers
                best_performer = max(performance_records, key=lambda p: p["performance"].absolute_return_percentage)
                worst_performer = min(performance_records, key=lambda p: p["performance"].absolute_return_percentage)
                
                overview_data["best_performing_portfolio"] = {
                    "portfolio_id": best_performer["portfolio_id"],
                    "portfolio_name": best_performer["portfolio_name"],
                    "return_percentage": best_performer["performance"].absolute_return_percentage
                }
                
                overview_data["worst_performing_portfolio"] = {
                    "portfolio_id": worst_performer["portfolio_id"],
                    "portfolio_name": worst_performer["portfolio_name"],
                    "return_percentage": worst_performer["performance"].absolute_return_percentage
                }
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Failed to get performance overview: {str(e)}")
            return {}
    
    def _get_portfolio_performance_summary(self, user_id: int) -> Dict[str, Any]:
        """Get portfolio performance summary"""
        try:
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            
            portfolio_summaries = []
            
            for portfolio in portfolios:
                performance = self.performance_service.get_portfolio_performance(portfolio.id, user_id)
                
                if performance:
                    portfolio_summaries.append({
                        "portfolio_id": portfolio.id,
                        "portfolio_name": portfolio.name,
                        "portfolio_value": performance.portfolio_value,
                        "invested_amount": performance.invested_amount,
                        "absolute_return": performance.absolute_return,
                        "absolute_return_percentage": performance.absolute_return_percentage,
                        "annualized_return": performance.annualized_return,
                        "annualized_volatility": performance.annualized_volatility,
                        "sharpe_ratio": performance.sharpe_ratio,
                        "maximum_drawdown": performance.maximum_drawdown,
                        "benchmark_return": performance.benchmark_return,
                        "excess_return": performance.excess_return,
                        "outperformance": performance.outperformance,
                        "holdings_count": performance.holdings_count,
                        "concentration_ratio": performance.concentration_ratio,
                        "performance_date": performance.performance_date.isoformat()
                    })
            
            return {
                "portfolio_summaries": portfolio_summaries,
                "portfolios_count": len(portfolio_summaries)
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio performance summary: {str(e)}")
            return {}
    
    def _get_benchmark_comparison_summary(self, user_id: int) -> Dict[str, Any]:
        """Get benchmark comparison summary"""
        try:
            # Get all performance records for user
            performance_records = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.user_id == user_id
            ).all()
            
            if not performance_records:
                return {"total_comparisons": 0}
            
            # Get benchmark comparisons
            benchmark_comparisons = []
            for performance in performance_records:
                comparisons = self.performance_service.get_benchmark_comparisons(performance.id)
                benchmark_comparisons.extend(comparisons)
            
            if not benchmark_comparisons:
                return {"total_comparisons": 0}
            
            # Analyze benchmark performance
            outperforming_count = len([c for c in benchmark_comparisons if c.excess_return > 0])
            underperforming_count = len([c for c in benchmark_comparisons if c.excess_return < 0])
            
            avg_excess_return = sum(c.excess_return for c in benchmark_comparisons) / len(benchmark_comparisons)
            avg_tracking_error = sum(c.tracking_error or 0 for c in benchmark_comparisons) / len(benchmark_comparisons)
            avg_information_ratio = sum(c.information_ratio or 0 for c in benchmark_comparisons) / len(benchmark_comparisons)
            
            return {
                "total_comparisons": len(benchmark_comparisons),
                "outperforming_count": outperforming_count,
                "underperforming_count": underperforming_count,
                "outperformance_rate": (outperforming_count / len(benchmark_comparisons)) * 100,
                "average_excess_return": avg_excess_return,
                "average_tracking_error": avg_tracking_error,
                "average_information_ratio": avg_information_ratio,
                "benchmark_types": list(set(c.benchmark_type.value for c in benchmark_comparisons))
            }
            
        except Exception as e:
            logger.error(f"Failed to get benchmark comparison summary: {str(e)}")
            return {}
    
    def _get_attribution_summary(self, user_id: int) -> Dict[str, Any]:
        """Get attribution analysis summary"""
        try:
            # Get all performance records for user
            performance_records = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.user_id == user_id
            ).all()
            
            if not performance_records:
                return {"total_attributions": 0}
            
            # Get attribution analyses
            attribution_analyses = []
            for performance in performance_records:
                attributions = self.performance_service.get_attribution_analysis(performance.id)
                attribution_analyses.extend(attributions)
            
            if not attribution_analyses:
                return {"total_attributions": 0}
            
            # Analyze attribution
            total_allocation_effect = sum(a.allocation_effect or 0 for a in attribution_analyses)
            total_selection_effect = sum(a.selection_effect or 0 for a in attribution_analyses)
            total_interaction_effect = sum(a.interaction_effect or 0 for a in attribution_analyses)
            
            # Group by attribution type
            attribution_by_type = {}
            for attribution in attribution_analyses:
                attr_type = attribution.attribution_type.value
                if attr_type not in attribution_by_type:
                    attribution_by_type[attr_type] = 0
                attribution_by_type[attr_type] += attribution.attribution_return
            
            return {
                "total_attributions": len(attribution_analyses),
                "total_allocation_effect": total_allocation_effect,
                "total_selection_effect": total_selection_effect,
                "total_interaction_effect": total_interaction_effect,
                "attribution_by_type": attribution_by_type,
                "dominant_effect": max(
                    [("allocation", total_allocation_effect), 
                     ("selection", total_selection_effect), 
                     ("interaction", total_interaction_effect)],
                    key=lambda x: abs(x[1])
                )[0]
            }
            
        except Exception as e:
            logger.error(f"Failed to get attribution summary: {str(e)}")
            return {}
    
    def _get_risk_metrics_summary(self, user_id: int) -> Dict[str, Any]:
        """Get risk metrics summary"""
        try:
            # Get all performance records for user
            performance_records = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.user_id == user_id
            ).all()
            
            if not performance_records:
                return {"total_portfolios": 0}
            
            # Calculate aggregate risk metrics
            sharpe_ratios = [p.sharpe_ratio for p in performance_records if p.sharpe_ratio is not None]
            volatilities = [p.annualized_volatility for p in performance_records if p.annualized_volatility is not None]
            max_drawdowns = [p.maximum_drawdown for p in performance_records if p.maximum_drawdown is not None]
            
            return {
                "total_portfolios": len(performance_records),
                "average_sharpe_ratio": sum(sharpe_ratios) / len(sharpe_ratios) if sharpe_ratios else 0,
                "average_volatility": sum(volatilities) / len(volatilities) if volatilities else 0,
                "average_max_drawdown": sum(max_drawdowns) / len(max_drawdowns) if max_drawdowns else 0,
                "high_risk_portfolios": len([p for p in performance_records if (p.annualized_volatility or 0) > 0.25]),
                "low_sharpe_portfolios": len([p for p in performance_records if (p.sharpe_ratio or 0) < 0.5]),
                "high_drawdown_portfolios": len([p for p in performance_records if (p.maximum_drawdown or 0) < -0.2])
            }
            
        except Exception as e:
            logger.error(f"Failed to get risk metrics summary: {str(e)}")
            return {}
    
    def _get_alerts_summary(self, user_id: int) -> Dict[str, Any]:
        """Get performance alerts summary"""
        try:
            # Get all performance alerts for user
            all_alerts = self.db.query(PerformanceAlert).filter(
                PerformanceAlert.user_id == user_id
            ).all()
            
            active_alerts = [a for a in all_alerts if not a.is_read]
            
            # Categorize by severity
            alert_severity = {}
            for alert in active_alerts:
                severity = alert.severity
                alert_severity[severity] = alert_severity.get(severity, 0) + 1
            
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
                "alert_severity": alert_severity,
                "alert_types": alert_types,
                "critical_alerts": len([a for a in active_alerts if a.severity == "critical"]),
                "unacknowledged_alerts": len([a for a in active_alerts if not a.is_acknowledged])
            }
            
        except Exception as e:
            logger.error(f"Failed to get alerts summary: {str(e)}")
            return {}
    
    def _get_performance_insights(self, user_id: int) -> List[str]:
        """Get performance insights"""
        try:
            insights = []
            
            # Get performance records
            performance_records = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.user_id == user_id
            ).all()
            
            if not performance_records:
                return insights
            
            # Generate insights based on performance data
            avg_return = sum(p.absolute_return_percentage for p in performance_records) / len(performance_records)
            avg_sharpe = sum(p.sharpe_ratio or 0 for p in performance_records) / len(performance_records)
            
            if avg_return > 15:
                insights.append(f"Strong portfolio performance with average returns of {avg_return:.1f}%")
            elif avg_return < 5:
                insights.append(f"Portfolio returns are below expectations at {avg_return:.1f}%")
            
            if avg_sharpe > 1.0:
                insights.append(f"Excellent risk-adjusted returns with average Sharpe ratio of {avg_sharpe:.2f}")
            elif avg_sharpe < 0.5:
                insights.append(f"Risk-adjusted returns need improvement (Sharpe ratio: {avg_sharpe:.2f})")
            
            # Outperformance insights
            outperforming_portfolios = len([p for p in performance_records if p.outperformance])
            if outperforming_portfolios > len(performance_records) / 2:
                insights.append(f"{outperforming_portfolios} out of {len(performance_records)} portfolios are outperforming benchmarks")
            
            return insights[:5]  # Limit to 5 insights
            
        except Exception as e:
            logger.error(f"Failed to get performance insights: {str(e)}")
            return []

    # Helper methods for insights
    def _calculate_performance_health_score(self, performance_records: List[PortfolioPerformance]) -> float:
        """Calculate overall performance health score"""
        try:
            if not performance_records:
                return 0

            score = 0
            max_score = 100

            # Returns component (40 points)
            avg_return = sum(p.absolute_return_percentage for p in performance_records) / len(performance_records)
            if avg_return > 20:
                score += 40
            elif avg_return > 10:
                score += 30
            elif avg_return > 5:
                score += 20
            elif avg_return > 0:
                score += 10

            # Risk-adjusted returns component (30 points)
            sharpe_ratios = [p.sharpe_ratio for p in performance_records if p.sharpe_ratio is not None]
            if sharpe_ratios:
                avg_sharpe = sum(sharpe_ratios) / len(sharpe_ratios)
                if avg_sharpe > 1.5:
                    score += 30
                elif avg_sharpe > 1.0:
                    score += 25
                elif avg_sharpe > 0.5:
                    score += 15
                elif avg_sharpe > 0:
                    score += 5

            # Benchmark outperformance component (20 points)
            outperforming_count = len([p for p in performance_records if p.outperformance])
            outperformance_rate = outperforming_count / len(performance_records)
            score += outperformance_rate * 20

            # Risk management component (10 points)
            max_drawdowns = [p.maximum_drawdown for p in performance_records if p.maximum_drawdown is not None]
            if max_drawdowns:
                avg_drawdown = sum(max_drawdowns) / len(max_drawdowns)
                if avg_drawdown > -0.1:  # Less than 10% drawdown
                    score += 10
                elif avg_drawdown > -0.2:  # Less than 20% drawdown
                    score += 7
                elif avg_drawdown > -0.3:  # Less than 30% drawdown
                    score += 4

            return min(max_score, max(0, score))

        except Exception as e:
            logger.error(f"Failed to calculate performance health score: {str(e)}")
            return 50.0

    def _generate_key_performance_insights(self, performance_records: List[PortfolioPerformance]) -> List[str]:
        """Generate key performance insights"""
        try:
            insights = []

            if not performance_records:
                return insights

            # Overall performance insight
            avg_return = sum(p.absolute_return_percentage for p in performance_records) / len(performance_records)
            total_value = sum(p.portfolio_value for p in performance_records)
            insights.append(f"Portfolio performance averages {avg_return:.1f}% across {len(performance_records)} portfolios worth ₹{total_value:,.0f}")

            # Risk-adjusted performance insight
            sharpe_ratios = [p.sharpe_ratio for p in performance_records if p.sharpe_ratio is not None]
            if sharpe_ratios:
                avg_sharpe = sum(sharpe_ratios) / len(sharpe_ratios)
                if avg_sharpe > 1.0:
                    insights.append(f"Excellent risk-adjusted returns with average Sharpe ratio of {avg_sharpe:.2f}")
                elif avg_sharpe < 0.5:
                    insights.append(f"Risk-adjusted returns below optimal level (Sharpe ratio: {avg_sharpe:.2f})")

            # Benchmark comparison insight
            outperforming_count = len([p for p in performance_records if p.outperformance])
            outperformance_rate = (outperforming_count / len(performance_records)) * 100
            insights.append(f"{outperformance_rate:.0f}% of portfolios are outperforming their benchmarks")

            # Volatility insight
            volatilities = [p.annualized_volatility for p in performance_records if p.annualized_volatility is not None]
            if volatilities:
                avg_volatility = sum(volatilities) / len(volatilities)
                if avg_volatility > 0.25:
                    insights.append(f"High portfolio volatility detected ({avg_volatility:.1%} average)")
                elif avg_volatility < 0.15:
                    insights.append(f"Conservative portfolio positioning with low volatility ({avg_volatility:.1%})")

            # Drawdown insight
            max_drawdowns = [p.maximum_drawdown for p in performance_records if p.maximum_drawdown is not None]
            if max_drawdowns:
                avg_drawdown = sum(max_drawdowns) / len(max_drawdowns)
                if avg_drawdown < -0.2:
                    insights.append(f"Significant drawdowns experienced (average: {avg_drawdown:.1%})")
                elif avg_drawdown > -0.1:
                    insights.append(f"Good downside protection with limited drawdowns ({avg_drawdown:.1%})")

            return insights[:5]  # Limit to 5 insights

        except Exception as e:
            logger.error(f"Failed to generate key performance insights: {str(e)}")
            return []

    def _generate_performance_action_items(self, performance_records: List[PortfolioPerformance]) -> List[str]:
        """Generate performance action items"""
        try:
            action_items = []

            for performance in performance_records:
                portfolio_name = f"Portfolio {performance.portfolio_id}"

                # Low Sharpe ratio actions
                if performance.sharpe_ratio and performance.sharpe_ratio < 0.5:
                    action_items.append(f"Improve risk-adjusted returns for {portfolio_name} (Sharpe ratio: {performance.sharpe_ratio:.2f})")

                # High drawdown actions
                if performance.maximum_drawdown and performance.maximum_drawdown < -0.25:
                    action_items.append(f"Review risk management for {portfolio_name} due to high drawdown ({performance.maximum_drawdown:.1%})")

                # Underperformance actions
                if performance.excess_return and performance.excess_return < -5:
                    action_items.append(f"Address underperformance in {portfolio_name} ({performance.excess_return:.1f}% vs benchmark)")

                # High concentration actions
                if performance.concentration_ratio and performance.concentration_ratio > 0.6:
                    action_items.append(f"Reduce concentration risk in {portfolio_name} (top 5 holdings: {performance.concentration_ratio:.1%})")

            # General actions if no specific issues
            if not action_items:
                action_items.extend([
                    "Continue monitoring portfolio performance regularly",
                    "Consider quarterly performance review and rebalancing",
                    "Evaluate benchmark appropriateness for portfolios"
                ])

            return action_items[:5]  # Limit to 5 action items

        except Exception as e:
            logger.error(f"Failed to generate performance action items: {str(e)}")
            return []

    def _identify_performance_opportunities(self, performance_records: List[PortfolioPerformance]) -> List[str]:
        """Identify performance optimization opportunities"""
        try:
            opportunities = []

            for performance in performance_records:
                portfolio_name = f"Portfolio {performance.portfolio_id}"

                # High Sharpe ratio opportunity
                if performance.sharpe_ratio and performance.sharpe_ratio > 1.5:
                    opportunities.append(f"{portfolio_name} shows excellent risk-adjusted returns - consider scaling strategy")

                # Low volatility with good returns
                if (performance.annualized_volatility and performance.annualized_volatility < 0.15 and
                    performance.absolute_return_percentage > 10):
                    opportunities.append(f"{portfolio_name} has low-risk high-return profile - potential for increased allocation")

                # Consistent outperformance
                if performance.outperformance and performance.excess_return and performance.excess_return > 5:
                    opportunities.append(f"{portfolio_name} consistently outperforms benchmark by {performance.excess_return:.1f}%")

                # Good diversification
                if (performance.concentration_ratio and performance.concentration_ratio < 0.4 and
                    performance.holdings_count and performance.holdings_count > 15):
                    opportunities.append(f"{portfolio_name} has good diversification - maintain current approach")

            return opportunities[:5]  # Limit to 5 opportunities

        except Exception as e:
            logger.error(f"Failed to identify performance opportunities: {str(e)}")
            return []

    def _identify_performance_warnings(self, performance_records: List[PortfolioPerformance]) -> List[str]:
        """Identify performance warnings"""
        try:
            warnings = []

            for performance in performance_records:
                portfolio_name = f"Portfolio {performance.portfolio_id}"

                # Negative returns warning
                if performance.absolute_return_percentage < -10:
                    warnings.append(f"{portfolio_name} has significant losses ({performance.absolute_return_percentage:.1f}%)")

                # High volatility warning
                if performance.annualized_volatility and performance.annualized_volatility > 0.35:
                    warnings.append(f"{portfolio_name} has very high volatility ({performance.annualized_volatility:.1%})")

                # Large drawdown warning
                if performance.maximum_drawdown and performance.maximum_drawdown < -0.3:
                    warnings.append(f"{portfolio_name} experienced large drawdown ({performance.maximum_drawdown:.1%})")

                # Poor risk-adjusted returns
                if performance.sharpe_ratio and performance.sharpe_ratio < 0:
                    warnings.append(f"{portfolio_name} has negative risk-adjusted returns (Sharpe: {performance.sharpe_ratio:.2f})")

                # Extreme concentration
                if performance.concentration_ratio and performance.concentration_ratio > 0.8:
                    warnings.append(f"{portfolio_name} is highly concentrated ({performance.concentration_ratio:.1%} in top 5 holdings)")

            return warnings[:5]  # Limit to 5 warnings

        except Exception as e:
            logger.error(f"Failed to identify performance warnings: {str(e)}")
            return []

    # Placeholder methods for detailed analytics (would be implemented based on specific requirements)
    def _analyze_single_portfolio_returns(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze returns for single portfolio"""
        return {"analysis": "single_portfolio_returns", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_risk(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze risk for single portfolio"""
        return {"analysis": "single_portfolio_risk", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_benchmarks(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze benchmarks for single portfolio"""
        return {"analysis": "single_portfolio_benchmarks", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_attribution(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze attribution for single portfolio"""
        return {"analysis": "single_portfolio_attribution", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_trends(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze trends for single portfolio"""
        return {"analysis": "single_portfolio_trends", "portfolio_id": portfolio_id}

    def _analyze_single_portfolio_efficiency(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze efficiency for single portfolio"""
        return {"analysis": "single_portfolio_efficiency", "portfolio_id": portfolio_id}

    def _analyze_all_portfolios_returns(self, user_id: int) -> Dict[str, Any]:
        """Analyze returns for all portfolios"""
        return {"analysis": "all_portfolios_returns", "user_id": user_id}

    def _analyze_all_portfolios_risk(self, user_id: int) -> Dict[str, Any]:
        """Analyze risk for all portfolios"""
        return {"analysis": "all_portfolios_risk", "user_id": user_id}

    def _analyze_all_portfolios_benchmarks(self, user_id: int) -> Dict[str, Any]:
        """Analyze benchmarks for all portfolios"""
        return {"analysis": "all_portfolios_benchmarks", "user_id": user_id}

    def _analyze_all_portfolios_attribution(self, user_id: int) -> Dict[str, Any]:
        """Analyze attribution for all portfolios"""
        return {"analysis": "all_portfolios_attribution", "user_id": user_id}

    def _analyze_all_portfolios_trends(self, user_id: int) -> Dict[str, Any]:
        """Analyze trends for all portfolios"""
        return {"analysis": "all_portfolios_trends", "user_id": user_id}

    def _analyze_all_portfolios_efficiency(self, user_id: int) -> Dict[str, Any]:
        """Analyze efficiency for all portfolios"""
        return {"analysis": "all_portfolios_efficiency", "user_id": user_id}
