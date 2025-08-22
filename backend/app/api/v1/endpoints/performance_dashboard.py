"""
Performance Dashboard endpoints - Comprehensive performance analytics dashboard
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.performance_dashboard_service import PerformanceDashboardService

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_performance_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive performance analytics dashboard"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        dashboard_data = dashboard_service.get_performance_dashboard(current_user.id)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "message": "Performance dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance dashboard: {str(e)}"
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_performance_analytics(
    portfolio_id: Optional[int] = Query(None, description="Specific portfolio ID for detailed analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed performance analytics"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        analytics_data = dashboard_service.get_performance_analytics(current_user.id, portfolio_id)
        
        return {
            "status": "success",
            "data": analytics_data,
            "message": "Performance analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance analytics: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_performance_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered performance insights"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        insights_data = dashboard_service.get_performance_insights(current_user.id)
        
        return {
            "status": "success",
            "data": insights_data,
            "message": "Performance insights retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance insights: {str(e)}"
        )


@router.get("/overview", response_model=Dict[str, Any])
async def get_performance_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get performance overview summary"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        overview_data = dashboard_service._get_performance_overview(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "performance_overview": overview_data,
                "overview_type": "performance_summary",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Performance overview retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance overview: {str(e)}"
        )


@router.get("/portfolio-summary", response_model=Dict[str, Any])
async def get_portfolio_performance_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get portfolio performance summary"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        summary_data = dashboard_service._get_portfolio_performance_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "portfolio_performance_summary": summary_data,
                "summary_type": "portfolio_performance",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Portfolio performance summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio performance summary: {str(e)}"
        )


@router.get("/benchmark-summary", response_model=Dict[str, Any])
async def get_benchmark_comparison_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get benchmark comparison summary"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        benchmark_data = dashboard_service._get_benchmark_comparison_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "benchmark_comparison_summary": benchmark_data,
                "summary_type": "benchmark_comparison",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Benchmark comparison summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get benchmark comparison summary: {str(e)}"
        )


@router.get("/attribution-summary", response_model=Dict[str, Any])
async def get_attribution_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get attribution analysis summary"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        attribution_data = dashboard_service._get_attribution_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "attribution_summary": attribution_data,
                "summary_type": "attribution_analysis",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Attribution analysis summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribution summary: {str(e)}"
        )


@router.get("/risk-summary", response_model=Dict[str, Any])
async def get_risk_metrics_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk metrics summary"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        risk_data = dashboard_service._get_risk_metrics_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "risk_metrics_summary": risk_data,
                "summary_type": "risk_metrics",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Risk metrics summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk metrics summary: {str(e)}"
        )


@router.get("/alerts-summary", response_model=Dict[str, Any])
async def get_performance_alerts_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get performance alerts summary"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        alerts_data = dashboard_service._get_alerts_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "performance_alerts_summary": alerts_data,
                "summary_type": "performance_alerts",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Performance alerts summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance alerts summary: {str(e)}"
        )


@router.get("/health-score", response_model=Dict[str, Any])
async def get_performance_health_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get overall performance health score"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        insights = dashboard_service.get_performance_insights(current_user.id)
        
        health_score = insights.get("performance_health_score", 0)
        
        # Determine health status
        if health_score >= 80:
            health_status = "Excellent"
            health_message = "Your portfolio performance is excellent!"
        elif health_score >= 60:
            health_status = "Good"
            health_message = "Your performance is good with room for optimization"
        elif health_score >= 40:
            health_status = "Fair"
            health_message = "Some performance improvements needed"
        else:
            health_status = "Needs Improvement"
            health_message = "Significant performance attention required"
        
        return {
            "status": "success",
            "data": {
                "performance_health_score": health_score,
                "health_status": health_status,
                "health_message": health_message,
                "key_insights": insights.get("key_performance_insights", [])[:3],
                "action_items": insights.get("performance_action_items", [])[:3],
                "performance_warnings": insights.get("performance_warnings", [])[:3]
            },
            "message": "Performance health score calculated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance health score: {str(e)}"
        )


@router.get("/summary", response_model=Dict[str, Any])
async def get_performance_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get quick performance summary"""
    try:
        dashboard_service = PerformanceDashboardService(db)
        
        # Get essential components
        overview = dashboard_service._get_performance_overview(current_user.id)
        portfolio_summary = dashboard_service._get_portfolio_performance_summary(current_user.id)
        benchmark_summary = dashboard_service._get_benchmark_comparison_summary(current_user.id)
        alerts_summary = dashboard_service._get_alerts_summary(current_user.id)
        insights = dashboard_service.get_performance_insights(current_user.id)
        
        summary_data = {
            "user_id": current_user.id,
            "summary_type": "performance_analytics_quick",
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "quick_stats": {
                "total_portfolios": overview.get("total_portfolios", 0),
                "portfolios_with_performance": overview.get("portfolios_with_performance", 0),
                "total_portfolio_value": overview.get("total_portfolio_value", 0),
                "weighted_average_return": overview.get("weighted_average_return", 0),
                "outperformance_rate": benchmark_summary.get("outperformance_rate", 0),
                "active_alerts": alerts_summary.get("active_alerts", 0),
                "performance_health_score": insights.get("performance_health_score", 0)
            },
            "best_performer": overview.get("best_performing_portfolio"),
            "worst_performer": overview.get("worst_performing_portfolio"),
            "benchmark_performance": {
                "outperforming_count": benchmark_summary.get("outperforming_count", 0),
                "average_excess_return": benchmark_summary.get("average_excess_return", 0)
            },
            "critical_warnings": insights.get("performance_warnings", [])[:2],
            "top_opportunities": insights.get("performance_opportunities", [])[:3]
        }
        
        return {
            "status": "success",
            "data": summary_data,
            "message": "Performance summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance summary: {str(e)}"
        )
