"""
Risk Management Models - Advanced risk assessment and analytics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class RiskMetricType(enum.Enum):
    """Types of risk metrics"""
    VALUE_AT_RISK = "value_at_risk"
    CONDITIONAL_VAR = "conditional_var"
    MAXIMUM_DRAWDOWN = "maximum_drawdown"
    VOLATILITY = "volatility"
    BETA = "beta"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    INFORMATION_RATIO = "information_ratio"
    TRACKING_ERROR = "tracking_error"
    CORRELATION = "correlation"


class RiskLevel(enum.Enum):
    """Risk level classifications"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class StressTestScenario(enum.Enum):
    """Stress test scenario types"""
    MARKET_CRASH = "market_crash"
    INTEREST_RATE_SHOCK = "interest_rate_shock"
    INFLATION_SPIKE = "inflation_spike"
    CURRENCY_DEVALUATION = "currency_devaluation"
    SECTOR_CRISIS = "sector_crisis"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    GEOPOLITICAL_CRISIS = "geopolitical_crisis"
    CUSTOM_SCENARIO = "custom_scenario"


class PortfolioRiskProfile(Base):
    """Portfolio risk profile and assessment"""
    __tablename__ = "portfolio_risk_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Risk Assessment
    overall_risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_score = Column(Float, nullable=False)  # 0-100 scale
    
    # Risk Metrics
    portfolio_volatility = Column(Float)  # Annualized volatility
    portfolio_beta = Column(Float)  # Beta vs benchmark
    sharpe_ratio = Column(Float)  # Risk-adjusted returns
    sortino_ratio = Column(Float)  # Downside risk-adjusted returns
    maximum_drawdown = Column(Float)  # Maximum peak-to-trough decline
    
    # Value at Risk
    var_1_day_95 = Column(Float)  # 1-day VaR at 95% confidence
    var_1_day_99 = Column(Float)  # 1-day VaR at 99% confidence
    var_10_day_95 = Column(Float)  # 10-day VaR at 95% confidence
    var_10_day_99 = Column(Float)  # 10-day VaR at 99% confidence
    
    # Conditional VaR (Expected Shortfall)
    cvar_1_day_95 = Column(Float)  # 1-day CVaR at 95% confidence
    cvar_1_day_99 = Column(Float)  # 1-day CVaR at 99% confidence
    
    # Concentration Risk
    concentration_score = Column(Float)  # Concentration risk score
    herfindahl_index = Column(Float)  # Portfolio concentration index
    top_5_holdings_weight = Column(Float)  # Weight of top 5 holdings
    
    # Correlation Analysis
    avg_correlation = Column(Float)  # Average correlation between holdings
    max_correlation = Column(Float)  # Maximum correlation between holdings
    
    # Risk Attribution
    systematic_risk = Column(Float)  # Market risk component
    idiosyncratic_risk = Column(Float)  # Stock-specific risk component
    
    # Assessment metadata
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    data_period_days = Column(Integer, default=252)  # Data period used for calculation
    benchmark_symbol = Column(String(20), default="^NSEI")  # Benchmark used
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio")
    user = relationship("User")
    risk_metrics = relationship("RiskMetric", back_populates="risk_profile", cascade="all, delete-orphan")
    stress_tests = relationship("StressTestResult", back_populates="risk_profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PortfolioRiskProfile(id={self.id}, portfolio_id={self.portfolio_id}, risk_level='{self.overall_risk_level}')>"


class RiskMetric(Base):
    """Individual risk metrics for detailed analysis"""
    __tablename__ = "risk_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_profile_id = Column(Integer, ForeignKey("portfolio_risk_profiles.id"), nullable=False, index=True)
    
    # Metric details
    metric_type = Column(Enum(RiskMetricType), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_percentile = Column(Float)  # Percentile vs benchmark/universe
    
    # Calculation parameters
    calculation_method = Column(String(50))  # Method used for calculation
    confidence_level = Column(Float)  # For VaR/CVaR metrics
    time_horizon_days = Column(Integer)  # Time horizon for metric
    
    # Metadata
    calculation_date = Column(DateTime(timezone=True), nullable=False)
    data_quality_score = Column(Float)  # Quality of underlying data (0-100)
    
    # Additional context (JSON)
    metric_context = Column(Text)  # JSON with additional metric context
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    risk_profile = relationship("PortfolioRiskProfile", back_populates="risk_metrics")
    
    def __repr__(self):
        return f"<RiskMetric(id={self.id}, type='{self.metric_type}', value={self.metric_value})>"


class StressTestResult(Base):
    """Stress test results for portfolio scenarios"""
    __tablename__ = "stress_test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_profile_id = Column(Integer, ForeignKey("portfolio_risk_profiles.id"), nullable=False, index=True)
    
    # Scenario details
    scenario_type = Column(Enum(StressTestScenario), nullable=False)
    scenario_name = Column(String(100), nullable=False)
    scenario_description = Column(Text)
    
    # Scenario parameters (JSON)
    scenario_parameters = Column(Text)  # JSON with scenario parameters
    
    # Results
    portfolio_impact_percentage = Column(Float, nullable=False)  # Portfolio impact %
    portfolio_impact_amount = Column(Float, nullable=False)  # Portfolio impact amount
    
    # Risk metrics under stress
    stressed_volatility = Column(Float)
    stressed_var_95 = Column(Float)
    stressed_var_99 = Column(Float)
    stressed_max_drawdown = Column(Float)
    
    # Recovery analysis
    estimated_recovery_days = Column(Integer)
    recovery_probability = Column(Float)  # Probability of recovery within timeframe
    
    # Holding-level impacts (JSON)
    holding_impacts = Column(Text)  # JSON with individual holding impacts
    
    # Test metadata
    test_date = Column(DateTime(timezone=True), nullable=False)
    test_methodology = Column(String(50))  # Monte Carlo, Historical, etc.
    confidence_level = Column(Float, default=95.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    risk_profile = relationship("PortfolioRiskProfile", back_populates="stress_tests")
    
    def __repr__(self):
        return f"<StressTestResult(id={self.id}, scenario='{self.scenario_type}', impact={self.portfolio_impact_percentage}%)>"


class RiskAlert(Base):
    """Risk-related alerts and notifications"""
    __tablename__ = "risk_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    risk_profile_id = Column(Integer, ForeignKey("portfolio_risk_profiles.id"), index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # risk_limit_breach, correlation_spike, etc.
    alert_level = Column(Enum(RiskLevel), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Risk context
    triggered_metric = Column(String(50))  # Which metric triggered the alert
    threshold_value = Column(Float)  # Threshold that was breached
    current_value = Column(Float)  # Current value of the metric
    
    # Alert data (JSON)
    alert_data = Column(Text)  # JSON with additional alert data
    
    # Recommendations
    recommended_actions = Column(Text)  # JSON with recommended actions
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    portfolio = relationship("Portfolio")
    risk_profile = relationship("PortfolioRiskProfile")
    
    def __repr__(self):
        return f"<RiskAlert(id={self.id}, type='{self.alert_type}', level='{self.alert_level}')>"


class RiskBenchmark(Base):
    """Risk benchmarks for comparison and analysis"""
    __tablename__ = "risk_benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Benchmark details
    benchmark_name = Column(String(100), nullable=False)
    benchmark_symbol = Column(String(20), nullable=False, index=True)
    benchmark_type = Column(String(50), nullable=False)  # market_index, peer_group, etc.
    
    # Risk metrics
    volatility = Column(Float)
    beta = Column(Float, default=1.0)  # Beta is 1.0 for market benchmarks
    sharpe_ratio = Column(Float)
    maximum_drawdown = Column(Float)
    var_95 = Column(Float)
    var_99 = Column(Float)
    
    # Benchmark metadata
    data_start_date = Column(DateTime(timezone=True))
    data_end_date = Column(DateTime(timezone=True))
    data_frequency = Column(String(20), default="daily")  # daily, weekly, monthly
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RiskBenchmark(id={self.id}, name='{self.benchmark_name}', symbol='{self.benchmark_symbol}')>"
