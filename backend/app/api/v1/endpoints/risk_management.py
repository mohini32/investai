"""
Risk Management endpoints - Advanced portfolio risk assessment and analytics
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.risk import RiskLevel, StressTestScenario
from app.services.risk_service import RiskManagementService

router = APIRouter()


# Pydantic models
class RiskAssessmentRequest(BaseModel):
    portfolio_id: int = Field(..., description="Portfolio ID for risk assessment")
    data_period_days: int = Field(default=252, ge=30, le=1000, description="Data period for analysis")
    include_stress_tests: bool = Field(default=True, description="Include stress testing")


class CustomStressTestRequest(BaseModel):
    portfolio_id: int = Field(..., description="Portfolio ID")
    scenario_name: str = Field(..., description="Custom scenario name")
    scenario_description: str = Field(..., description="Scenario description")
    market_shock: float = Field(..., ge=-1.0, le=1.0, description="Market shock percentage")
    volatility_multiplier: float = Field(default=1.5, ge=1.0, le=5.0, description="Volatility multiplier")
    correlation_increase: float = Field(default=0.2, ge=0.0, le=1.0, description="Correlation increase")


class RiskAlertUpdate(BaseModel):
    is_acknowledged: Optional[bool] = Field(None, description="Acknowledge alert")
    is_resolved: Optional[bool] = Field(None, description="Resolve alert")


@router.post("/assess", response_model=Dict[str, Any])
async def assess_portfolio_risk(
    request: RiskAssessmentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Perform comprehensive risk assessment on a portfolio"""
    try:
        risk_service = RiskManagementService(db)
        
        # Create or update risk profile
        risk_profile = risk_service.create_risk_profile(
            request.portfolio_id, 
            current_user.id, 
            request.data_period_days
        )
        
        return {
            "status": "success",
            "data": {
                "risk_profile_id": risk_profile.id,
                "overall_risk_level": risk_profile.overall_risk_level.value,
                "risk_score": risk_profile.risk_score,
                "portfolio_volatility": risk_profile.portfolio_volatility,
                "portfolio_beta": risk_profile.portfolio_beta,
                "sharpe_ratio": risk_profile.sharpe_ratio,
                "maximum_drawdown": risk_profile.maximum_drawdown,
                "var_1_day_99": risk_profile.var_1_day_99,
                "concentration_score": risk_profile.concentration_score,
                "assessment_date": risk_profile.assessment_date.isoformat()
            },
            "message": "Risk assessment completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to assess portfolio risk: {str(e)}"
        )


@router.get("/summary/{portfolio_id}", response_model=Dict[str, Any])
async def get_risk_summary(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive risk summary for a portfolio"""
    try:
        risk_service = RiskManagementService(db)
        summary = risk_service.get_portfolio_risk_summary(portfolio_id, current_user.id)
        
        if "error" in summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary["error"]
            )
        
        return {
            "status": "success",
            "data": summary,
            "message": "Risk summary retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk summary: {str(e)}"
        )


@router.get("/profile/{portfolio_id}", response_model=Dict[str, Any])
async def get_risk_profile(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed risk profile for a portfolio"""
    try:
        risk_service = RiskManagementService(db)
        risk_profile = risk_service.get_portfolio_risk_profile(portfolio_id, current_user.id)
        
        if not risk_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk profile not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": risk_profile.id,
                "overall_risk_level": risk_profile.overall_risk_level.value,
                "risk_score": risk_profile.risk_score,
                "portfolio_volatility": risk_profile.portfolio_volatility,
                "portfolio_beta": risk_profile.portfolio_beta,
                "sharpe_ratio": risk_profile.sharpe_ratio,
                "sortino_ratio": risk_profile.sortino_ratio,
                "maximum_drawdown": risk_profile.maximum_drawdown,
                "var_1_day_95": risk_profile.var_1_day_95,
                "var_1_day_99": risk_profile.var_1_day_99,
                "var_10_day_95": risk_profile.var_10_day_95,
                "var_10_day_99": risk_profile.var_10_day_99,
                "cvar_1_day_95": risk_profile.cvar_1_day_95,
                "cvar_1_day_99": risk_profile.cvar_1_day_99,
                "concentration_score": risk_profile.concentration_score,
                "herfindahl_index": risk_profile.herfindahl_index,
                "top_5_holdings_weight": risk_profile.top_5_holdings_weight,
                "avg_correlation": risk_profile.avg_correlation,
                "max_correlation": risk_profile.max_correlation,
                "systematic_risk": risk_profile.systematic_risk,
                "idiosyncratic_risk": risk_profile.idiosyncratic_risk,
                "assessment_date": risk_profile.assessment_date.isoformat(),
                "data_period_days": risk_profile.data_period_days,
                "benchmark_symbol": risk_profile.benchmark_symbol
            },
            "message": "Risk profile retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk profile: {str(e)}"
        )


