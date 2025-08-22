"""
Performance Analytics Service - Comprehensive portfolio performance tracking and analytics
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging
import math
import numpy as np
import pandas as pd

from app.models.performance import (
    PortfolioPerformance, BenchmarkComparison, AttributionAnalysis, PerformanceReport,
    PerformanceBenchmark, PerformanceAlert, PerformancePeriod, BenchmarkType, AttributionType
)
from app.models.portfolio import Portfolio, Holding, Transaction
from app.models.user import User

logger = logging.getLogger(__name__)


class PerformanceAnalyticsService:
    """Service for comprehensive portfolio performance analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Risk-free rate (10-year G-Sec rate)
        self.risk_free_rate = 0.07  # 7% annual
        
        # Default benchmarks
        self.default_benchmarks = {
            "NIFTY50": {"name": "NIFTY 50", "type": BenchmarkType.MARKET_INDEX},
            "SENSEX": {"name": "BSE SENSEX", "type": BenchmarkType.MARKET_INDEX},
            "NIFTY500": {"name": "NIFTY 500", "type": BenchmarkType.MARKET_INDEX},
            "NIFTYMIDCAP": {"name": "NIFTY Midcap 100", "type": BenchmarkType.MARKET_INDEX}
        }
    
    # Performance Calculation
    def calculate_portfolio_performance(self, portfolio_id: int, user_id: int, 
                                      performance_date: Optional[datetime] = None) -> PortfolioPerformance:
        """Calculate comprehensive portfolio performance"""
        try:
            if performance_date is None:
                performance_date = datetime.now()
            
            # Get portfolio
            portfolio = self.db.query(Portfolio).filter(
                and_(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
            ).first()
            
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            # Get holdings
            holdings = self.db.query(Holding).filter(
                Holding.portfolio_id == portfolio_id
            ).all()
            
            # Calculate current portfolio value
            portfolio_value = sum(h.current_value or 0 for h in holdings)
            invested_amount = sum(h.invested_amount or 0 for h in holdings)
            cash_balance = portfolio.cash_balance or 0
            
            total_portfolio_value = portfolio_value + cash_balance
            
            # Calculate absolute returns
            absolute_return = total_portfolio_value - invested_amount
            absolute_return_percentage = (absolute_return / invested_amount * 100) if invested_amount > 0 else 0
            
            # Calculate period returns
            period_returns = self._calculate_period_returns(portfolio_id, performance_date)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(portfolio_id, performance_date)
            
            # Calculate benchmark comparison
            benchmark_metrics = self._calculate_benchmark_comparison(portfolio_id, performance_date)
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(holdings)
            
            # Create performance record
            performance = PortfolioPerformance(
                portfolio_id=portfolio_id,
                user_id=user_id,
                performance_date=performance_date,
                portfolio_value=total_portfolio_value,
                invested_amount=invested_amount,
                cash_balance=cash_balance,
                absolute_return=absolute_return,
                absolute_return_percentage=absolute_return_percentage,
                day_return=period_returns.get("day_return", 0),
                day_return_percentage=period_returns.get("day_return_percentage", 0),
                week_return=period_returns.get("week_return", 0),
                week_return_percentage=period_returns.get("week_return_percentage", 0),
                month_return=period_returns.get("month_return", 0),
                month_return_percentage=period_returns.get("month_return_percentage", 0),
                quarter_return=period_returns.get("quarter_return", 0),
                quarter_return_percentage=period_returns.get("quarter_return_percentage", 0),
                year_return=period_returns.get("year_return", 0),
                year_return_percentage=period_returns.get("year_return_percentage", 0),
                annualized_return=risk_metrics.get("annualized_return"),
                annualized_volatility=risk_metrics.get("annualized_volatility"),
                sharpe_ratio=risk_metrics.get("sharpe_ratio"),
                sortino_ratio=risk_metrics.get("sortino_ratio"),
                calmar_ratio=risk_metrics.get("calmar_ratio"),
                information_ratio=risk_metrics.get("information_ratio"),
                current_drawdown=risk_metrics.get("current_drawdown", 0),
                maximum_drawdown=risk_metrics.get("maximum_drawdown", 0),
                drawdown_duration_days=risk_metrics.get("drawdown_duration_days", 0),
                portfolio_beta=benchmark_metrics.get("beta"),
                portfolio_alpha=benchmark_metrics.get("alpha"),
                tracking_error=benchmark_metrics.get("tracking_error"),
                r_squared=benchmark_metrics.get("r_squared"),
                benchmark_return=benchmark_metrics.get("benchmark_return"),
                excess_return=benchmark_metrics.get("excess_return"),
                outperformance=benchmark_metrics.get("outperformance", False),
                holdings_count=portfolio_metrics.get("holdings_count", 0),
                concentration_ratio=portfolio_metrics.get("concentration_ratio", 0)
            )
            
            self.db.add(performance)
            self.db.commit()
            self.db.refresh(performance)
            
            # Generate benchmark comparisons
            self._generate_benchmark_comparisons(performance.id, performance_date)
            
            # Generate attribution analysis
            self._generate_attribution_analysis(performance.id, holdings, performance_date)
            
            # Check for performance alerts
            self._check_performance_alerts(performance)
            
            logger.info(f"Calculated performance for portfolio {portfolio_id}")
            return performance
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to calculate portfolio performance: {str(e)}")
            raise
    
    def _calculate_period_returns(self, portfolio_id: int, current_date: datetime) -> Dict[str, float]:
        """Calculate returns for different periods"""
        try:
            # Get historical performance data
            historical_performance = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.portfolio_id == portfolio_id
            ).order_by(desc(PortfolioPerformance.performance_date)).limit(252).all()  # ~1 year
            
            if not historical_performance:
                return {}
            
            current_value = historical_performance[0].portfolio_value
            
            # Calculate period returns
            period_returns = {}
            
            # Day return (if we have yesterday's data)
            if len(historical_performance) > 1:
                yesterday_value = historical_performance[1].portfolio_value
                day_return = current_value - yesterday_value
                day_return_percentage = (day_return / yesterday_value * 100) if yesterday_value > 0 else 0
                period_returns.update({
                    "day_return": day_return,
                    "day_return_percentage": day_return_percentage
                })
            
            # Week return (7 days ago)
            week_data = [p for p in historical_performance if (current_date - p.performance_date).days <= 7]
            if len(week_data) > 1:
                week_old_value = week_data[-1].portfolio_value
                week_return = current_value - week_old_value
                week_return_percentage = (week_return / week_old_value * 100) if week_old_value > 0 else 0
                period_returns.update({
                    "week_return": week_return,
                    "week_return_percentage": week_return_percentage
                })
            
            # Month return (30 days ago)
            month_data = [p for p in historical_performance if (current_date - p.performance_date).days <= 30]
            if len(month_data) > 1:
                month_old_value = month_data[-1].portfolio_value
                month_return = current_value - month_old_value
                month_return_percentage = (month_return / month_old_value * 100) if month_old_value > 0 else 0
                period_returns.update({
                    "month_return": month_return,
                    "month_return_percentage": month_return_percentage
                })
            
            # Quarter return (90 days ago)
            quarter_data = [p for p in historical_performance if (current_date - p.performance_date).days <= 90]
            if len(quarter_data) > 1:
                quarter_old_value = quarter_data[-1].portfolio_value
                quarter_return = current_value - quarter_old_value
                quarter_return_percentage = (quarter_return / quarter_old_value * 100) if quarter_old_value > 0 else 0
                period_returns.update({
                    "quarter_return": quarter_return,
                    "quarter_return_percentage": quarter_return_percentage
                })
            
            # Year return (365 days ago)
            year_data = [p for p in historical_performance if (current_date - p.performance_date).days <= 365]
            if len(year_data) > 1:
                year_old_value = year_data[-1].portfolio_value
                year_return = current_value - year_old_value
                year_return_percentage = (year_return / year_old_value * 100) if year_old_value > 0 else 0
                period_returns.update({
                    "year_return": year_return,
                    "year_return_percentage": year_return_percentage
                })
            
            return period_returns
            
        except Exception as e:
            logger.error(f"Failed to calculate period returns: {str(e)}")
            return {}
    
    def _calculate_risk_metrics(self, portfolio_id: int, current_date: datetime) -> Dict[str, float]:
        """Calculate risk-adjusted performance metrics"""
        try:
            # Get historical performance data
            historical_performance = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.portfolio_id == portfolio_id
            ).order_by(PortfolioPerformance.performance_date).all()
            
            if len(historical_performance) < 30:  # Need at least 30 data points
                return {}
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(historical_performance)):
                prev_value = historical_performance[i-1].portfolio_value
                curr_value = historical_performance[i].portfolio_value
                if prev_value > 0:
                    daily_return = (curr_value - prev_value) / prev_value
                    daily_returns.append(daily_return)
            
            if not daily_returns:
                return {}
            
            daily_returns = np.array(daily_returns)
            
            # Annualized return
            mean_daily_return = np.mean(daily_returns)
            annualized_return = (1 + mean_daily_return) ** 252 - 1
            
            # Annualized volatility
            daily_volatility = np.std(daily_returns)
            annualized_volatility = daily_volatility * np.sqrt(252)
            
            # Sharpe ratio
            excess_return = annualized_return - self.risk_free_rate
            sharpe_ratio = excess_return / annualized_volatility if annualized_volatility > 0 else 0
            
            # Sortino ratio (downside deviation)
            downside_returns = daily_returns[daily_returns < 0]
            downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else annualized_volatility
            sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum drawdown
            portfolio_values = [p.portfolio_value for p in historical_performance]
            cumulative_returns = np.array(portfolio_values) / portfolio_values[0]
            rolling_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - rolling_max) / rolling_max
            maximum_drawdown = np.min(drawdowns)
            current_drawdown = drawdowns[-1]
            
            # Calmar ratio
            calmar_ratio = annualized_return / abs(maximum_drawdown) if maximum_drawdown != 0 else 0
            
            # Drawdown duration
            drawdown_duration_days = 0
            for i in range(len(drawdowns) - 1, -1, -1):
                if drawdowns[i] < 0:
                    drawdown_duration_days += 1
                else:
                    break
            
            return {
                "annualized_return": annualized_return,
                "annualized_volatility": annualized_volatility,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "calmar_ratio": calmar_ratio,
                "maximum_drawdown": maximum_drawdown,
                "current_drawdown": current_drawdown,
                "drawdown_duration_days": drawdown_duration_days
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate risk metrics: {str(e)}")
            return {}
    
    def _calculate_benchmark_comparison(self, portfolio_id: int, current_date: datetime) -> Dict[str, float]:
        """Calculate benchmark comparison metrics"""
        try:
            # For now, use mock benchmark data
            # In production, this would fetch actual benchmark data
            
            # Mock NIFTY 50 performance
            benchmark_return = 0.12  # 12% annual return
            benchmark_volatility = 0.18  # 18% annual volatility
            
            # Get portfolio historical data
            historical_performance = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.portfolio_id == portfolio_id
            ).order_by(PortfolioPerformance.performance_date).all()
            
            if len(historical_performance) < 30:
                return {"benchmark_return": benchmark_return}
            
            # Calculate portfolio returns
            portfolio_values = [p.portfolio_value for p in historical_performance]
            portfolio_returns = []
            for i in range(1, len(portfolio_values)):
                if portfolio_values[i-1] > 0:
                    ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                    portfolio_returns.append(ret)
            
            if not portfolio_returns:
                return {"benchmark_return": benchmark_return}
            
            portfolio_returns = np.array(portfolio_returns)
            
            # Mock benchmark returns (normally would be fetched)
            np.random.seed(42)  # For reproducible results
            benchmark_returns = np.random.normal(benchmark_return/252, benchmark_volatility/np.sqrt(252), len(portfolio_returns))
            
            # Calculate beta
            covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
            
            # Calculate alpha
            portfolio_annual_return = np.mean(portfolio_returns) * 252
            alpha = portfolio_annual_return - (self.risk_free_rate + beta * (benchmark_return - self.risk_free_rate))
            
            # Calculate tracking error
            excess_returns = portfolio_returns - benchmark_returns
            tracking_error = np.std(excess_returns) * np.sqrt(252)
            
            # Calculate information ratio
            excess_return = np.mean(excess_returns) * 252
            information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
            
            # Calculate R-squared
            correlation = np.corrcoef(portfolio_returns, benchmark_returns)[0, 1]
            r_squared = correlation ** 2 if not np.isnan(correlation) else 0
            
            return {
                "benchmark_return": benchmark_return,
                "beta": beta,
                "alpha": alpha,
                "tracking_error": tracking_error,
                "information_ratio": information_ratio,
                "r_squared": r_squared,
                "excess_return": excess_return,
                "outperformance": excess_return > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate benchmark comparison: {str(e)}")
            return {}
    
    def _calculate_portfolio_metrics(self, holdings: List[Holding]) -> Dict[str, Any]:
        """Calculate portfolio composition metrics"""
        try:
            if not holdings:
                return {"holdings_count": 0, "concentration_ratio": 0}
            
            # Calculate weights
            total_value = sum(h.current_value or 0 for h in holdings)
            if total_value == 0:
                return {"holdings_count": len(holdings), "concentration_ratio": 0}
            
            weights = [(h.current_value or 0) / total_value for h in holdings]
            weights.sort(reverse=True)
            
            # Top 5 holdings concentration
            top_5_weight = sum(weights[:5])
            
            return {
                "holdings_count": len(holdings),
                "concentration_ratio": top_5_weight
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio metrics: {str(e)}")
            return {"holdings_count": 0, "concentration_ratio": 0}

    # Benchmark Comparison
    def _generate_benchmark_comparisons(self, performance_id: int, performance_date: datetime):
        """Generate benchmark comparisons for different periods"""
        try:
            # Get performance record
            performance = self.db.query(PortfolioPerformance).filter(
                PortfolioPerformance.id == performance_id
            ).first()

            if not performance:
                return

            # Define comparison periods
            periods = [
                (PerformancePeriod.ONE_MONTH, 30),
                (PerformancePeriod.THREE_MONTHS, 90),
                (PerformancePeriod.ONE_YEAR, 365)
            ]

            for period_type, days in periods:
                start_date = performance_date - timedelta(days=days)

                # Get benchmark data (mock for now)
                benchmark_data = self._get_benchmark_data("NIFTY50", start_date, performance_date)

                if benchmark_data:
                    comparison = BenchmarkComparison(
                        performance_id=performance_id,
                        benchmark_type=BenchmarkType.MARKET_INDEX,
                        benchmark_name=benchmark_data["name"],
                        benchmark_symbol=benchmark_data["symbol"],
                        benchmark_return=benchmark_data["return"],
                        benchmark_volatility=benchmark_data["volatility"],
                        benchmark_sharpe_ratio=benchmark_data["sharpe_ratio"],
                        benchmark_max_drawdown=benchmark_data["max_drawdown"],
                        excess_return=performance.year_return_percentage - benchmark_data["return"],
                        tracking_error=benchmark_data.get("tracking_error", 0),
                        information_ratio=benchmark_data.get("information_ratio", 0),
                        beta=performance.portfolio_beta or 1.0,
                        alpha=performance.portfolio_alpha or 0,
                        r_squared=performance.r_squared or 0,
                        up_market_capture=benchmark_data.get("up_market_capture", 1.0),
                        down_market_capture=benchmark_data.get("down_market_capture", 1.0),
                        period_type=period_type,
                        start_date=start_date,
                        end_date=performance_date
                    )

                    self.db.add(comparison)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to generate benchmark comparisons: {str(e)}")

    def _get_benchmark_data(self, benchmark_symbol: str, start_date: datetime,
                           end_date: datetime) -> Optional[Dict[str, Any]]:
        """Get benchmark performance data"""
        try:
            # Mock benchmark data - in production, this would fetch real data
            benchmark_data = {
                "NIFTY50": {
                    "name": "NIFTY 50",
                    "symbol": "NIFTY50",
                    "return": 12.5,  # 12.5% annual return
                    "volatility": 18.0,  # 18% volatility
                    "sharpe_ratio": 0.65,
                    "max_drawdown": -15.2,
                    "tracking_error": 2.5,
                    "information_ratio": 0.3,
                    "up_market_capture": 1.05,
                    "down_market_capture": 0.95
                }
            }

            return benchmark_data.get(benchmark_symbol)

        except Exception as e:
            logger.error(f"Failed to get benchmark data: {str(e)}")
            return None

    # Attribution Analysis
    def _generate_attribution_analysis(self, performance_id: int, holdings: List[Holding],
                                     performance_date: datetime):
        """Generate performance attribution analysis"""
        try:
            if not holdings:
                return

            # Calculate total portfolio value
            total_value = sum(h.current_value or 0 for h in holdings)
            if total_value == 0:
                return

            # Security-level attribution
            for holding in holdings:
                if holding.current_value and holding.current_value > 0:
                    # Calculate holding weight
                    weight = holding.current_value / total_value

                    # Calculate holding return (mock calculation)
                    holding_return = self._calculate_holding_return(holding, performance_date)

                    # Calculate contribution to portfolio return
                    contribution = weight * holding_return

                    # Create attribution record
                    attribution = AttributionAnalysis(
                        performance_id=performance_id,
                        attribution_type=AttributionType.SECURITY_SELECTION,
                        attribution_name=f"{holding.symbol} Security Selection",
                        attribution_return=contribution,
                        attribution_percentage=(contribution / 10) * 100,  # Assume 10% portfolio return
                        security_symbol=holding.symbol,
                        security_name=holding.name,
                        security_weight=weight,
                        security_return=holding_return,
                        security_contribution=contribution,
                        benchmark_weight=0.02,  # Mock benchmark weight
                        benchmark_return=12.0,  # Mock benchmark return
                        active_weight=weight - 0.02,
                        allocation_effect=0,
                        selection_effect=contribution,
                        interaction_effect=0,
                        analysis_period=PerformancePeriod.ONE_MONTH,
                        start_date=performance_date - timedelta(days=30),
                        end_date=performance_date
                    )

                    self.db.add(attribution)

            # Sector-level attribution
            sector_attribution = self._calculate_sector_attribution(holdings, performance_date)
            for sector_data in sector_attribution:
                attribution = AttributionAnalysis(
                    performance_id=performance_id,
                    attribution_type=AttributionType.ASSET_ALLOCATION,
                    attribution_name=f"{sector_data['sector']} Allocation",
                    attribution_return=sector_data["contribution"],
                    attribution_percentage=sector_data["percentage"],
                    sector_name=sector_data["sector"],
                    security_weight=sector_data["weight"],
                    security_return=sector_data["return"],
                    security_contribution=sector_data["contribution"],
                    benchmark_weight=sector_data["benchmark_weight"],
                    benchmark_return=sector_data["benchmark_return"],
                    active_weight=sector_data["active_weight"],
                    allocation_effect=sector_data["allocation_effect"],
                    selection_effect=sector_data["selection_effect"],
                    interaction_effect=sector_data["interaction_effect"],
                    analysis_period=PerformancePeriod.ONE_MONTH,
                    start_date=performance_date - timedelta(days=30),
                    end_date=performance_date
                )

                self.db.add(attribution)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to generate attribution analysis: {str(e)}")

    def _calculate_holding_return(self, holding: Holding, performance_date: datetime) -> float:
        """Calculate individual holding return"""
        try:
            # Mock calculation - in production, would use actual price data
            # Simulate some return based on holding characteristics
            import random
            random.seed(hash(holding.symbol) % 1000)  # Deterministic but varied

            # Generate return between -20% to +30%
            return random.uniform(-0.20, 0.30)

        except Exception as e:
            logger.error(f"Failed to calculate holding return: {str(e)}")
            return 0.0

    def _calculate_sector_attribution(self, holdings: List[Holding],
                                    performance_date: datetime) -> List[Dict[str, Any]]:
        """Calculate sector-level attribution"""
        try:
            # Group holdings by sector (simplified)
            sectors = {}
            total_value = sum(h.current_value or 0 for h in holdings)

            for holding in holdings:
                # Mock sector assignment
                sector = self._get_holding_sector(holding.symbol)

                if sector not in sectors:
                    sectors[sector] = {
                        "holdings": [],
                        "total_value": 0,
                        "total_return": 0
                    }

                sectors[sector]["holdings"].append(holding)
                sectors[sector]["total_value"] += holding.current_value or 0

            # Calculate sector attribution
            sector_attribution = []

            for sector, data in sectors.items():
                sector_weight = data["total_value"] / total_value if total_value > 0 else 0
                sector_return = sum(self._calculate_holding_return(h, performance_date) *
                                  ((h.current_value or 0) / data["total_value"])
                                  for h in data["holdings"]) if data["total_value"] > 0 else 0

                # Mock benchmark data
                benchmark_weight = 0.15  # 15% benchmark weight
                benchmark_return = 0.12  # 12% benchmark return

                active_weight = sector_weight - benchmark_weight
                allocation_effect = active_weight * (benchmark_return - 0.10)  # vs portfolio benchmark
                selection_effect = benchmark_weight * (sector_return - benchmark_return)
                interaction_effect = active_weight * (sector_return - benchmark_return)

                total_contribution = allocation_effect + selection_effect + interaction_effect

                sector_attribution.append({
                    "sector": sector,
                    "weight": sector_weight,
                    "return": sector_return,
                    "contribution": total_contribution,
                    "percentage": (total_contribution / 0.10) * 100,  # Assume 10% portfolio return
                    "benchmark_weight": benchmark_weight,
                    "benchmark_return": benchmark_return,
                    "active_weight": active_weight,
                    "allocation_effect": allocation_effect,
                    "selection_effect": selection_effect,
                    "interaction_effect": interaction_effect
                })

            return sector_attribution

        except Exception as e:
            logger.error(f"Failed to calculate sector attribution: {str(e)}")
            return []

    def _get_holding_sector(self, symbol: str) -> str:
        """Get sector for a holding symbol"""
        # Simplified sector mapping
        sector_mapping = {
            "RELIANCE": "Energy",
            "TCS": "Technology",
            "HDFCBANK": "Banking",
            "INFY": "Technology",
            "HINDUNILVR": "Consumer Goods",
            "ITC": "Consumer Goods",
            "KOTAKBANK": "Banking",
            "LT": "Infrastructure",
            "AXISBANK": "Banking",
            "MARUTI": "Automotive"
        }

        return sector_mapping.get(symbol, "Others")

    # Performance Alerts
    def _check_performance_alerts(self, performance: PortfolioPerformance):
        """Check for performance alerts and create notifications"""
        try:
            alerts = []

            # Underperformance alert
            if performance.excess_return and performance.excess_return < -5:  # 5% underperformance
                alerts.append({
                    "type": "underperformance",
                    "title": "Portfolio Underperformance Alert",
                    "message": f"Portfolio is underperforming benchmark by {abs(performance.excess_return):.1f}%",
                    "metric": "excess_return",
                    "threshold": -5,
                    "current": performance.excess_return,
                    "severity": "high"
                })

            # High drawdown alert
            if performance.current_drawdown < -10:  # 10% drawdown
                alerts.append({
                    "type": "high_drawdown",
                    "title": "High Drawdown Alert",
                    "message": f"Portfolio is in {abs(performance.current_drawdown):.1f}% drawdown",
                    "metric": "current_drawdown",
                    "threshold": -10,
                    "current": performance.current_drawdown,
                    "severity": "high"
                })

            # Low Sharpe ratio alert
            if performance.sharpe_ratio and performance.sharpe_ratio < 0.5:
                alerts.append({
                    "type": "low_sharpe_ratio",
                    "title": "Low Risk-Adjusted Returns",
                    "message": f"Sharpe ratio is {performance.sharpe_ratio:.2f}, indicating poor risk-adjusted returns",
                    "metric": "sharpe_ratio",
                    "threshold": 0.5,
                    "current": performance.sharpe_ratio,
                    "severity": "medium"
                })

            # High concentration alert
            if performance.concentration_ratio > 0.6:  # 60% in top 5 holdings
                alerts.append({
                    "type": "high_concentration",
                    "title": "High Portfolio Concentration",
                    "message": f"Top 5 holdings represent {performance.concentration_ratio:.1%} of portfolio",
                    "metric": "concentration_ratio",
                    "threshold": 0.6,
                    "current": performance.concentration_ratio,
                    "severity": "medium"
                })

            # Milestone alerts
            if performance.absolute_return_percentage > 25:  # 25% positive return
                alerts.append({
                    "type": "milestone_achievement",
                    "title": "Portfolio Milestone Achieved",
                    "message": f"Portfolio has achieved {performance.absolute_return_percentage:.1f}% returns!",
                    "metric": "absolute_return_percentage",
                    "threshold": 25,
                    "current": performance.absolute_return_percentage,
                    "severity": "low"
                })

            # Create alert records
            for alert_data in alerts:
                alert = PerformanceAlert(
                    user_id=performance.user_id,
                    portfolio_id=performance.portfolio_id,
                    alert_type=alert_data["type"],
                    alert_title=alert_data["title"],
                    alert_message=alert_data["message"],
                    triggered_metric=alert_data["metric"],
                    threshold_value=alert_data["threshold"],
                    current_value=alert_data["current"],
                    severity=alert_data["severity"],
                    alert_data=json.dumps(alert_data)
                )
                self.db.add(alert)

            if alerts:
                self.db.commit()
                logger.info(f"Created {len(alerts)} performance alerts for portfolio {performance.portfolio_id}")

        except Exception as e:
            logger.error(f"Failed to check performance alerts: {str(e)}")

    # Public Methods
    def get_portfolio_performance(self, portfolio_id: int, user_id: int,
                                period: Optional[PerformancePeriod] = None) -> Optional[PortfolioPerformance]:
        """Get latest portfolio performance"""
        query = self.db.query(PortfolioPerformance).filter(
            and_(
                PortfolioPerformance.portfolio_id == portfolio_id,
                PortfolioPerformance.user_id == user_id
            )
        )

        return query.order_by(desc(PortfolioPerformance.performance_date)).first()

    def get_performance_history(self, portfolio_id: int, user_id: int,
                              days: int = 365) -> List[PortfolioPerformance]:
        """Get portfolio performance history"""
        cutoff_date = datetime.now() - timedelta(days=days)

        return self.db.query(PortfolioPerformance).filter(
            and_(
                PortfolioPerformance.portfolio_id == portfolio_id,
                PortfolioPerformance.user_id == user_id,
                PortfolioPerformance.performance_date >= cutoff_date
            )
        ).order_by(PortfolioPerformance.performance_date).all()

    def get_benchmark_comparisons(self, performance_id: int) -> List[BenchmarkComparison]:
        """Get benchmark comparisons for a performance record"""
        return self.db.query(BenchmarkComparison).filter(
            BenchmarkComparison.performance_id == performance_id
        ).all()

    def get_attribution_analysis(self, performance_id: int) -> List[AttributionAnalysis]:
        """Get attribution analysis for a performance record"""
        return self.db.query(AttributionAnalysis).filter(
            AttributionAnalysis.performance_id == performance_id
        ).all()

    def get_performance_alerts(self, user_id: int, portfolio_id: Optional[int] = None) -> List[PerformanceAlert]:
        """Get performance alerts for user"""
        query = self.db.query(PerformanceAlert).filter(PerformanceAlert.user_id == user_id)

        if portfolio_id:
            query = query.filter(PerformanceAlert.portfolio_id == portfolio_id)

        return query.filter(PerformanceAlert.is_read == False).order_by(
            desc(PerformanceAlert.created_at)
        ).all()
