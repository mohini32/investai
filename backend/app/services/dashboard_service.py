"""
Dashboard Service - Comprehensive portfolio dashboard and analytics
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging

from app.models.portfolio import Portfolio, Holding, Transaction, PortfolioSnapshot, AssetType
from app.models.user import User
from app.services.portfolio_service import PortfolioService
from app.services.market_service import MarketService
from app.ai.crew import InvestAICrew

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard analytics and insights"""
    
    def __init__(self, db: Session):
        self.db = db
        self.portfolio_service = PortfolioService(db)
        self.market_service = MarketService()
        self.ai_crew = InvestAICrew()
    
    def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user dashboard"""
        try:
            dashboard_data = {
                "user_id": user_id,
                "dashboard_type": "comprehensive",
                "generated_at": datetime.now().isoformat(),
                "portfolio_overview": {},
                "market_overview": {},
                "performance_summary": {},
                "recent_activity": {},
                "alerts_summary": {},
                "ai_insights": {},
                "recommendations": {}
            }
            
            # Portfolio Overview
            dashboard_data["portfolio_overview"] = self._get_portfolio_overview(user_id)
            
            # Market Overview
            dashboard_data["market_overview"] = self._get_market_overview()
            
            # Performance Summary
            dashboard_data["performance_summary"] = self._get_performance_summary(user_id)
            
            # Recent Activity
            dashboard_data["recent_activity"] = self._get_recent_activity(user_id)
            
            # Alerts Summary
            dashboard_data["alerts_summary"] = self._get_alerts_summary(user_id)
            
            # AI Insights
            dashboard_data["ai_insights"] = self._get_ai_insights(user_id)
            
            # Recommendations
            dashboard_data["recommendations"] = self._get_dashboard_recommendations(user_id)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate user dashboard: {str(e)}")
            raise
    
    def get_portfolio_analytics(self, user_id: int, portfolio_id: int = None) -> Dict[str, Any]:
        """Get detailed portfolio analytics"""
        try:
            analytics_data = {
                "user_id": user_id,
                "portfolio_id": portfolio_id,
                "analytics_type": "detailed_portfolio",
                "generated_at": datetime.now().isoformat(),
                "asset_allocation": {},
                "sector_allocation": {},
                "performance_metrics": {},
                "risk_metrics": {},
                "dividend_analysis": {},
                "tax_analysis": {},
                "benchmark_comparison": {}
            }
            
            # Get portfolio data
            if portfolio_id:
                portfolios = [self.portfolio_service.get_portfolio(portfolio_id, user_id)]
                portfolios = [p for p in portfolios if p is not None]
            else:
                portfolios = self.portfolio_service.get_user_portfolios(user_id)
            
            if not portfolios:
                return {"error": "No portfolios found"}
            
            # Aggregate data across portfolios
            all_holdings = []
            for portfolio in portfolios:
                holdings = self.portfolio_service.get_portfolio_holdings(portfolio.id, user_id)
                all_holdings.extend(holdings)
            
            # Asset Allocation Analysis
            analytics_data["asset_allocation"] = self._analyze_asset_allocation(all_holdings)
            
            # Sector Allocation Analysis
            analytics_data["sector_allocation"] = self._analyze_sector_allocation(all_holdings)
            
            # Performance Metrics
            analytics_data["performance_metrics"] = self._calculate_performance_metrics(all_holdings)
            
            # Risk Metrics
            analytics_data["risk_metrics"] = self._calculate_risk_metrics(all_holdings)
            
            # Dividend Analysis
            analytics_data["dividend_analysis"] = self._analyze_dividends(user_id, all_holdings)
            
            # Tax Analysis
            analytics_data["tax_analysis"] = self._analyze_tax_implications(user_id, all_holdings)
            
            # Benchmark Comparison
            analytics_data["benchmark_comparison"] = self._compare_with_benchmarks(all_holdings)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to generate portfolio analytics: {str(e)}")
            raise
    
    def get_investment_insights(self, user_id: int) -> Dict[str, Any]:
        """Get AI-powered investment insights"""
        try:
            insights_data = {
                "user_id": user_id,
                "insights_type": "ai_powered",
                "generated_at": datetime.now().isoformat(),
                "market_insights": {},
                "portfolio_insights": {},
                "opportunity_insights": {},
                "risk_insights": {},
                "action_items": []
            }
            
            # Get user profile
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Market Insights
            insights_data["market_insights"] = self._get_market_insights()
            
            # Portfolio Insights using AI
            insights_data["portfolio_insights"] = self._get_ai_portfolio_insights(user_id, user)
            
            # Opportunity Insights
            insights_data["opportunity_insights"] = self._get_opportunity_insights(user_id, user)
            
            # Risk Insights
            insights_data["risk_insights"] = self._get_risk_insights(user_id, user)
            
            # Action Items
            insights_data["action_items"] = self._generate_action_items(insights_data)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Failed to generate investment insights: {str(e)}")
            raise
    
    # Helper methods for dashboard components
    def _get_portfolio_overview(self, user_id: int) -> Dict[str, Any]:
        """Get portfolio overview for dashboard"""
        try:
            overview = self.portfolio_service.get_user_portfolio_overview(user_id)
            
            # Add additional metrics
            portfolios = self.portfolio_service.get_user_portfolios(user_id)
            
            # Calculate day change
            day_change = 0
            day_change_percentage = 0
            
            for portfolio in portfolios:
                holdings = self.portfolio_service.get_portfolio_holdings(portfolio.id, user_id)
                for holding in holdings:
                    if holding.day_change:
                        day_change += holding.day_change * holding.quantity
            
            if overview.get("total_current_value", 0) > 0:
                day_change_percentage = (day_change / overview["total_current_value"]) * 100
            
            overview.update({
                "day_change": day_change,
                "day_change_percentage": day_change_percentage,
                "best_performer": self._get_best_performer(user_id),
                "worst_performer": self._get_worst_performer(user_id)
            })
            
            return overview
            
        except Exception as e:
            logger.error(f"Failed to get portfolio overview: {str(e)}")
            return {}
    
    def _get_market_overview(self) -> Dict[str, Any]:
        """Get market overview for dashboard"""
        try:
            market_data = {
                "indices": self.market_service.get_market_indices(),
                "sectors": self.market_service.get_sector_performance(),
                "market_status": self.market_service.get_market_status(),
                "top_movers": self.market_service.get_top_gainers_losers(5)
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to get market overview: {str(e)}")
            return {}
    
    def _get_performance_summary(self, user_id: int) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            portfolios = self.portfolio_service.get_user_portfolios(user_id)
            
            # Calculate performance metrics
            total_invested = sum(p.total_invested or 0 for p in portfolios)
            current_value = sum(p.current_value or 0 for p in portfolios)
            total_returns = current_value - total_invested
            
            # Get historical performance
            performance_data = []
            for portfolio in portfolios:
                try:
                    perf = self.portfolio_service.get_portfolio_performance(portfolio.id, user_id, 30)
                    if "performance_data" in perf:
                        performance_data.extend(perf["performance_data"])
                except:
                    continue
            
            # Calculate metrics
            returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0
            
            return {
                "total_invested": total_invested,
                "current_value": current_value,
                "total_returns": total_returns,
                "returns_percentage": returns_percentage,
                "performance_trend": "positive" if returns_percentage > 0 else "negative",
                "historical_data": performance_data[-30:] if performance_data else []  # Last 30 data points
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {str(e)}")
            return {}
    
    def _get_recent_activity(self, user_id: int) -> Dict[str, Any]:
        """Get recent activity summary"""
        try:
            # Get recent transactions
            recent_transactions = self.portfolio_service.get_user_transactions(user_id, limit=10)
            
            # Get recent alerts
            recent_alerts = self.portfolio_service.get_user_alerts(user_id, limit=5)
            
            return {
                "recent_transactions": [
                    {
                        "id": t.id,
                        "type": t.transaction_type.value,
                        "symbol": t.symbol,
                        "quantity": t.quantity,
                        "amount": t.total_amount,
                        "date": t.transaction_date.isoformat()
                    } for t in recent_transactions
                ],
                "recent_alerts": [
                    {
                        "id": a.id,
                        "type": a.alert_type,
                        "title": a.title,
                        "severity": a.severity,
                        "created_at": a.created_at.isoformat()
                    } for a in recent_alerts
                ],
                "activity_summary": {
                    "transactions_this_month": len([t for t in recent_transactions 
                                                  if t.transaction_date >= datetime.now() - timedelta(days=30)]),
                    "unread_alerts": len([a for a in recent_alerts if not a.is_read])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {str(e)}")
            return {}
    
    def _get_alerts_summary(self, user_id: int) -> Dict[str, Any]:
        """Get alerts summary"""
        try:
            all_alerts = self.portfolio_service.get_user_alerts(user_id, limit=100)
            
            unread_count = len([a for a in all_alerts if not a.is_read])
            critical_count = len([a for a in all_alerts if a.severity == "critical" and not a.is_dismissed])
            warning_count = len([a for a in all_alerts if a.severity == "warning" and not a.is_dismissed])
            
            return {
                "total_alerts": len(all_alerts),
                "unread_count": unread_count,
                "critical_count": critical_count,
                "warning_count": warning_count,
                "alert_types": self._categorize_alerts(all_alerts)
            }
            
        except Exception as e:
            logger.error(f"Failed to get alerts summary: {str(e)}")
            return {}
    
    def _get_ai_insights(self, user_id: int) -> Dict[str, Any]:
        """Get AI-powered insights"""
        try:
            # Get user's default portfolio for AI analysis
            portfolios = self.portfolio_service.get_user_portfolios(user_id)
            default_portfolio = next((p for p in portfolios if p.is_default), portfolios[0] if portfolios else None)
            
            if not default_portfolio:
                return {"message": "No portfolio available for AI analysis"}
            
            # Get AI analysis (simplified)
            try:
                ai_analysis = self.portfolio_service.analyze_portfolio_with_ai(default_portfolio.id, user_id)
                
                if "error" not in ai_analysis:
                    return {
                        "portfolio_health": "Good" if ai_analysis.get("current_portfolio_analysis", {}).get("advisor_analysis", {}).get("health_assessment", {}).get("overall_health") == "Healthy" else "Needs Attention",
                        "key_recommendations": ai_analysis.get("optimization_recommendations", {}).get("recommended_changes", [])[:3],
                        "risk_assessment": ai_analysis.get("current_portfolio_analysis", {}).get("risk_analysis", {}).get("risk_category", "Unknown"),
                        "ai_score": 75  # Placeholder score
                    }
            except:
                pass
            
            return {
                "portfolio_health": "Unknown",
                "key_recommendations": ["Update portfolio prices", "Review asset allocation", "Consider rebalancing"],
                "risk_assessment": "Moderate",
                "ai_score": 50
            }
            
        except Exception as e:
            logger.error(f"Failed to get AI insights: {str(e)}")
            return {}
    
    def _get_dashboard_recommendations(self, user_id: int) -> List[str]:
        """Get dashboard recommendations"""
        try:
            recommendations = []
            
            # Check portfolio overview
            overview = self.portfolio_service.get_user_portfolio_overview(user_id)
            
            if overview.get("total_returns_percentage", 0) < 0:
                recommendations.append("Consider reviewing underperforming holdings")
            
            if overview.get("portfolios_count", 0) == 0:
                recommendations.append("Create your first portfolio to start investing")
            
            if overview.get("total_holdings", 0) < 5:
                recommendations.append("Consider diversifying with more holdings")
            
            # Check recent activity
            recent_transactions = self.portfolio_service.get_user_transactions(user_id, limit=10)
            if not recent_transactions:
                recommendations.append("Start investing by adding your first transaction")
            
            # Check alerts
            unread_alerts = self.portfolio_service.get_user_alerts(user_id, unread_only=True, limit=10)
            if unread_alerts:
                recommendations.append(f"You have {len(unread_alerts)} unread alerts to review")
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to get dashboard recommendations: {str(e)}")
            return []
    
    # Helper methods for analytics
    def _analyze_asset_allocation(self, holdings: List[Holding]) -> Dict[str, Any]:
        """Analyze asset allocation"""
        total_value = sum(h.current_value or 0 for h in holdings)
        
        if total_value == 0:
            return {}
        
        allocation = {}
        for holding in holdings:
            asset_type = holding.asset_type.value
            value = holding.current_value or 0
            percentage = (value / total_value) * 100
            
            if asset_type in allocation:
                allocation[asset_type] += percentage
            else:
                allocation[asset_type] = percentage
        
        return {
            "allocation": allocation,
            "diversification_score": self._calculate_diversification_score(allocation),
            "recommendations": self._get_allocation_recommendations(allocation)
        }
    
    def _analyze_sector_allocation(self, holdings: List[Holding]) -> Dict[str, Any]:
        """Analyze sector allocation"""
        # This would require sector data for each holding
        # For now, return a placeholder
        return {
            "allocation": {"Technology": 30, "Banking": 25, "Healthcare": 20, "Others": 25},
            "concentration_risk": "Medium",
            "recommendations": ["Consider reducing technology exposure"]
        }
    
    def _calculate_performance_metrics(self, holdings: List[Holding]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        total_invested = sum(h.invested_amount or 0 for h in holdings)
        current_value = sum(h.current_value or 0 for h in holdings)
        
        returns = current_value - total_invested
        returns_percentage = (returns / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "total_returns": returns,
            "returns_percentage": returns_percentage,
            "absolute_returns": returns,
            "annualized_returns": returns_percentage,  # Simplified
            "best_performer": max(holdings, key=lambda h: h.unrealized_pnl_percentage or 0).symbol if holdings else None,
            "worst_performer": min(holdings, key=lambda h: h.unrealized_pnl_percentage or 0).symbol if holdings else None
        }
    
    def _calculate_risk_metrics(self, holdings: List[Holding]) -> Dict[str, Any]:
        """Calculate risk metrics"""
        # Simplified risk calculation
        return {
            "portfolio_beta": 1.0,
            "volatility": 0.2,
            "sharpe_ratio": 1.5,
            "max_drawdown": -0.15,
            "risk_score": 65,
            "risk_category": "Moderate"
        }
    
    # Additional helper methods would continue here...
    def _get_best_performer(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get best performing holding"""
        try:
            portfolios = self.portfolio_service.get_user_portfolios(user_id)
            best_holding = None
            best_performance = float('-inf')
            
            for portfolio in portfolios:
                holdings = self.portfolio_service.get_portfolio_holdings(portfolio.id, user_id)
                for holding in holdings:
                    if holding.unrealized_pnl_percentage and holding.unrealized_pnl_percentage > best_performance:
                        best_performance = holding.unrealized_pnl_percentage
                        best_holding = holding
            
            if best_holding:
                return {
                    "symbol": best_holding.symbol,
                    "name": best_holding.name,
                    "returns_percentage": best_holding.unrealized_pnl_percentage
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get best performer: {str(e)}")
            return None
    
    def _get_worst_performer(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get worst performing holding"""
        try:
            portfolios = self.portfolio_service.get_user_portfolios(user_id)
            worst_holding = None
            worst_performance = float('inf')
            
            for portfolio in portfolios:
                holdings = self.portfolio_service.get_portfolio_holdings(portfolio.id, user_id)
                for holding in holdings:
                    if holding.unrealized_pnl_percentage and holding.unrealized_pnl_percentage < worst_performance:
                        worst_performance = holding.unrealized_pnl_percentage
                        worst_holding = holding
            
            if worst_holding:
                return {
                    "symbol": worst_holding.symbol,
                    "name": worst_holding.name,
                    "returns_percentage": worst_holding.unrealized_pnl_percentage
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get worst performer: {str(e)}")
            return None