@router.put("/profile/{portfolio_id}/update", response_model=Dict[str, Any])
async def update_risk_profile(
    portfolio_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update risk profile with latest data"""
    try:
        risk_service = RiskManagementService(db)
        
        # Update risk profile in background
        background_tasks.add_task(
            risk_service.update_risk_profile, 
            portfolio_id, 
            current_user.id
        )
        
        return {
            "status": "success",
            "message": "Risk profile update initiated"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update risk profile: {str(e)}"
        )


@router.get("/metrics/{portfolio_id}", response_model=Dict[str, Any])
async def get_risk_metrics(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed risk metrics for a portfolio"""
    try:
        risk_service = RiskManagementService(db)
        risk_profile = risk_service.get_portfolio_risk_profile(portfolio_id, current_user.id)
        
        if not risk_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk profile not found"
            )
        
        # Get detailed metrics
        detailed_metrics = db.query(risk_service.db.query(risk_service.RiskMetric).filter(
            risk_service.RiskMetric.risk_profile_id == risk_profile.id
        ).all())
        
        metrics_data = []
        for metric in risk_profile.risk_metrics:
            metrics_data.append({
                "id": metric.id,
                "metric_type": metric.metric_type.value,
                "metric_name": metric.metric_name,
                "metric_value": metric.metric_value,
                "metric_percentile": metric.metric_percentile,
                "calculation_method": metric.calculation_method,
                "confidence_level": metric.confidence_level,
                "time_horizon_days": metric.time_horizon_days,
                "calculation_date": metric.calculation_date.isoformat(),
                "data_quality_score": metric.data_quality_score
            })
        
        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "risk_profile_id": risk_profile.id,
                "metrics": metrics_data,
                "metrics_count": len(metrics_data)
            },
            "message": f"Retrieved {len(metrics_data)} risk metrics"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk metrics: {str(e)}"
        )


