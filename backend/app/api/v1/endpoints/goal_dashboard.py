"""
Goal Dashboard endpoints - Comprehensive goal planning dashboard and analytics
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.goal_dashboard_service import GoalDashboardService

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_goal_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive goal planning dashboard"""
    try:
        dashboard_service = GoalDashboardService(db)
        dashboard_data = dashboard_service.get_goal_dashboard(current_user.id)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "message": "Goal dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal dashboard: {str(e)}"
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_goal_analytics(
    goal_id: Optional[int] = Query(None, description="Specific goal ID for detailed analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed goal analytics"""
    try:
        dashboard_service = GoalDashboardService(db)
        analytics_data = dashboard_service.get_goal_analytics(current_user.id, goal_id)
        
        if "error" in analytics_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analytics_data["error"]
            )
        
        return {
            "status": "success",
            "data": analytics_data,
            "message": "Goal analytics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal analytics: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_goal_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered goal insights"""
    try:
        dashboard_service = GoalDashboardService(db)
        insights_data = dashboard_service.get_goal_insights(current_user.id)
        
        return {
            "status": "success",
            "data": insights_data,
            "message": "Goal insights retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal insights: {str(e)}"
        )


@router.get("/progress-summary", response_model=Dict[str, Any])
async def get_progress_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get goal progress summary"""
    try:
        dashboard_service = GoalDashboardService(db)
        progress_data = dashboard_service._get_progress_summary(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "progress_summary": progress_data,
                "summary_type": "goal_progress",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Progress summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress summary: {str(e)}"
        )


@router.get("/milestones/upcoming", response_model=Dict[str, Any])
async def get_upcoming_milestones(
    limit: int = Query(10, ge=1, le=50, description="Number of milestones to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get upcoming milestones across all goals"""
    try:
        dashboard_service = GoalDashboardService(db)
        milestones = dashboard_service._get_upcoming_milestones(current_user.id)
        
        # Limit results
        limited_milestones = milestones[:limit]
        
        return {
            "status": "success",
            "data": {
                "upcoming_milestones": limited_milestones,
                "count": len(limited_milestones),
                "total_available": len(milestones)
            },
            "message": f"Retrieved {len(limited_milestones)} upcoming milestones"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming milestones: {str(e)}"
        )


@router.get("/performance", response_model=Dict[str, Any])
async def get_goal_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get goal performance metrics"""
    try:
        dashboard_service = GoalDashboardService(db)
        performance_data = dashboard_service._get_goal_performance(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "performance_metrics": performance_data,
                "analysis_type": "goal_performance",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Goal performance metrics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal performance: {str(e)}"
        )


@router.get("/contributions/analysis", response_model=Dict[str, Any])
async def get_contribution_analysis(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get contribution analysis and patterns"""
    try:
        dashboard_service = GoalDashboardService(db)
        contribution_data = dashboard_service._get_contribution_analysis(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "contribution_analysis": contribution_data,
                "analysis_period": "12_months",
                "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat()
            },
            "message": "Contribution analysis retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contribution analysis: {str(e)}"
        )


@router.get("/alerts", response_model=Dict[str, Any])
async def get_goal_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get goal-related alerts and notifications"""
    try:
        dashboard_service = GoalDashboardService(db)
        alerts = dashboard_service._get_goal_alerts(current_user.id)
        
        # Categorize alerts by severity
        alert_summary = {
            "high": len([a for a in alerts if a.get("severity") == "high"]),
            "medium": len([a for a in alerts if a.get("severity") == "medium"]),
            "low": len([a for a in alerts if a.get("severity") == "low"])
        }
        
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "alert_summary": alert_summary,
                "total_alerts": len(alerts)
            },
            "message": f"Retrieved {len(alerts)} goal alerts"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal alerts: {str(e)}"
        )


@router.get("/recommendations", response_model=Dict[str, Any])
async def get_goal_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get goal planning recommendations"""
    try:
        dashboard_service = GoalDashboardService(db)
        recommendations = dashboard_service._get_dashboard_recommendations(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "recommendation_count": len(recommendations),
                "recommendation_type": "goal_planning"
            },
            "message": f"Retrieved {len(recommendations)} recommendations"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal recommendations: {str(e)}"
        )


@router.get("/health-score", response_model=Dict[str, Any])
async def get_goal_health_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get overall goal planning health score"""
    try:
        dashboard_service = GoalDashboardService(db)
        insights = dashboard_service.get_goal_insights(current_user.id)
        
        health_score = insights.get("goal_health_score", 0)
        
        # Determine health status
        if health_score >= 80:
            health_status = "Excellent"
            health_message = "Your goal planning is on track!"
        elif health_score >= 60:
            health_status = "Good"
            health_message = "Your goals are progressing well with room for improvement"
        elif health_score >= 40:
            health_status = "Fair"
            health_message = "Some goals need attention to stay on track"
        else:
            health_status = "Needs Improvement"
            health_message = "Consider reviewing and adjusting your goal strategy"
        
        return {
            "status": "success",
            "data": {
                "health_score": health_score,
                "health_status": health_status,
                "health_message": health_message,
                "key_insights": insights.get("key_insights", [])[:3],  # Top 3 insights
                "action_items": insights.get("action_items", [])[:3]   # Top 3 action items
            },
            "message": "Goal health score calculated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal health score: {str(e)}"
        )


@router.get("/summary", response_model=Dict[str, Any])
async def get_goal_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get quick goal planning summary"""
    try:
        dashboard_service = GoalDashboardService(db)
        
        # Get essential components
        overview = dashboard_service._get_goal_overview(current_user.id)
        progress = dashboard_service._get_progress_summary(current_user.id)
        upcoming_milestones = dashboard_service._get_upcoming_milestones(current_user.id)
        alerts = dashboard_service._get_goal_alerts(current_user.id)
        
        summary_data = {
            "user_id": current_user.id,
            "summary_type": "goal_planning_quick",
            "generated_at": dashboard_service.db.query(dashboard_service.db.func.now()).scalar().isoformat(),
            "quick_stats": {
                "total_goals": overview.get("total_goals", 0),
                "active_goals": overview.get("active_goals", 0),
                "overall_progress": progress.get("overall_progress_percentage", 0),
                "total_target_amount": progress.get("total_target_amount", 0),
                "total_current_amount": progress.get("total_current_amount", 0),
                "monthly_contribution": progress.get("total_monthly_contribution", 0),
                "upcoming_milestones": len(upcoming_milestones),
                "active_alerts": len([a for a in alerts if a.get("severity") in ["high", "medium"]])
            },
            "next_milestone": upcoming_milestones[0] if upcoming_milestones else None,
            "urgent_alerts": [a for a in alerts if a.get("severity") == "high"][:3]
        }
        
        return {
            "status": "success",
            "data": summary_data,
            "message": "Goal planning summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal summary: {str(e)}"
        )
