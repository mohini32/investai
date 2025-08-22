"""
Performance Analytics endpoints - Comprehensive portfolio performance tracking and analytics
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.performance import PerformancePeriod
from app.services.performance_service import PerformanceAnalyticsService

router = APIRouter()


# Pydantic models
class PerformanceCalculationRequest(BaseModel):
    portfolio_id: int = Field(..., description="Portfolio ID for performance calculation")
    performance_date: Optional[datetime] = Field(None, description="Performance calculation date")


@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_portfolio_performance(
    request: PerformanceCalculationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate comprehensive portfolio performance"""
    try:
        performance_service = PerformanceAnalyticsService(db)
        
        performance = performance_service.calculate_portfolio_performance(
            request.portfolio_id,
            current_user.id,
            request.performance_date
        )
        
        return {
            "status": "success",
            "data": {
                "performance_id": performance.id,
                "portfolio_id": performance.portfolio_id,
                "performance_date": performance.performance_date.isoformat(),
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
                "outperformance": performance.outperformance
            },
            "message": "Portfolio performance calculated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate portfolio performance: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}", response_model=Dict[str, Any])
async def get_portfolio_performance(
    portfolio_id: int,
    period: Optional[str] = Query(None, description="Performance period filter"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get latest portfolio performance"""
    try:
        performance_service = PerformanceAnalyticsService(db)
        
        # Convert period string to enum if provided
        period_enum = None
        if period:
            try:
                period_enum = PerformancePeriod(period)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid period: {period}"
                )
        
        performance = performance_service.get_portfolio_performance(
            portfolio_id, current_user.id, period_enum
        )
        
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio performance not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": performance.id,
                "portfolio_id": performance.portfolio_id,
                "performance_date": performance.performance_date.isoformat(),
                "portfolio_value": performance.portfolio_value,
                "invested_amount": performance.invested_amount,
                "cash_balance": performance.cash_balance,
                "absolute_return": performance.absolute_return,
                "absolute_return_percentage": performance.absolute_return_percentage,
                "period_returns": {
                    "day_return": performance.day_return,
                    "day_return_percentage": performance.day_return_percentage,
                    "week_return": performance.week_return,
                    "week_return_percentage": performance.week_return_percentage,
                    "month_return": performance.month_return,
                    "month_return_percentage": performance.month_return_percentage,
                    "quarter_return": performance.quarter_return,
                    "quarter_return_percentage": performance.quarter_return_percentage,
                    "year_return": performance.year_return,
                    "year_return_percentage": performance.year_return_percentage
                },
                "risk_metrics": {
                    "annualized_return": performance.annualized_return,
                    "annualized_volatility": performance.annualized_volatility,
                    "sharpe_ratio": performance.sharpe_ratio,
                    "sortino_ratio": performance.sortino_ratio,
                    "calmar_ratio": performance.calmar_ratio,
                    "information_ratio": performance.information_ratio
                },
                "drawdown_metrics": {
                    "current_drawdown": performance.current_drawdown,
                    "maximum_drawdown": performance.maximum_drawdown,
                    "drawdown_duration_days": performance.drawdown_duration_days
                },
                "benchmark_metrics": {
                    "portfolio_beta": performance.portfolio_beta,
                    "portfolio_alpha": performance.portfolio_alpha,
                    "tracking_error": performance.tracking_error,
                    "r_squared": performance.r_squared,
                    "benchmark_return": performance.benchmark_return,
                    "excess_return": performance.excess_return,
                    "outperformance": performance.outperformance
                },
                "portfolio_metrics": {
                    "holdings_count": performance.holdings_count,
                    "concentration_ratio": performance.concentration_ratio
                }
            },
            "message": "Portfolio performance retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio performance: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}/history", response_model=Dict[str, Any])
async def get_performance_history(
    portfolio_id: int,
    days: int = Query(365, ge=30, le=1825, description="Number of days of history"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get portfolio performance history"""
    try:
        performance_service = PerformanceAnalyticsService(db)
        
        performance_history = performance_service.get_performance_history(
            portfolio_id, current_user.id, days
        )
        
        if not performance_history:
            return {
                "status": "success",
                "data": {
                    "portfolio_id": portfolio_id,
                    "history": [],
                    "summary": {
                        "total_records": 0,
                        "date_range": None
                    }
                },
                "message": "No performance history found"
            }
        
        # Format history data
        history_data = []
        for perf in performance_history:
            history_data.append({
                "date": perf.performance_date.isoformat(),
                "portfolio_value": perf.portfolio_value,
                "absolute_return": perf.absolute_return,
                "absolute_return_percentage": perf.absolute_return_percentage,
                "day_return_percentage": perf.day_return_percentage,
                "sharpe_ratio": perf.sharpe_ratio,
                "maximum_drawdown": perf.maximum_drawdown,
                "benchmark_return": perf.benchmark_return,
                "excess_return": perf.excess_return
            })
        
        # Calculate summary statistics
        latest_perf = performance_history[-1]
        earliest_perf = performance_history[0]
        
        summary = {
            "total_records": len(performance_history),
            "date_range": {
                "start": earliest_perf.performance_date.isoformat(),
                "end": latest_perf.performance_date.isoformat()
            },
            "value_change": {
                "start_value": earliest_perf.portfolio_value,
                "end_value": latest_perf.portfolio_value,
                "total_change": latest_perf.portfolio_value - earliest_perf.portfolio_value,
                "total_change_percentage": ((latest_perf.portfolio_value - earliest_perf.portfolio_value) / earliest_perf.portfolio_value * 100) if earliest_perf.portfolio_value > 0 else 0
            },
            "best_day": max(performance_history, key=lambda x: x.day_return_percentage or 0),
            "worst_day": min(performance_history, key=lambda x: x.day_return_percentage or 0)
        }
        
        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "history": history_data,
                "summary": summary
            },
            "message": f"Retrieved {len(history_data)} performance records"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance history: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}/benchmarks", response_model=Dict[str, Any])