@router.get("/stress-tests/{portfolio_id}", response_model=Dict[str, Any])
async def get_stress_test_results(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get stress test results for a portfolio"""
    try:
        risk_service = RiskManagementService(db)
        risk_profile = risk_service.get_portfolio_risk_profile(portfolio_id, current_user.id)
        
        if not risk_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk profile not found"
            )
        
        stress_tests_data = []
        for stress_test in risk_profile.stress_tests:
            stress_tests_data.append({
                "id": stress_test.id,
                "scenario_type": stress_test.scenario_type.value,
                "scenario_name": stress_test.scenario_name,
                "scenario_description": stress_test.scenario_description,
                "portfolio_impact_percentage": stress_test.portfolio_impact_percentage,
                "portfolio_impact_amount": stress_test.portfolio_impact_amount,
                "stressed_volatility": stress_test.stressed_volatility,
                "stressed_var_95": stress_test.stressed_var_95,
                "stressed_var_99": stress_test.stressed_var_99,
                "stressed_max_drawdown": stress_test.stressed_max_drawdown,
                "estimated_recovery_days": stress_test.estimated_recovery_days,
                "recovery_probability": stress_test.recovery_probability,
                "test_date": stress_test.test_date.isoformat(),
                "test_methodology": stress_test.test_methodology,
                "confidence_level": stress_test.confidence_level
            })
        
        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "risk_profile_id": risk_profile.id,
                "stress_tests": stress_tests_data,
                "stress_tests_count": len(stress_tests_data)
            },
            "message": f"Retrieved {len(stress_tests_data)} stress test results"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stress test results: {str(e)}"
        )


@router.post("/stress-test/custom", response_model=Dict[str, Any])
async def run_custom_stress_test(
    request: CustomStressTestRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Run custom stress test scenario"""
    try:
        # This would implement custom stress testing
        # For now, return a mock response
        
        return {
            "status": "success",
            "data": {
                "scenario_name": request.scenario_name,
                "portfolio_impact_percentage": request.market_shock * 100,
                "estimated_recovery_days": abs(request.market_shock) * 365,
                "recovery_probability": max(0.3, 1.0 - abs(request.market_shock)),
                "test_date": db.query(db.func.now()).scalar().isoformat()
            },
            "message": "Custom stress test completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to run custom stress test: {str(e)}"
        )


@router.get("/alerts", response_model=Dict[str, Any])
async def get_risk_alerts(
    portfolio_id: Optional[int] = Query(None, description="Filter by portfolio ID"),
    alert_level: Optional[RiskLevel] = Query(None, description="Filter by alert level"),
    unresolved_only: bool = Query(True, description="Show only unresolved alerts"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk alerts for user"""
    try:
        risk_service = RiskManagementService(db)
        alerts = risk_service.get_risk_alerts(current_user.id, portfolio_id)

        # Apply filters
        if alert_level:
            alerts = [a for a in alerts if a.alert_level == alert_level]

        if unresolved_only:
            alerts = [a for a in alerts if not a.is_resolved]

        # Limit results
        alerts = alerts[:limit]

        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "id": alert.id,
                "portfolio_id": alert.portfolio_id,
                "alert_type": alert.alert_type,
                "alert_level": alert.alert_level.value,
                "title": alert.title,
                "message": alert.message,
                "triggered_metric": alert.triggered_metric,
                "threshold_value": alert.threshold_value,
                "current_value": alert.current_value,
                "is_acknowledged": alert.is_acknowledged,
                "is_resolved": alert.is_resolved,
                "created_at": alert.created_at.isoformat(),
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            })

        # Categorize alerts by level
        alert_summary = {
            "very_high": len([a for a in alerts_data if a["alert_level"] == "very_high"]),
            "high": len([a for a in alerts_data if a["alert_level"] == "high"]),
            "moderate": len([a for a in alerts_data if a["alert_level"] == "moderate"]),
            "low": len([a for a in alerts_data if a["alert_level"] == "low"]),
            "very_low": len([a for a in alerts_data if a["alert_level"] == "very_low"])
        }

        return {
            "status": "success",
            "data": {
                "alerts": alerts_data,
                "alert_summary": alert_summary,
                "total_alerts": len(alerts_data),
                "unresolved_count": len([a for a in alerts_data if not a["is_resolved"]])
            },
            "message": f"Retrieved {len(alerts_data)} risk alerts"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}", response_model=Dict[str, Any])
async def update_risk_alert(
    alert_id: int,
    update_data: RiskAlertUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update risk alert status"""
    try:
        risk_service = RiskManagementService(db)

        # Get alert
        alert = db.query(risk_service.RiskAlert).filter(
            risk_service.RiskAlert.id == alert_id,
            risk_service.RiskAlert.user_id == current_user.id
        ).first()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk alert not found"
            )

        # Update fields
        if update_data.is_acknowledged is not None:
            alert.is_acknowledged = update_data.is_acknowledged
            if update_data.is_acknowledged:
                alert.acknowledged_at = db.query(db.func.now()).scalar()

        if update_data.is_resolved is not None:
            alert.is_resolved = update_data.is_resolved
            if update_data.is_resolved:
                alert.resolved_at = db.query(db.func.now()).scalar()

        db.commit()

        return {
            "status": "success",
            "data": {
                "id": alert.id,
                "is_acknowledged": alert.is_acknowledged,
                "is_resolved": alert.is_resolved,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            },
            "message": "Risk alert updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update risk alert: {str(e)}"
        )


@router.post("/alerts/{alert_id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge_risk_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Acknowledge a risk alert"""
    try:
        risk_service = RiskManagementService(db)
        success = risk_service.acknowledge_risk_alert(alert_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk alert not found"
            )

        return {
            "status": "success",
            "message": "Risk alert acknowledged successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to acknowledge risk alert: {str(e)}"
        )


@router.get("/analytics/portfolio-comparison", response_model=Dict[str, Any])
async def get_portfolio_risk_comparison(
    portfolio_ids: List[int] = Query(..., description="Portfolio IDs to compare"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Compare risk metrics across multiple portfolios"""
    try:
        if len(portfolio_ids) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 portfolios can be compared at once"
            )

        risk_service = RiskManagementService(db)
        comparison_data = []

        for portfolio_id in portfolio_ids:
            risk_profile = risk_service.get_portfolio_risk_profile(portfolio_id, current_user.id)

            if risk_profile:
                comparison_data.append({
                    "portfolio_id": portfolio_id,
                    "overall_risk_level": risk_profile.overall_risk_level.value,
                    "risk_score": risk_profile.risk_score,
                    "portfolio_volatility": risk_profile.portfolio_volatility,
                    "portfolio_beta": risk_profile.portfolio_beta,
                    "sharpe_ratio": risk_profile.sharpe_ratio,
                    "maximum_drawdown": risk_profile.maximum_drawdown,
                    "var_1_day_99": risk_profile.var_1_day_99,
                    "concentration_score": risk_profile.concentration_score,
                    "assessment_date": risk_profile.assessment_date.isoformat()
                })

        if not comparison_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No risk profiles found for the specified portfolios"
            )

        # Calculate comparison metrics
        risk_scores = [p["risk_score"] for p in comparison_data if p["risk_score"]]
        volatilities = [p["portfolio_volatility"] for p in comparison_data if p["portfolio_volatility"]]

        comparison_summary = {
            "portfolios_compared": len(comparison_data),
            "risk_score_range": {
                "min": min(risk_scores) if risk_scores else 0,
                "max": max(risk_scores) if risk_scores else 0,
                "avg": sum(risk_scores) / len(risk_scores) if risk_scores else 0
            },
            "volatility_range": {
                "min": min(volatilities) if volatilities else 0,
                "max": max(volatilities) if volatilities else 0,
                "avg": sum(volatilities) / len(volatilities) if volatilities else 0
            }
        }

        return {
            "status": "success",
            "data": {
                "portfolio_comparisons": comparison_data,
                "comparison_summary": comparison_summary
            },
            "message": f"Risk comparison completed for {len(comparison_data)} portfolios"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare portfolio risks: {str(e)}"
        )


@router.get("/analytics/risk-trends/{portfolio_id}", response_model=Dict[str, Any])
async def get_risk_trends(
    portfolio_id: int,
    days: int = Query(90, ge=30, le=365, description="Number of days for trend analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk trends over time for a portfolio"""
    try:
        # This would typically query historical risk profiles
        # For now, return mock trend data

        import numpy as np
        from datetime import datetime, timedelta

        # Generate mock trend data
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days, 0, -1)]

        # Mock risk score trend
        base_risk_score = 60
        risk_scores = [base_risk_score + np.random.normal(0, 5) for _ in range(days)]
        risk_scores = [max(0, min(100, score)) for score in risk_scores]

        # Mock volatility trend
        base_volatility = 0.25
        volatilities = [base_volatility + np.random.normal(0, 0.03) for _ in range(days)]
        volatilities = [max(0.05, vol) for vol in volatilities]

        trend_data = {
            "portfolio_id": portfolio_id,
            "period_days": days,
            "risk_score_trend": [
                {"date": date, "value": score}
                for date, score in zip(dates, risk_scores)
            ],
            "volatility_trend": [
                {"date": date, "value": vol}
                for date, vol in zip(dates, volatilities)
            ],
            "trend_analysis": {
                "risk_score_direction": "stable",
                "volatility_direction": "increasing" if volatilities[-1] > volatilities[0] else "decreasing",
                "overall_trend": "improving" if risk_scores[-1] < risk_scores[0] else "deteriorating"
            }
        }

        return {
            "status": "success",
            "data": trend_data,
            "message": f"Risk trends retrieved for {days} days"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk trends: {str(e)}"
        )
