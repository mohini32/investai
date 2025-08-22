"""
Tax Dashboard endpoints - Comprehensive tax analytics dashboard
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.tax_dashboard_service import TaxDashboardService

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_tax_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive tax planning dashboard"""
    try:
        dashboard_service = TaxDashboardService(db)
        dashboard_data = dashboard_service.get_tax_dashboard(current_user.id)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "message": "Tax dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax dashboard: {str(e)}"
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_tax_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed tax analytics"""
    try:
        dashboard_service = TaxDashboardService(db)
        analytics_data = dashboard_service.get_tax_analytics(current_user.id)
        
        return {
            "status": "success",
            "data": analytics_data,
            "message": "Tax analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax analytics: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_tax_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered tax insights"""
    try:
        dashboard_service = TaxDashboardService(db)
        insights_data = dashboard_service.get_tax_insights(current_user.id)
        
        return {
            "status": "success",
            "data": insights_data,
            "message": "Tax insights retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax insights: {str(e)}"
        )


@router.get("/overview", response_model=Dict[str, Any])
async def get_tax_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax overview summary"""
    try:
        dashboard_service = TaxDashboardService(db)
        overview_data = dashboard_service._get_tax_overview(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "tax_overview": overview_data,
                "overview_type": "tax_summary",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Tax overview retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax overview: {str(e)}"
        )


@router.get("/calculation-summary", response_model=Dict[str, Any])
async def get_tax_calculation_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax calculation summary"""
    try:
        dashboard_service = TaxDashboardService(db)
        calculation_data = dashboard_service._get_tax_calculation_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "tax_calculation_summary": calculation_data,
                "summary_type": "tax_calculation",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Tax calculation summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax calculation summary: {str(e)}"
        )


@router.get("/savings-summary", response_model=Dict[str, Any])
async def get_tax_savings_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax savings summary"""
    try:
        dashboard_service = TaxDashboardService(db)
        savings_data = dashboard_service._get_tax_savings_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "tax_savings_summary": savings_data,
                "summary_type": "tax_savings",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Tax savings summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax savings summary: {str(e)}"
        )


@router.get("/capital-gains-summary", response_model=Dict[str, Any])
async def get_capital_gains_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get capital gains summary"""
    try:
        dashboard_service = TaxDashboardService(db)
        capital_gains_data = dashboard_service._get_capital_gains_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "capital_gains_summary": capital_gains_data,
                "summary_type": "capital_gains",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Capital gains summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get capital gains summary: {str(e)}"
        )


@router.get("/optimization-summary", response_model=Dict[str, Any])
async def get_optimization_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax optimization summary"""
    try:
        dashboard_service = TaxDashboardService(db)
        optimization_data = dashboard_service._get_optimization_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "optimization_summary": optimization_data,
                "summary_type": "tax_optimization",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Tax optimization summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get optimization summary: {str(e)}"
        )


@router.get("/calendar-summary", response_model=Dict[str, Any])
async def get_tax_calendar_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax calendar summary"""
    try:
        dashboard_service = TaxDashboardService(db)
        calendar_data = dashboard_service._get_tax_calendar_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "tax_calendar_summary": calendar_data,
                "summary_type": "tax_calendar",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Tax calendar summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax calendar summary: {str(e)}"
        )


@router.get("/recommendations", response_model=Dict[str, Any])
async def get_tax_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax planning recommendations"""
    try:
        dashboard_service = TaxDashboardService(db)
        recommendations = dashboard_service._get_tax_recommendations(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "recommendation_count": len(recommendations),
                "recommendation_type": "tax_planning"
            },
            "message": f"Retrieved {len(recommendations)} tax recommendations"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax recommendations: {str(e)}"
        )


@router.get("/health-score", response_model=Dict[str, Any])
async def get_tax_health_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get overall tax health score"""
    try:
        dashboard_service = TaxDashboardService(db)
        insights = dashboard_service.get_tax_insights(current_user.id)
        
        health_score = insights.get("tax_health_score", 0)
        
        # Determine health status
        if health_score >= 80:
            health_status = "Excellent"
            health_message = "Your tax planning is excellent!"
        elif health_score >= 60:
            health_status = "Good"
            health_message = "Your tax planning is good with room for optimization"
        elif health_score >= 40:
            health_status = "Fair"
            health_message = "Some tax planning improvements needed"
        else:
            health_status = "Needs Improvement"
            health_message = "Significant tax planning attention required"
        
        return {
            "status": "success",
            "data": {
                "tax_health_score": health_score,
                "health_status": health_status,
                "health_message": health_message,
                "key_insights": insights.get("key_tax_insights", [])[:3],
                "action_items": insights.get("tax_action_items", [])[:3],
                "tax_warnings": insights.get("tax_warnings", [])[:3]
            },
            "message": "Tax health score calculated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax health score: {str(e)}"
        )


@router.get("/summary", response_model=Dict[str, Any])
async def get_tax_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get quick tax planning summary"""
    try:
        dashboard_service = TaxDashboardService(db)
        
        # Get essential components
        overview = dashboard_service._get_tax_overview(current_user.id)
        calculation_summary = dashboard_service._get_tax_calculation_summary(current_user.id)
        savings_summary = dashboard_service._get_tax_savings_summary(current_user.id)
        optimization_summary = dashboard_service._get_optimization_summary(current_user.id)
        insights = dashboard_service.get_tax_insights(current_user.id)
        
        summary_data = {
            "user_id": current_user.id,
            "summary_type": "tax_planning_quick",
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "quick_stats": {
                "annual_income": overview.get("annual_income", 0),
                "total_tax": calculation_summary.get("total_tax", 0),
                "effective_tax_rate": calculation_summary.get("effective_tax_rate", 0),
                "potential_savings": optimization_summary.get("total_potential_savings", 0),
                "tax_regime": overview.get("tax_regime", ""),
                "tax_health_score": insights.get("tax_health_score", 0)
            },
            "deduction_utilization": {
                "section_80c": savings_summary.get("section_80c", {}),
                "section_80d": savings_summary.get("section_80d", {}),
                "total_potential_savings": savings_summary.get("total_potential_savings", 0)
            },
            "optimization_opportunities": optimization_summary.get("total_suggestions", 0),
            "critical_warnings": insights.get("tax_warnings", [])[:2],
            "top_recommendations": dashboard_service._get_tax_recommendations(current_user.id)[:3]
        }
        
        return {
            "status": "success",
            "data": summary_data,
            "message": "Tax planning summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax summary: {str(e)}"
        )