async def get_benchmark_comparisons(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get benchmark comparisons for portfolio"""
    try:
        performance_service = PerformanceAnalyticsService(db)
        
        # Get latest performance
        performance = performance_service.get_portfolio_performance(portfolio_id, current_user.id)
        
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio performance not found"
            )
        
        # Get benchmark comparisons
        benchmark_comparisons = performance_service.get_benchmark_comparisons(performance.id)
        
        comparisons_data = []
        for comparison in benchmark_comparisons:
            comparisons_data.append({
                "id": comparison.id,
                "benchmark_type": comparison.benchmark_type.value,
                "benchmark_name": comparison.benchmark_name,
                "benchmark_symbol": comparison.benchmark_symbol,
                "benchmark_return": comparison.benchmark_return,
                "benchmark_volatility": comparison.benchmark_volatility,
                "benchmark_sharpe_ratio": comparison.benchmark_sharpe_ratio,
                "benchmark_max_drawdown": comparison.benchmark_max_drawdown,
                "excess_return": comparison.excess_return,
                "tracking_error": comparison.tracking_error,
                "information_ratio": comparison.information_ratio,
                "beta": comparison.beta,
                "alpha": comparison.alpha,
                "r_squared": comparison.r_squared,
                "up_market_capture": comparison.up_market_capture,
                "down_market_capture": comparison.down_market_capture,
                "period_type": comparison.period_type.value,
                "start_date": comparison.start_date.isoformat(),
                "end_date": comparison.end_date.isoformat()
            })
        
        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "performance_id": performance.id,
                "benchmark_comparisons": comparisons_data,
                "comparisons_count": len(comparisons_data)
            },
            "message": f"Retrieved {len(comparisons_data)} benchmark comparisons"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get benchmark comparisons: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}/attribution", response_model=Dict[str, Any])
async def get_attribution_analysis(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get performance attribution analysis"""
    try:
        performance_service = PerformanceAnalyticsService(db)

        # Get latest performance
        performance = performance_service.get_portfolio_performance(portfolio_id, current_user.id)

        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio performance not found"
            )

        # Get attribution analysis
        attribution_analysis = performance_service.get_attribution_analysis(performance.id)

        # Group by attribution type
        attribution_by_type = {}
        for attribution in attribution_analysis:
            attr_type = attribution.attribution_type.value
            if attr_type not in attribution_by_type:
                attribution_by_type[attr_type] = []

            attribution_by_type[attr_type].append({
                "id": attribution.id,
                "attribution_name": attribution.attribution_name,
                "attribution_return": attribution.attribution_return,
                "attribution_percentage": attribution.attribution_percentage,
                "sector_name": attribution.sector_name,
                "asset_class": attribution.asset_class,
                "security_symbol": attribution.security_symbol,
                "security_name": attribution.security_name,
                "security_weight": attribution.security_weight,
                "security_return": attribution.security_return,
                "security_contribution": attribution.security_contribution,
                "benchmark_weight": attribution.benchmark_weight,
                "benchmark_return": attribution.benchmark_return,
                "active_weight": attribution.active_weight,
                "allocation_effect": attribution.allocation_effect,
                "selection_effect": attribution.selection_effect,
                "interaction_effect": attribution.interaction_effect,
                "analysis_period": attribution.analysis_period.value,
                "start_date": attribution.start_date.isoformat(),
                "end_date": attribution.end_date.isoformat()
            })

        # Calculate summary statistics
        total_attribution = sum(attr.attribution_return for attr in attribution_analysis)
        total_allocation_effect = sum(attr.allocation_effect or 0 for attr in attribution_analysis)
        total_selection_effect = sum(attr.selection_effect or 0 for attr in attribution_analysis)
        total_interaction_effect = sum(attr.interaction_effect or 0 for attr in attribution_analysis)

        summary = {
            "total_attribution": total_attribution,
            "total_allocation_effect": total_allocation_effect,
            "total_selection_effect": total_selection_effect,
            "total_interaction_effect": total_interaction_effect,
            "attribution_breakdown": {
                "allocation_percentage": (total_allocation_effect / total_attribution * 100) if total_attribution != 0 else 0,
                "selection_percentage": (total_selection_effect / total_attribution * 100) if total_attribution != 0 else 0,
                "interaction_percentage": (total_interaction_effect / total_attribution * 100) if total_attribution != 0 else 0
            }
        }

        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "performance_id": performance.id,
                "attribution_by_type": attribution_by_type,
                "summary": summary,
                "total_attributions": len(attribution_analysis)
            },
            "message": f"Retrieved {len(attribution_analysis)} attribution analyses"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribution analysis: {str(e)}"
        )


