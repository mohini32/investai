"""
Risk Dashboard endpoints - Comprehensive risk analytics dashboard
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.risk_dashboard_service import RiskDashboardService

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_risk_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive risk management dashboard"""
    try:
        dashboard_service = RiskDashboardService(db)
        dashboard_data = dashboard_service.get_risk_dashboard(current_user.id)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "message": "Risk dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk dashboard: {str(e)}"
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_risk_analytics(
    portfolio_id: Optional[int] = Query(None, description="Specific portfolio ID for detailed analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed risk analytics"""
    try:
        dashboard_service = RiskDashboardService(db)
        analytics_data = dashboard_service.get_risk_analytics(current_user.id, portfolio_id)
        
        return {
            "status": "success",
            "data": analytics_data,
            "message": "Risk analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk analytics: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_risk_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered risk insights"""
    try:
        dashboard_service = RiskDashboardService(db)
        insights_data = dashboard_service.get_risk_insights(current_user.id)
        
        return {
            "status": "success",
            "data": insights_data,
            "message": "Risk insights retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk insights: {str(e)}"
        )


@router.get("/overview", response_model=Dict[str, Any])
async def get_risk_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk overview summary"""
    try:
        dashboard_service = RiskDashboardService(db)
        overview_data = dashboard_service._get_risk_overview(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "risk_overview": overview_data,
                "overview_type": "risk_summary",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Risk overview retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk overview: {str(e)}"
        )


@router.get("/portfolio-summary", response_model=Dict[str, Any])
async def get_portfolio_risk_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get portfolio risk summary"""
    try:
        dashboard_service = RiskDashboardService(db)
        summary_data = dashboard_service._get_portfolio_risk_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "portfolio_risk_summary": summary_data,
                "summary_type": "portfolio_risk",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Portfolio risk summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio risk summary: {str(e)}"
        )


@router.get("/stress-test-summary", response_model=Dict[str, Any])
async def get_stress_test_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get stress test summary"""
    try:
        dashboard_service = RiskDashboardService(db)
        stress_test_data = dashboard_service._get_stress_test_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "stress_test_summary": stress_test_data,
                "summary_type": "stress_testing",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Stress test summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stress test summary: {str(e)}"
        )


@router.get("/alerts-summary", response_model=Dict[str, Any])
async def get_risk_alerts_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk alerts summary"""
    try:
        dashboard_service = RiskDashboardService(db)
        alerts_data = dashboard_service._get_risk_alerts_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "risk_alerts_summary": alerts_data,
                "summary_type": "risk_alerts",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Risk alerts summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk alerts summary: {str(e)}"
        )


@router.get("/trends", response_model=Dict[str, Any])
async def get_risk_trends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk trends analysis"""
    try:
        dashboard_service = RiskDashboardService(db)
        trends_data = dashboard_service._get_risk_trends(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "risk_trends": trends_data,
                "trends_type": "risk_analysis",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Risk trends retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk trends: {str(e)}"
        )


@router.get("/recommendations", response_model=Dict[str, Any])
async def get_risk_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk management recommendations"""
    try:
        dashboard_service = RiskDashboardService(db)
        recommendations = dashboard_service._get_risk_recommendations(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "recommendation_count": len(recommendations),
                "recommendation_type": "risk_management"
            },
            "message": f"Retrieved {len(recommendations)} risk recommendations"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk recommendations: {str(e)}"
        )


@router.get("/health-score", response_model=Dict[str, Any])
async def get_risk_health_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get overall risk health score"""
    try:
        dashboard_service = RiskDashboardService(db)
        insights = dashboard_service.get_risk_insights(current_user.id)
        
        health_score = insights.get("overall_risk_health", 0)
        
        # Determine health status
        if health_score >= 80:
            health_status = "Excellent"
            health_message = "Your portfolio risk management is excellent!"
        elif health_score >= 60:
            health_status = "Good"
            health_message = "Your risk management is good with room for optimization"
        elif health_score >= 40:
            health_status = "Fair"
            health_message = "Some risk management improvements needed"
        else:
            health_status = "Needs Improvement"
            health_message = "Significant risk management attention required"
        
        return {
            "status": "success",
            "data": {
                "risk_health_score": health_score,
                "health_status": health_status,
                "health_message": health_message,
                "key_insights": insights.get("key_risk_insights", [])[:3],
                "action_items": insights.get("risk_action_items", [])[:3],
                "risk_warnings": insights.get("risk_warnings", [])[:3]
            },
            "message": "Risk health score calculated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk health score: {str(e)}"
        )


@router.get("/summary", response_model=Dict[str, Any])
async def get_risk_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get quick risk management summary"""
    try:
        dashboard_service = RiskDashboardService(db)
        
        # Get essential components
        overview = dashboard_service._get_risk_overview(current_user.id)
        portfolio_summary = dashboard_service._get_portfolio_risk_summary(current_user.id)
        alerts_summary = dashboard_service._get_risk_alerts_summary(current_user.id)
        insights = dashboard_service.get_risk_insights(current_user.id)
        
        summary_data = {
            "user_id": current_user.id,
            "summary_type": "risk_management_quick",
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "quick_stats": {
                "total_portfolios": overview.get("total_portfolios", 0),
                "portfolios_assessed": overview.get("portfolios_with_risk_assessment", 0),
                "average_risk_score": overview.get("average_risk_score", 0),
                "total_portfolio_value": portfolio_summary.get("total_portfolio_value", 0),
                "active_alerts": alerts_summary.get("active_alerts", 0),
                "critical_alerts": alerts_summary.get("critical_alerts", 0),
                "risk_health_score": insights.get("overall_risk_health", 0)
            },
            "highest_risk_portfolio": overview.get("highest_risk_portfolio"),
            "critical_warnings": insights.get("risk_warnings", [])[:2],
            "top_recommendations": dashboard_service._get_risk_recommendations(current_user.id)[:3]
        }
        
        return {
            "status": "success",
            "data": summary_data,
            "message": "Risk management summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk summary: {str(e)}"
        )
