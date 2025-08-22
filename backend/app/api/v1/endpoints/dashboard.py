"""
Dashboard endpoints - Comprehensive portfolio dashboard and analytics
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_user_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive user dashboard"""
    try:
        dashboard_service = DashboardService(db)
        dashboard_data = dashboard_service.get_user_dashboard(current_user.id)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "message": "Dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_portfolio_analytics(
    portfolio_id: Optional[int] = Query(None, description="Specific portfolio ID (optional)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed portfolio analytics"""
    try:
        dashboard_service = DashboardService(db)
        analytics_data = dashboard_service.get_portfolio_analytics(
            current_user.id, portfolio_id
        )
        
        if "error" in analytics_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analytics_data["error"]
            )
        
        return {
            "status": "success",
            "data": analytics_data,
            "message": "Portfolio analytics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio analytics: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_investment_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered investment insights"""
    try:
        dashboard_service = DashboardService(db)
        insights_data = dashboard_service.get_investment_insights(current_user.id)
        
        if "error" in insights_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=insights_data["error"]
            )
        
        return {
            "status": "success",
            "data": insights_data,
            "message": "Investment insights retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get investment insights: {str(e)}"
        )


@router.get("/summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get quick dashboard summary"""
    try:
        dashboard_service = DashboardService(db)
        
        # Get essential dashboard components
        portfolio_overview = dashboard_service._get_portfolio_overview(current_user.id)
        performance_summary = dashboard_service._get_performance_summary(current_user.id)
        alerts_summary = dashboard_service._get_alerts_summary(current_user.id)
        
        summary_data = {
            "user_id": current_user.id,
            "summary_type": "quick_dashboard",
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "portfolio_overview": portfolio_overview,
            "performance_summary": performance_summary,
            "alerts_summary": alerts_summary,
            "quick_stats": {
                "total_portfolios": portfolio_overview.get("portfolios_count", 0),
                "total_value": portfolio_overview.get("total_current_value", 0),
                "total_returns": portfolio_overview.get("total_returns", 0),
                "returns_percentage": portfolio_overview.get("total_returns_percentage", 0),
                "unread_alerts": alerts_summary.get("unread_count", 0)
            }
        }
        
        return {
            "status": "success",
            "data": summary_data,
            "message": "Dashboard summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_dashboard(
    period_days: int = Query(30, ge=1, le=365, description="Performance period in days"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get performance-focused dashboard"""
    try:
        dashboard_service = DashboardService(db)
        
        # Get performance data
        performance_data = {
            "user_id": current_user.id,
            "dashboard_type": "performance_focused",
            "period_days": period_days,
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "overall_performance": dashboard_service._get_performance_summary(current_user.id),
            "portfolio_comparison": {},
            "benchmark_comparison": {},
            "performance_attribution": {}
        }
        
        # Get individual portfolio performance
        portfolios = dashboard_service.portfolio_service.get_user_portfolios(current_user.id)
        portfolio_performance = []
        
        for portfolio in portfolios:
            try:
                perf = dashboard_service.portfolio_service.get_portfolio_performance(
                    portfolio.id, current_user.id, period_days
                )
                portfolio_performance.append({
                    "portfolio_id": portfolio.id,
                    "portfolio_name": portfolio.name,
                    "performance": perf
                })
            except:
                continue
        
        performance_data["portfolio_comparison"] = portfolio_performance
        
        return {
            "status": "success",
            "data": performance_data,
            "message": f"Performance dashboard for {period_days} days retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance dashboard: {str(e)}"
        )


@router.get("/risk", response_model=Dict[str, Any])
async def get_risk_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk-focused dashboard"""
    try:
        dashboard_service = DashboardService(db)
        
        # Get all user holdings for risk analysis
        portfolios = dashboard_service.portfolio_service.get_user_portfolios(current_user.id)
        all_holdings = []
        
        for portfolio in portfolios:
            holdings = dashboard_service.portfolio_service.get_portfolio_holdings(
                portfolio.id, current_user.id
            )
            all_holdings.extend(holdings)
        
        risk_data = {
            "user_id": current_user.id,
            "dashboard_type": "risk_focused",
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "risk_metrics": dashboard_service._calculate_risk_metrics(all_holdings),
            "asset_allocation": dashboard_service._analyze_asset_allocation(all_holdings),
            "sector_allocation": dashboard_service._analyze_sector_allocation(all_holdings),
            "concentration_analysis": {},
            "risk_recommendations": []
        }
        
        # Calculate concentration risk
        total_value = sum(h.current_value or 0 for h in all_holdings)
        if total_value > 0:
            concentration_data = []
            for holding in all_holdings:
                weight = (holding.current_value or 0) / total_value * 100
                concentration_data.append({
                    "symbol": holding.symbol,
                    "weight_percentage": weight,
                    "risk_contribution": weight * 1.2  # Simplified risk contribution
                })
            
            # Sort by weight
            concentration_data.sort(key=lambda x: x["weight_percentage"], reverse=True)
            risk_data["concentration_analysis"] = {
                "top_holdings": concentration_data[:10],
                "concentration_score": sum(h["weight_percentage"]**2 for h in concentration_data),
                "diversification_level": "Good" if len(all_holdings) >= 10 else "Needs Improvement"
            }
        
        # Generate risk recommendations
        risk_recommendations = []
        if risk_data["concentration_analysis"].get("concentration_score", 0) > 2500:
            risk_recommendations.append("Portfolio is highly concentrated - consider diversifying")
        
        if len(all_holdings) < 5:
            risk_recommendations.append("Add more holdings to improve diversification")
        
        risk_data["risk_recommendations"] = risk_recommendations
        
        return {
            "status": "success",
            "data": risk_data,
            "message": "Risk dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk dashboard: {str(e)}"
        )


@router.get("/market-overview", response_model=Dict[str, Any])
async def get_market_overview_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get market overview dashboard"""
    try:
        dashboard_service = DashboardService(db)
        market_data = dashboard_service._get_market_overview()
        
        # Add user-specific market insights
        user_holdings = []
        portfolios = dashboard_service.portfolio_service.get_user_portfolios(current_user.id)
        
        for portfolio in portfolios:
            holdings = dashboard_service.portfolio_service.get_portfolio_holdings(
                portfolio.id, current_user.id
            )
            user_holdings.extend(holdings)
        
        # Analyze how market movements affect user's portfolio
        portfolio_impact = {
            "affected_holdings": len(user_holdings),
            "market_correlation": "Medium",  # Simplified
            "sector_exposure": {},
            "market_sensitivity": "Moderate"
        }
        
        market_dashboard = {
            "user_id": current_user.id,
            "dashboard_type": "market_overview",
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "market_data": market_data,
            "portfolio_impact": portfolio_impact,
            "market_insights": [
                "Technology sector showing strong performance",
                "Banking sector facing headwinds",
                "Consider defensive positioning in current market"
            ]
        }
        
        return {
            "status": "success",
            "data": market_dashboard,
            "message": "Market overview dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market overview dashboard: {str(e)}"
        )