@router.get("/alerts", response_model=Dict[str, Any])
async def get_performance_alerts(
    portfolio_id: Optional[int] = Query(None, description="Filter by portfolio ID"),
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get performance alerts for user"""
    try:
        performance_service = PerformanceAnalyticsService(db)
        alerts = performance_service.get_performance_alerts(current_user.id, portfolio_id)

        # Apply severity filter
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        # Limit results
        alerts = alerts[:limit]

        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "id": alert.id,
                "portfolio_id": alert.portfolio_id,
                "alert_type": alert.alert_type,
                "alert_title": alert.alert_title,
                "alert_message": alert.alert_message,
                "triggered_metric": alert.triggered_metric,
                "threshold_value": alert.threshold_value,
                "current_value": alert.current_value,
                "severity": alert.severity,
                "is_read": alert.is_read,
                "is_acknowledged": alert.is_acknowledged,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "created_at": alert.created_at.isoformat()
            })

        # Categorize alerts by severity
        alert_summary = {
            "critical": len([a for a in alerts_data if a["severity"] == "critical"]),
            "high": len([a for a in alerts_data if a["severity"] == "high"]),
            "medium": len([a for a in alerts_data if a["severity"] == "medium"]),
            "low": len([a for a in alerts_data if a["severity"] == "low"])
        }

        return {
            "status": "success",
            "data": {
                "alerts": alerts_data,
                "alert_summary": alert_summary,
                "total_alerts": len(alerts_data),
                "unread_count": len([a for a in alerts_data if not a["is_read"]]),
                "unacknowledged_count": len([a for a in alerts_data if not a["is_acknowledged"]])
            },
            "message": f"Retrieved {len(alerts_data)} performance alerts"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge_performance_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Acknowledge a performance alert"""
    try:
        # Get alert
        alert = db.query(PerformanceAlert).filter(
            and_(
                PerformanceAlert.id == alert_id,
                PerformanceAlert.user_id == current_user.id
            )
        ).first()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performance alert not found"
            )

        # Update alert
        alert.is_acknowledged = True
        alert.acknowledged_at = datetime.now()

        db.commit()

        return {
            "status": "success",
            "data": {
                "id": alert.id,
                "is_acknowledged": alert.is_acknowledged,
                "acknowledged_at": alert.acknowledged_at.isoformat()
            },
            "message": "Performance alert acknowledged successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to acknowledge performance alert: {str(e)}"
        )


