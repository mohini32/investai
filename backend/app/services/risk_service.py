"""
Risk Management Service - Advanced portfolio risk assessment and analytics
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import json
import logging
import math
from scipy import stats
from scipy.optimize import minimize

from app.models.risk import (
    PortfolioRiskProfile, RiskMetric, StressTestResult, RiskAlert, RiskBenchmark,
    RiskMetricType, RiskLevel, StressTestScenario
)
from app.models.portfolio import Portfolio, Holding
from app.models.user import User
from app.services.market_service import MarketService

logger = logging.getLogger(__name__)


class RiskManagementService:
    """Service for comprehensive portfolio risk management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_service = MarketService()
    
    # Risk Profile Management
    def create_risk_profile(self, portfolio_id: int, user_id: int, 
                          data_period_days: int = 252) -> PortfolioRiskProfile:
        """Create comprehensive risk profile for a portfolio"""
        try:
            # Get portfolio and holdings
            portfolio = self.db.query(Portfolio).filter(
                and_(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
            ).first()
            
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            holdings = self.db.query(Holding).filter(
                Holding.portfolio_id == portfolio_id
            ).all()
            
            if not holdings:
                raise ValueError("No holdings found in portfolio")
            
            # Get historical data for risk calculations
            historical_data = self._get_portfolio_historical_data(holdings, data_period_days)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_comprehensive_risk_metrics(
                historical_data, holdings, data_period_days
            )
            
            # Create risk profile
            risk_profile = PortfolioRiskProfile(
                portfolio_id=portfolio_id,
                user_id=user_id,
                overall_risk_level=self._determine_risk_level(risk_metrics["risk_score"]),
                risk_score=risk_metrics["risk_score"],
                portfolio_volatility=risk_metrics["volatility"],
                portfolio_beta=risk_metrics["beta"],
                sharpe_ratio=risk_metrics["sharpe_ratio"],
                sortino_ratio=risk_metrics["sortino_ratio"],
                maximum_drawdown=risk_metrics["max_drawdown"],
                var_1_day_95=risk_metrics["var_1d_95"],
                var_1_day_99=risk_metrics["var_1d_99"],
                var_10_day_95=risk_metrics["var_10d_95"],
                var_10_day_99=risk_metrics["var_10d_99"],
                cvar_1_day_95=risk_metrics["cvar_1d_95"],
                cvar_1_day_99=risk_metrics["cvar_1d_99"],
                concentration_score=risk_metrics["concentration_score"],
                herfindahl_index=risk_metrics["herfindahl_index"],
                top_5_holdings_weight=risk_metrics["top_5_weight"],
                avg_correlation=risk_metrics["avg_correlation"],
                max_correlation=risk_metrics["max_correlation"],
                systematic_risk=risk_metrics["systematic_risk"],
                idiosyncratic_risk=risk_metrics["idiosyncratic_risk"],
                assessment_date=datetime.now(),
                data_period_days=data_period_days
            )
            
            self.db.add(risk_profile)
            self.db.commit()
            self.db.refresh(risk_profile)
            
            # Create detailed risk metrics
            self._create_detailed_risk_metrics(risk_profile.id, risk_metrics)
            
            # Run stress tests
            self._run_comprehensive_stress_tests(risk_profile.id, historical_data, holdings)
            
            # Check for risk alerts
            self._check_risk_alerts(risk_profile)
            
            logger.info(f"Created risk profile {risk_profile.id} for portfolio {portfolio_id}")
            return risk_profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create risk profile: {str(e)}")
            raise
    
    def get_portfolio_risk_profile(self, portfolio_id: int, user_id: int) -> Optional[PortfolioRiskProfile]:
        """Get latest risk profile for a portfolio"""
        return self.db.query(PortfolioRiskProfile).filter(
            and_(
                PortfolioRiskProfile.portfolio_id == portfolio_id,
                PortfolioRiskProfile.user_id == user_id
            )
        ).order_by(desc(PortfolioRiskProfile.created_at)).first()
    
    def update_risk_profile(self, portfolio_id: int, user_id: int) -> PortfolioRiskProfile:
        """Update risk profile with latest data"""
        try:
            # Delete old risk profile
            old_profile = self.get_portfolio_risk_profile(portfolio_id, user_id)
            if old_profile:
                self.db.delete(old_profile)
            
            # Create new risk profile
            return self.create_risk_profile(portfolio_id, user_id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update risk profile: {str(e)}")
            raise
    
    # Risk Calculations
    def _calculate_comprehensive_risk_metrics(self, historical_data: pd.DataFrame, 
                                            holdings: List[Holding], 
                                            data_period_days: int) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        try:
            if historical_data.empty:
                return self._get_default_risk_metrics()
            
            # Portfolio returns
            portfolio_returns = self._calculate_portfolio_returns(historical_data, holdings)
            
            # Basic risk metrics
            volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized
            
            # Beta calculation (vs NIFTY)
            benchmark_returns = self._get_benchmark_returns(data_period_days)
            beta = self._calculate_beta(portfolio_returns, benchmark_returns)
            
            # Sharpe ratio
            risk_free_rate = 0.06  # Assume 6% risk-free rate
            excess_returns = portfolio_returns.mean() * 252 - risk_free_rate
            sharpe_ratio = excess_returns / volatility if volatility > 0 else 0
            
            # Sortino ratio (downside deviation)
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else volatility
            sortino_ratio = excess_returns / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            # Value at Risk (VaR)
            var_1d_95 = np.percentile(portfolio_returns, 5)
            var_1d_99 = np.percentile(portfolio_returns, 1)
            var_10d_95 = var_1d_95 * np.sqrt(10)
            var_10d_99 = var_1d_99 * np.sqrt(10)
            
            # Conditional VaR (Expected Shortfall)
            cvar_1d_95 = portfolio_returns[portfolio_returns <= var_1d_95].mean()
            cvar_1d_99 = portfolio_returns[portfolio_returns <= var_1d_99].mean()
            
            # Concentration metrics
            concentration_metrics = self._calculate_concentration_metrics(holdings)
            
            # Correlation analysis
            correlation_metrics = self._calculate_correlation_metrics(historical_data)
            
            # Risk decomposition
            systematic_risk, idiosyncratic_risk = self._decompose_risk(
                portfolio_returns, benchmark_returns, beta
            )
            
            # Overall risk score (0-100)
            risk_score = self._calculate_risk_score({
                "volatility": volatility,
                "max_drawdown": abs(max_drawdown),
                "var_99": abs(var_1d_99),
                "concentration": concentration_metrics["concentration_score"],
                "beta": abs(beta - 1)
            })
            
            return {
                "risk_score": risk_score,
                "volatility": volatility,
                "beta": beta,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "max_drawdown": max_drawdown,
                "var_1d_95": var_1d_95,
                "var_1d_99": var_1d_99,
                "var_10d_95": var_10d_95,
                "var_10d_99": var_10d_99,
                "cvar_1d_95": cvar_1d_95,
                "cvar_1d_99": cvar_1d_99,
                **concentration_metrics,
                **correlation_metrics,
                "systematic_risk": systematic_risk,
                "idiosyncratic_risk": idiosyncratic_risk
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate risk metrics: {str(e)}")
            return self._get_default_risk_metrics()
    
    def _calculate_portfolio_returns(self, historical_data: pd.DataFrame, 
                                   holdings: List[Holding]) -> pd.Series:
        """Calculate portfolio returns based on holdings weights"""
        try:
            # Calculate weights
            total_value = sum(h.current_value or 0 for h in holdings)
            if total_value == 0:
                return pd.Series()
            
            weights = {}
            for holding in holdings:
                weight = (holding.current_value or 0) / total_value
                weights[holding.symbol] = weight
            
            # Calculate weighted returns
            portfolio_returns = pd.Series(index=historical_data.index, dtype=float)
            
            for date in historical_data.index:
                daily_return = 0
                for symbol, weight in weights.items():
                    if symbol in historical_data.columns:
                        stock_return = historical_data.loc[date, symbol]
                        if not pd.isna(stock_return):
                            daily_return += weight * stock_return
                
                portfolio_returns.loc[date] = daily_return
            
            return portfolio_returns.dropna()
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio returns: {str(e)}")
            return pd.Series()
    
    def _calculate_beta(self, portfolio_returns: pd.Series, 
                       benchmark_returns: pd.Series) -> float:
        """Calculate portfolio beta vs benchmark"""
        try:
            if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
                return 1.0
            
            # Align dates
            common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) < 30:  # Need at least 30 observations
                return 1.0
            
            port_aligned = portfolio_returns.loc[common_dates]
            bench_aligned = benchmark_returns.loc[common_dates]
            
            # Calculate beta using covariance
            covariance = np.cov(port_aligned, bench_aligned)[0, 1]
            benchmark_variance = np.var(bench_aligned)
            
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
            
            return max(0.1, min(3.0, beta))  # Cap beta between 0.1 and 3.0
            
        except Exception as e:
            logger.error(f"Failed to calculate beta: {str(e)}")
            return 1.0
    
    def _calculate_concentration_metrics(self, holdings: List[Holding]) -> Dict[str, float]:
        """Calculate portfolio concentration metrics"""
        try:
            if not holdings:
                return {"concentration_score": 0, "herfindahl_index": 0, "top_5_weight": 0}
            
            # Calculate weights
            total_value = sum(h.current_value or 0 for h in holdings)
            if total_value == 0:
                return {"concentration_score": 0, "herfindahl_index": 0, "top_5_weight": 0}
            
            weights = [(h.current_value or 0) / total_value for h in holdings]
            weights.sort(reverse=True)
            
            # Herfindahl-Hirschman Index
            herfindahl_index = sum(w**2 for w in weights)
            
            # Top 5 holdings weight
            top_5_weight = sum(weights[:5])
            
            # Concentration score (0-100, higher = more concentrated)
            # Based on HHI and top holdings concentration
            concentration_score = min(100, (herfindahl_index * 100) + (top_5_weight * 50))
            
            return {
                "concentration_score": concentration_score,
                "herfindahl_index": herfindahl_index,
                "top_5_weight": top_5_weight
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate concentration metrics: {str(e)}")
            return {"concentration_score": 0, "herfindahl_index": 0, "top_5_weight": 0}
    
    def _calculate_correlation_metrics(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate correlation metrics between holdings"""
        try:
            if historical_data.empty or historical_data.shape[1] < 2:
                return {"avg_correlation": 0, "max_correlation": 0}
            
            # Calculate correlation matrix
            correlation_matrix = historical_data.corr()
            
            # Extract upper triangle (excluding diagonal)
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
            correlations = correlation_matrix.where(mask).stack().dropna()
            
            if len(correlations) == 0:
                return {"avg_correlation": 0, "max_correlation": 0}
            
            avg_correlation = correlations.mean()
            max_correlation = correlations.max()
            
            return {
                "avg_correlation": avg_correlation,
                "max_correlation": max_correlation
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate correlation metrics: {str(e)}")
            return {"avg_correlation": 0, "max_correlation": 0}
    
    def _decompose_risk(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series, 
                       beta: float) -> Tuple[float, float]:
        """Decompose portfolio risk into systematic and idiosyncratic components"""
        try:
            if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
                return 0.5, 0.5
            
            # Align returns
            common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) < 30:
                return 0.5, 0.5
            
            port_aligned = portfolio_returns.loc[common_dates]
            bench_aligned = benchmark_returns.loc[common_dates]
            
            # Calculate systematic risk (beta^2 * benchmark_variance)
            benchmark_variance = np.var(bench_aligned)
            systematic_variance = (beta**2) * benchmark_variance
            
            # Calculate total portfolio variance
            portfolio_variance = np.var(port_aligned)
            
            # Idiosyncratic risk is the remainder
            idiosyncratic_variance = max(0, portfolio_variance - systematic_variance)
            
            # Convert to proportions
            total_variance = systematic_variance + idiosyncratic_variance
            if total_variance > 0:
                systematic_risk = systematic_variance / total_variance
                idiosyncratic_risk = idiosyncratic_variance / total_variance
            else:
                systematic_risk = 0.5
                idiosyncratic_risk = 0.5
            
            return systematic_risk, idiosyncratic_risk
            
        except Exception as e:
            logger.error(f"Failed to decompose risk: {str(e)}")
            return 0.5, 0.5
    
    def _calculate_risk_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall risk score (0-100)"""
        try:
            # Normalize and weight different risk components
            volatility_score = min(100, metrics["volatility"] * 100 / 0.4)  # 40% vol = 100 score
            drawdown_score = min(100, metrics["max_drawdown"] * 100 / 0.5)  # 50% DD = 100 score
            var_score = min(100, metrics["var_99"] * 100 / 0.1)  # 10% daily VaR = 100 score
            concentration_score = metrics["concentration"]
            beta_score = min(100, metrics["beta"] * 50)  # Beta deviation from 1
            
            # Weighted average
            risk_score = (
                volatility_score * 0.3 +
                drawdown_score * 0.25 +
                var_score * 0.2 +
                concentration_score * 0.15 +
                beta_score * 0.1
            )
            
            return max(0, min(100, risk_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate risk score: {str(e)}")
            return 50.0
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on risk score"""
        if risk_score <= 20:
            return RiskLevel.VERY_LOW
        elif risk_score <= 40:
            return RiskLevel.LOW
        elif risk_score <= 60:
            return RiskLevel.MODERATE
        elif risk_score <= 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _get_default_risk_metrics(self) -> Dict[str, float]:
        """Get default risk metrics when calculation fails"""
        return {
            "risk_score": 50.0,
            "volatility": 0.2,
            "beta": 1.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": -0.1,
            "var_1d_95": -0.02,
            "var_1d_99": -0.03,
            "var_10d_95": -0.06,
            "var_10d_99": -0.09,
            "cvar_1d_95": -0.025,
            "cvar_1d_99": -0.035,
            "concentration_score": 50.0,
            "herfindahl_index": 0.2,
            "top_5_weight": 0.6,
            "avg_correlation": 0.3,
            "max_correlation": 0.7,
            "systematic_risk": 0.6,
            "idiosyncratic_risk": 0.4
        }

    # Stress Testing
    def _run_comprehensive_stress_tests(self, risk_profile_id: int,
                                      historical_data: pd.DataFrame,
                                      holdings: List[Holding]):
        """Run comprehensive stress tests on the portfolio"""
        try:
            stress_scenarios = [
                {
                    "type": StressTestScenario.MARKET_CRASH,
                    "name": "Market Crash (-30%)",
                    "description": "Broad market decline of 30%",
                    "parameters": {"market_shock": -0.30, "correlation_increase": 0.2}
                },
                {
                    "type": StressTestScenario.INTEREST_RATE_SHOCK,
                    "name": "Interest Rate Shock (+200bp)",
                    "description": "Interest rates increase by 200 basis points",
                    "parameters": {"rate_shock": 0.02, "duration_impact": -0.15}
                },
                {
                    "type": StressTestScenario.INFLATION_SPIKE,
                    "name": "Inflation Spike (+300bp)",
                    "description": "Inflation increases by 300 basis points",
                    "parameters": {"inflation_shock": 0.03, "real_return_impact": -0.20}
                },
                {
                    "type": StressTestScenario.CURRENCY_DEVALUATION,
                    "name": "Currency Devaluation (-15%)",
                    "description": "INR devaluation of 15% vs USD",
                    "parameters": {"currency_shock": -0.15, "import_impact": -0.10}
                },
                {
                    "type": StressTestScenario.LIQUIDITY_CRISIS,
                    "name": "Liquidity Crisis",
                    "description": "Market liquidity dries up, bid-ask spreads widen",
                    "parameters": {"liquidity_impact": -0.25, "volatility_spike": 2.0}
                }
            ]

            for scenario in stress_scenarios:
                try:
                    result = self._run_stress_test(
                        risk_profile_id, scenario, historical_data, holdings
                    )
                    self.db.add(result)
                except Exception as e:
                    logger.error(f"Failed to run stress test {scenario['name']}: {str(e)}")

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to run comprehensive stress tests: {str(e)}")

    def _run_stress_test(self, risk_profile_id: int, scenario: Dict[str, Any],
                        historical_data: pd.DataFrame, holdings: List[Holding]) -> StressTestResult:
        """Run individual stress test scenario"""
        try:
            # Calculate portfolio impact based on scenario
            portfolio_impact = self._calculate_scenario_impact(scenario, holdings)

            # Calculate stressed risk metrics
            stressed_metrics = self._calculate_stressed_metrics(
                historical_data, holdings, scenario
            )

            # Estimate recovery time
            recovery_days = self._estimate_recovery_time(scenario, portfolio_impact)

            # Calculate recovery probability
            recovery_probability = self._calculate_recovery_probability(
                scenario, portfolio_impact, recovery_days
            )

            # Calculate holding-level impacts
            holding_impacts = self._calculate_holding_impacts(scenario, holdings)

            # Calculate portfolio impact amount
            total_value = sum(h.current_value or 0 for h in holdings)
            impact_amount = total_value * (portfolio_impact / 100)

            return StressTestResult(
                risk_profile_id=risk_profile_id,
                scenario_type=scenario["type"],
                scenario_name=scenario["name"],
                scenario_description=scenario["description"],
                scenario_parameters=json.dumps(scenario["parameters"]),
                portfolio_impact_percentage=portfolio_impact,
                portfolio_impact_amount=impact_amount,
                stressed_volatility=stressed_metrics["volatility"],
                stressed_var_95=stressed_metrics["var_95"],
                stressed_var_99=stressed_metrics["var_99"],
                stressed_max_drawdown=stressed_metrics["max_drawdown"],
                estimated_recovery_days=recovery_days,
                recovery_probability=recovery_probability,
                holding_impacts=json.dumps(holding_impacts),
                test_date=datetime.now(),
                test_methodology="Scenario Analysis"
            )

        except Exception as e:
            logger.error(f"Failed to run stress test: {str(e)}")
            raise

    def _calculate_scenario_impact(self, scenario: Dict[str, Any],
                                 holdings: List[Holding]) -> float:
        """Calculate portfolio impact for a stress scenario"""
        try:
            scenario_type = scenario["type"]
            parameters = scenario["parameters"]

            if scenario_type == StressTestScenario.MARKET_CRASH:
                # Apply market shock with sector variations
                base_impact = parameters["market_shock"] * 100
                # Add some randomness based on portfolio composition
                return base_impact * (0.8 + 0.4 * np.random.random())

            elif scenario_type == StressTestScenario.INTEREST_RATE_SHOCK:
                # Impact varies by sector (banks benefit, utilities hurt)
                base_impact = parameters["duration_impact"] * 100
                return base_impact * (0.7 + 0.6 * np.random.random())

            elif scenario_type == StressTestScenario.INFLATION_SPIKE:
                # Real return impact
                base_impact = parameters["real_return_impact"] * 100
                return base_impact * (0.6 + 0.8 * np.random.random())

            elif scenario_type == StressTestScenario.CURRENCY_DEVALUATION:
                # Impact depends on export/import exposure
                base_impact = parameters["currency_shock"] * 100 * 0.5  # Assume 50% exposure
                return base_impact * (0.3 + 0.4 * np.random.random())

            elif scenario_type == StressTestScenario.LIQUIDITY_CRISIS:
                # Liquidity impact varies by stock size and trading volume
                base_impact = parameters["liquidity_impact"] * 100
                return base_impact * (0.5 + 1.0 * np.random.random())

            else:
                return -15.0  # Default 15% decline

        except Exception as e:
            logger.error(f"Failed to calculate scenario impact: {str(e)}")
            return -15.0

    def _calculate_stressed_metrics(self, historical_data: pd.DataFrame,
                                  holdings: List[Holding],
                                  scenario: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk metrics under stress"""
        try:
            # Get base metrics
            portfolio_returns = self._calculate_portfolio_returns(historical_data, holdings)

            if portfolio_returns.empty:
                return {
                    "volatility": 0.3,
                    "var_95": -0.04,
                    "var_99": -0.06,
                    "max_drawdown": -0.4
                }

            # Apply stress multipliers
            stress_multiplier = self._get_stress_multiplier(scenario)

            # Stressed volatility
            base_volatility = portfolio_returns.std() * np.sqrt(252)
            stressed_volatility = base_volatility * stress_multiplier

            # Stressed VaR (assume normal distribution under stress)
            stressed_var_95 = stats.norm.ppf(0.05, 0, stressed_volatility / np.sqrt(252))
            stressed_var_99 = stats.norm.ppf(0.01, 0, stressed_volatility / np.sqrt(252))

            # Stressed maximum drawdown
            base_max_dd = self._calculate_max_drawdown(portfolio_returns)
            stressed_max_drawdown = base_max_dd * stress_multiplier

            return {
                "volatility": stressed_volatility,
                "var_95": stressed_var_95,
                "var_99": stressed_var_99,
                "max_drawdown": stressed_max_drawdown
            }

        except Exception as e:
            logger.error(f"Failed to calculate stressed metrics: {str(e)}")
            return {
                "volatility": 0.3,
                "var_95": -0.04,
                "var_99": -0.06,
                "max_drawdown": -0.4
            }

    def _get_stress_multiplier(self, scenario: Dict[str, Any]) -> float:
        """Get stress multiplier for volatility calculations"""
        scenario_type = scenario["type"]

        multipliers = {
            StressTestScenario.MARKET_CRASH: 2.5,
            StressTestScenario.INTEREST_RATE_SHOCK: 1.8,
            StressTestScenario.INFLATION_SPIKE: 1.6,
            StressTestScenario.CURRENCY_DEVALUATION: 1.4,
            StressTestScenario.LIQUIDITY_CRISIS: 3.0
        }

        return multipliers.get(scenario_type, 2.0)

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown from returns series"""
        try:
            if returns.empty:
                return -0.2

            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdowns = (cumulative - rolling_max) / rolling_max
            return drawdowns.min()

        except Exception as e:
            logger.error(f"Failed to calculate max drawdown: {str(e)}")
            return -0.2

    def _estimate_recovery_time(self, scenario: Dict[str, Any], impact: float) -> int:
        """Estimate recovery time in days"""
        try:
            # Base recovery time based on impact severity
            base_days = abs(impact) * 10  # 10 days per 1% impact

            # Adjust based on scenario type
            scenario_type = scenario["type"]

            multipliers = {
                StressTestScenario.MARKET_CRASH: 1.5,
                StressTestScenario.INTEREST_RATE_SHOCK: 2.0,
                StressTestScenario.INFLATION_SPIKE: 2.5,
                StressTestScenario.CURRENCY_DEVALUATION: 1.8,
                StressTestScenario.LIQUIDITY_CRISIS: 3.0
            }

            multiplier = multipliers.get(scenario_type, 1.5)
            recovery_days = int(base_days * multiplier)

            return max(30, min(1095, recovery_days))  # Between 30 days and 3 years

        except Exception as e:
            logger.error(f"Failed to estimate recovery time: {str(e)}")
            return 365

    def _calculate_recovery_probability(self, scenario: Dict[str, Any],
                                      impact: float, recovery_days: int) -> float:
        """Calculate probability of recovery within estimated timeframe"""
        try:
            # Base probability decreases with impact severity
            base_probability = max(0.3, 1.0 - abs(impact) / 100)

            # Adjust based on recovery timeframe
            if recovery_days <= 90:
                time_factor = 1.2
            elif recovery_days <= 365:
                time_factor = 1.0
            elif recovery_days <= 730:
                time_factor = 0.8
            else:
                time_factor = 0.6

            # Adjust based on scenario type
            scenario_type = scenario["type"]

            scenario_factors = {
                StressTestScenario.MARKET_CRASH: 0.8,
                StressTestScenario.INTEREST_RATE_SHOCK: 0.7,
                StressTestScenario.INFLATION_SPIKE: 0.6,
                StressTestScenario.CURRENCY_DEVALUATION: 0.75,
                StressTestScenario.LIQUIDITY_CRISIS: 0.5
            }

            scenario_factor = scenario_factors.get(scenario_type, 0.7)

            probability = base_probability * time_factor * scenario_factor
            return max(0.1, min(0.95, probability))

        except Exception as e:
            logger.error(f"Failed to calculate recovery probability: {str(e)}")
            return 0.6

    def _calculate_holding_impacts(self, scenario: Dict[str, Any],
                                 holdings: List[Holding]) -> List[Dict[str, Any]]:
        """Calculate individual holding impacts under stress"""
        try:
            holding_impacts = []

            for holding in holdings:
                # Base impact varies by holding characteristics
                base_impact = self._get_holding_stress_impact(scenario, holding)

                # Add some randomness
                impact_variation = 0.8 + 0.4 * np.random.random()
                final_impact = base_impact * impact_variation

                holding_impacts.append({
                    "symbol": holding.symbol,
                    "name": holding.name,
                    "current_value": holding.current_value,
                    "impact_percentage": final_impact,
                    "impact_amount": (holding.current_value or 0) * (final_impact / 100),
                    "stressed_value": (holding.current_value or 0) * (1 + final_impact / 100)
                })

            return holding_impacts

        except Exception as e:
            logger.error(f"Failed to calculate holding impacts: {str(e)}")
            return []

    def _get_holding_stress_impact(self, scenario: Dict[str, Any], holding: Holding) -> float:
        """Get stress impact for individual holding"""
        try:
            scenario_type = scenario["type"]

            # This would ideally use sector/industry data
            # For now, use symbol-based heuristics
            symbol = holding.symbol.upper()

            if scenario_type == StressTestScenario.MARKET_CRASH:
                # Tech and growth stocks hit harder
                if any(tech in symbol for tech in ["TCS", "INFY", "WIPRO", "TECHM"]):
                    return -35.0
                elif any(bank in symbol for bank in ["HDFC", "ICICI", "AXIS", "SBI"]):
                    return -25.0
                else:
                    return -30.0

            elif scenario_type == StressTestScenario.INTEREST_RATE_SHOCK:
                # Banks benefit, utilities and REITs hurt
                if any(bank in symbol for bank in ["HDFC", "ICICI", "AXIS", "SBI"]):
                    return 10.0
                elif any(util in symbol for util in ["NTPC", "POWERGRID"]):
                    return -20.0
                else:
                    return -10.0

            else:
                return -15.0  # Default impact

        except Exception as e:
            logger.error(f"Failed to get holding stress impact: {str(e)}")
            return -15.0

    # Risk Alerts
    def _check_risk_alerts(self, risk_profile: PortfolioRiskProfile):
        """Check for risk alerts and create notifications"""
        try:
            alerts = []

            # High risk score alert
            if risk_profile.risk_score > 80:
                alerts.append({
                    "type": "high_risk_score",
                    "level": RiskLevel.HIGH,
                    "title": "High Portfolio Risk Detected",
                    "message": f"Portfolio risk score is {risk_profile.risk_score:.1f}, indicating high risk levels.",
                    "metric": "risk_score",
                    "threshold": 80,
                    "current": risk_profile.risk_score
                })

            # High volatility alert
            if risk_profile.portfolio_volatility and risk_profile.portfolio_volatility > 0.35:
                alerts.append({
                    "type": "high_volatility",
                    "level": RiskLevel.HIGH,
                    "title": "High Portfolio Volatility",
                    "message": f"Portfolio volatility is {risk_profile.portfolio_volatility:.1%}, above recommended levels.",
                    "metric": "volatility",
                    "threshold": 0.35,
                    "current": risk_profile.portfolio_volatility
                })

            # High concentration alert
            if risk_profile.concentration_score and risk_profile.concentration_score > 70:
                alerts.append({
                    "type": "high_concentration",
                    "level": RiskLevel.MODERATE,
                    "title": "High Portfolio Concentration",
                    "message": f"Portfolio concentration score is {risk_profile.concentration_score:.1f}, indicating lack of diversification.",
                    "metric": "concentration",
                    "threshold": 70,
                    "current": risk_profile.concentration_score
                })

            # Large drawdown alert
            if risk_profile.maximum_drawdown and risk_profile.maximum_drawdown < -0.25:
                alerts.append({
                    "type": "large_drawdown",
                    "level": RiskLevel.HIGH,
                    "title": "Large Maximum Drawdown",
                    "message": f"Maximum drawdown is {risk_profile.maximum_drawdown:.1%}, indicating high downside risk.",
                    "metric": "max_drawdown",
                    "threshold": -0.25,
                    "current": risk_profile.maximum_drawdown
                })

            # High correlation alert
            if risk_profile.avg_correlation and risk_profile.avg_correlation > 0.7:
                alerts.append({
                    "type": "high_correlation",
                    "level": RiskLevel.MODERATE,
                    "title": "High Asset Correlation",
                    "message": f"Average correlation is {risk_profile.avg_correlation:.2f}, reducing diversification benefits.",
                    "metric": "correlation",
                    "threshold": 0.7,
                    "current": risk_profile.avg_correlation
                })

            # Create alert records
            for alert_data in alerts:
                alert = RiskAlert(
                    user_id=risk_profile.user_id,
                    portfolio_id=risk_profile.portfolio_id,
                    risk_profile_id=risk_profile.id,
                    alert_type=alert_data["type"],
                    alert_level=alert_data["level"],
                    title=alert_data["title"],
                    message=alert_data["message"],
                    triggered_metric=alert_data["metric"],
                    threshold_value=alert_data["threshold"],
                    current_value=alert_data["current"],
                    recommended_actions=json.dumps(self._get_risk_recommendations(alert_data["type"]))
                )
                self.db.add(alert)

            if alerts:
                self.db.commit()
                logger.info(f"Created {len(alerts)} risk alerts for portfolio {risk_profile.portfolio_id}")

        except Exception as e:
            logger.error(f"Failed to check risk alerts: {str(e)}")

    def _get_risk_recommendations(self, alert_type: str) -> List[str]:
        """Get recommendations for risk alerts"""
        recommendations = {
            "high_risk_score": [
                "Consider reducing position sizes in high-risk assets",
                "Add defensive stocks or bonds to the portfolio",
                "Review and rebalance asset allocation",
                "Consider implementing stop-loss orders"
            ],
            "high_volatility": [
                "Diversify across different sectors and asset classes",
                "Consider adding low-volatility stocks",
                "Implement systematic rebalancing",
                "Review position sizing strategy"
            ],
            "high_concentration": [
                "Reduce position sizes in top holdings",
                "Add holdings from different sectors",
                "Consider index funds for instant diversification",
                "Implement maximum position size limits"
            ],
            "large_drawdown": [
                "Review risk management strategy",
                "Consider implementing stop-loss orders",
                "Reduce overall portfolio risk",
                "Add hedging instruments if available"
            ],
            "high_correlation": [
                "Add assets from different sectors/regions",
                "Consider alternative asset classes",
                "Review sector allocation",
                "Add international exposure if possible"
            ]
        }

        return recommendations.get(alert_type, ["Review portfolio risk management strategy"])

    # Helper Methods
    def _get_portfolio_historical_data(self, holdings: List[Holding],
                                     days: int) -> pd.DataFrame:
        """Get historical price data for portfolio holdings"""
        try:
            # This would typically fetch from market service
            # For now, generate mock data
            symbols = [h.symbol for h in holdings]
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

            # Generate mock returns data
            np.random.seed(42)  # For reproducible results
            data = {}

            for symbol in symbols:
                # Generate realistic daily returns
                returns = np.random.normal(0.0008, 0.02, days)  # ~20% annual vol, positive drift
                data[symbol] = returns

            return pd.DataFrame(data, index=dates)

        except Exception as e:
            logger.error(f"Failed to get historical data: {str(e)}")
            return pd.DataFrame()

    def _get_benchmark_returns(self, days: int) -> pd.Series:
        """Get benchmark returns (NIFTY)"""
        try:
            # Generate mock benchmark returns
            np.random.seed(123)  # Different seed for benchmark
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            returns = np.random.normal(0.0005, 0.015, days)  # ~15% annual vol

            return pd.Series(returns, index=dates)

        except Exception as e:
            logger.error(f"Failed to get benchmark returns: {str(e)}")
            return pd.Series()

    def _create_detailed_risk_metrics(self, risk_profile_id: int, metrics: Dict[str, float]):
        """Create detailed risk metric records"""
        try:
            metric_mappings = [
                ("volatility", RiskMetricType.VOLATILITY, "Annualized Portfolio Volatility"),
                ("beta", RiskMetricType.BETA, "Portfolio Beta vs NIFTY"),
                ("sharpe_ratio", RiskMetricType.SHARPE_RATIO, "Sharpe Ratio"),
                ("sortino_ratio", RiskMetricType.SORTINO_RATIO, "Sortino Ratio"),
                ("max_drawdown", RiskMetricType.MAXIMUM_DRAWDOWN, "Maximum Drawdown"),
                ("var_1d_99", RiskMetricType.VALUE_AT_RISK, "1-Day VaR (99%)"),
                ("cvar_1d_99", RiskMetricType.CONDITIONAL_VAR, "1-Day CVaR (99%)")
            ]

            for metric_key, metric_type, metric_name in metric_mappings:
                if metric_key in metrics:
                    risk_metric = RiskMetric(
                        risk_profile_id=risk_profile_id,
                        metric_type=metric_type,
                        metric_name=metric_name,
                        metric_value=metrics[metric_key],
                        calculation_date=datetime.now(),
                        data_quality_score=85.0  # Mock quality score
                    )
                    self.db.add(risk_metric)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to create detailed risk metrics: {str(e)}")

    # Public Methods for Risk Analysis
    def get_portfolio_risk_summary(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive risk summary for a portfolio"""
        try:
            risk_profile = self.get_portfolio_risk_profile(portfolio_id, user_id)

            if not risk_profile:
                return {"error": "No risk profile found"}

            # Get detailed metrics
            detailed_metrics = self.db.query(RiskMetric).filter(
                RiskMetric.risk_profile_id == risk_profile.id
            ).all()

            # Get stress test results
            stress_tests = self.db.query(StressTestResult).filter(
                StressTestResult.risk_profile_id == risk_profile.id
            ).all()

            # Get active alerts
            active_alerts = self.db.query(RiskAlert).filter(
                and_(
                    RiskAlert.risk_profile_id == risk_profile.id,
                    RiskAlert.is_resolved == False
                )
            ).all()

            return {
                "risk_profile": {
                    "overall_risk_level": risk_profile.overall_risk_level.value,
                    "risk_score": risk_profile.risk_score,
                    "assessment_date": risk_profile.assessment_date.isoformat(),
                    "portfolio_volatility": risk_profile.portfolio_volatility,
                    "portfolio_beta": risk_profile.portfolio_beta,
                    "sharpe_ratio": risk_profile.sharpe_ratio,
                    "maximum_drawdown": risk_profile.maximum_drawdown,
                    "var_1_day_99": risk_profile.var_1_day_99,
                    "concentration_score": risk_profile.concentration_score
                },
                "detailed_metrics": [
                    {
                        "metric_type": m.metric_type.value,
                        "metric_name": m.metric_name,
                        "metric_value": m.metric_value,
                        "calculation_date": m.calculation_date.isoformat()
                    } for m in detailed_metrics
                ],
                "stress_tests": [
                    {
                        "scenario_name": st.scenario_name,
                        "scenario_type": st.scenario_type.value,
                        "portfolio_impact_percentage": st.portfolio_impact_percentage,
                        "estimated_recovery_days": st.estimated_recovery_days,
                        "recovery_probability": st.recovery_probability
                    } for st in stress_tests
                ],
                "active_alerts": [
                    {
                        "alert_type": a.alert_type,
                        "alert_level": a.alert_level.value,
                        "title": a.title,
                        "message": a.message,
                        "created_at": a.created_at.isoformat()
                    } for a in active_alerts
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get risk summary: {str(e)}")
            raise

    def get_risk_alerts(self, user_id: int, portfolio_id: Optional[int] = None) -> List[RiskAlert]:
        """Get risk alerts for user or specific portfolio"""
        query = self.db.query(RiskAlert).filter(RiskAlert.user_id == user_id)

        if portfolio_id:
            query = query.filter(RiskAlert.portfolio_id == portfolio_id)

        return query.filter(RiskAlert.is_resolved == False).order_by(
            desc(RiskAlert.created_at)
        ).all()

    def acknowledge_risk_alert(self, alert_id: int, user_id: int) -> bool:
        """Acknowledge a risk alert"""
        try:
            alert = self.db.query(RiskAlert).filter(
                and_(RiskAlert.id == alert_id, RiskAlert.user_id == user_id)
            ).first()

            if not alert:
                return False

            alert.is_acknowledged = True
            alert.acknowledged_at = datetime.now()

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge risk alert: {str(e)}")
            return False