@router.get("/analytics/multi-portfolio", response_model=Dict[str, Any])
async def get_multi_portfolio_analytics(
    portfolio_ids: List[int] = Query(..., description="Portfolio IDs to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get analytics across multiple portfolios"""
    try:
        if len(portfolio_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 portfolios can be analyzed at once"
            )

        performance_service = PerformanceAnalyticsService(db)
        portfolio_analytics = []

        total_value = 0
        total_invested = 0
        weighted_returns = 0

        for portfolio_id in portfolio_ids:
            performance = performance_service.get_portfolio_performance(portfolio_id, current_user.id)

            if performance:
                portfolio_analytics.append({
                    "portfolio_id": portfolio_id,
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
                    "holdings_count": performance.holdings_count,
                    "concentration_ratio": performance.concentration_ratio
                })

                total_value += performance.portfolio_value
                total_invested += performance.invested_amount
                weighted_returns += performance.absolute_return_percentage * performance.portfolio_value

        if not portfolio_analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No performance data found for the specified portfolios"
            )

        # Calculate aggregate metrics
        aggregate_metrics = {
            "total_portfolios": len(portfolio_analytics),
            "total_value": total_value,
            "total_invested": total_invested,
            "total_return": total_value - total_invested,
            "total_return_percentage": ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            "weighted_average_return": (weighted_returns / total_value) if total_value > 0 else 0,
            "best_performer": max(portfolio_analytics, key=lambda x: x["absolute_return_percentage"]),
            "worst_performer": min(portfolio_analytics, key=lambda x: x["absolute_return_percentage"]),
            "average_sharpe_ratio": sum(p.get("sharpe_ratio", 0) or 0 for p in portfolio_analytics) / len(portfolio_analytics),
            "average_volatility": sum(p.get("annualized_volatility", 0) or 0 for p in portfolio_analytics) / len(portfolio_analytics),
            "total_holdings": sum(p.get("holdings_count", 0) for p in portfolio_analytics)
        }

        return {
            "status": "success",
            "data": {
                "portfolio_analytics": portfolio_analytics,
                "aggregate_metrics": aggregate_metrics
            },
            "message": f"Multi-portfolio analytics completed for {len(portfolio_analytics)} portfolios"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get multi-portfolio analytics: {str(e)}"
        )


@router.get("/analytics/risk-return", response_model=Dict[str, Any])
async def get_risk_return_analysis(
    portfolio_id: int,
    benchmark_symbol: str = Query("NIFTY50", description="Benchmark symbol for comparison"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get risk-return analysis for portfolio"""
    try:
        performance_service = PerformanceAnalyticsService(db)

        # Get portfolio performance
        performance = performance_service.get_portfolio_performance(portfolio_id, current_user.id)

        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio performance not found"
            )

        # Get performance history for detailed analysis
        performance_history = performance_service.get_performance_history(portfolio_id, current_user.id, 365)

        # Calculate risk-return metrics
        risk_return_analysis = {
            "portfolio_metrics": {
                "annualized_return": performance.annualized_return,
                "annualized_volatility": performance.annualized_volatility,
                "sharpe_ratio": performance.sharpe_ratio,
                "sortino_ratio": performance.sortino_ratio,
                "calmar_ratio": performance.calmar_ratio,
                "maximum_drawdown": performance.maximum_drawdown,
                "current_drawdown": performance.current_drawdown
            },
            "benchmark_metrics": {
                "benchmark_return": performance.benchmark_return,
                "beta": performance.portfolio_beta,
                "alpha": performance.portfolio_alpha,
                "r_squared": performance.r_squared,
                "tracking_error": performance.tracking_error,
                "information_ratio": performance.information_ratio
            },
            "risk_analysis": {
                "risk_level": "High" if (performance.annualized_volatility or 0) > 0.25 else "Medium" if (performance.annualized_volatility or 0) > 0.15 else "Low",
                "return_consistency": "High" if (performance.sharpe_ratio or 0) > 1.0 else "Medium" if (performance.sharpe_ratio or 0) > 0.5 else "Low",
                "downside_protection": "Good" if (performance.maximum_drawdown or 0) > -0.15 else "Average" if (performance.maximum_drawdown or 0) > -0.25 else "Poor"
            },
            "performance_periods": {
                "ytd_return": performance.year_return_percentage,
                "qtd_return": performance.quarter_return_percentage,
                "mtd_return": performance.month_return_percentage,
                "wtd_return": performance.week_return_percentage
            }
        }

        # Add historical volatility analysis if we have enough data
        if len(performance_history) >= 30:
            daily_returns = []
            for i in range(1, len(performance_history)):
                prev_value = performance_history[i-1].portfolio_value
                curr_value = performance_history[i].portfolio_value
                if prev_value > 0:
                    daily_return = (curr_value - prev_value) / prev_value
                    daily_returns.append(daily_return)

            if daily_returns:
                import numpy as np
                daily_returns = np.array(daily_returns)

                # Rolling volatility analysis
                risk_return_analysis["volatility_analysis"] = {
                    "30_day_volatility": np.std(daily_returns[-30:]) * np.sqrt(252) if len(daily_returns) >= 30 else None,
                    "90_day_volatility": np.std(daily_returns[-90:]) * np.sqrt(252) if len(daily_returns) >= 90 else None,
                    "volatility_trend": "Increasing" if len(daily_returns) >= 60 and np.std(daily_returns[-30:]) > np.std(daily_returns[-60:-30]) else "Decreasing"
                }

        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "analysis_date": performance.performance_date.isoformat(),
                "risk_return_analysis": risk_return_analysis
            },
            "message": "Risk-return analysis completed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk-return analysis: {str(e)}"
        )
