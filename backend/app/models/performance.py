"""
Performance Analytics Models - Comprehensive performance tracking and analytics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class PerformancePeriod(enum.Enum):
    """Performance measurement periods"""
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"
    THREE_YEARS = "3y"
    FIVE_YEARS = "5y"
    INCEPTION = "inception"


class BenchmarkType(enum.Enum):
    """Types of benchmarks"""
    MARKET_INDEX = "market_index"
    SECTOR_INDEX = "sector_index"
    PEER_GROUP = "peer_group"
    CUSTOM_BENCHMARK = "custom_benchmark"
    RISK_FREE_RATE = "risk_free_rate"


class AttributionType(enum.Enum):
    """Performance attribution types"""
    ASSET_ALLOCATION = "asset_allocation"
    SECURITY_SELECTION = "security_selection"
    INTERACTION_EFFECT = "interaction_effect"
    CURRENCY_EFFECT = "currency_effect"
    TIMING_EFFECT = "timing_effect"


class ReportType(enum.Enum):
    """Performance report types"""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_REPORT = "monthly_report"
    QUARTERLY_REPORT = "quarterly_report"
    ANNUAL_REPORT = "annual_report"
    CUSTOM_REPORT = "custom_report"


class PortfolioPerformance(Base):
    """Portfolio performance tracking and analytics"""
    __tablename__ = "portfolio_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Performance date
    performance_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Portfolio values
    portfolio_value = Column(Float, nullable=False)
    invested_amount = Column(Float, nullable=False)
    cash_balance = Column(Float, default=0)
    
    # Absolute returns
    absolute_return = Column(Float, nullable=False)  # Total return amount
    absolute_return_percentage = Column(Float, nullable=False)  # Total return %
    
    # Period returns
    day_return = Column(Float, default=0)
    day_return_percentage = Column(Float, default=0)
    week_return = Column(Float, default=0)
    week_return_percentage = Column(Float, default=0)
    month_return = Column(Float, default=0)
    month_return_percentage = Column(Float, default=0)
    quarter_return = Column(Float, default=0)
    quarter_return_percentage = Column(Float, default=0)
    year_return = Column(Float, default=0)
    year_return_percentage = Column(Float, default=0)
    
    # Annualized metrics
    annualized_return = Column(Float)
    annualized_volatility = Column(Float)
    
    # Risk-adjusted returns
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    calmar_ratio = Column(Float)
    information_ratio = Column(Float)
    
    # Drawdown metrics
    current_drawdown = Column(Float, default=0)
    maximum_drawdown = Column(Float, default=0)
    drawdown_duration_days = Column(Integer, default=0)
    
    # Portfolio metrics
    portfolio_beta = Column(Float)
    portfolio_alpha = Column(Float)
    tracking_error = Column(Float)
    r_squared = Column(Float)
    
    # Benchmark comparison
    benchmark_return = Column(Float)
    excess_return = Column(Float)
    outperformance = Column(Boolean, default=False)
    
    # Holdings count and diversification
    holdings_count = Column(Integer, default=0)
    concentration_ratio = Column(Float, default=0)  # Top 5 holdings weight
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio")
    user = relationship("User")
    attribution_analysis = relationship("AttributionAnalysis", back_populates="performance", cascade="all, delete-orphan")
    benchmark_comparisons = relationship("BenchmarkComparison", back_populates="performance", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PortfolioPerformance(id={self.id}, portfolio_id={self.portfolio_id}, return={self.absolute_return_percentage:.2f}%)>"


class BenchmarkComparison(Base):
    """Benchmark comparison and analysis"""
    __tablename__ = "benchmark_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("portfolio_performance.id"), nullable=False, index=True)
    
    # Benchmark details
    benchmark_type = Column(Enum(BenchmarkType), nullable=False)
    benchmark_name = Column(String(100), nullable=False)
    benchmark_symbol = Column(String(20), nullable=False)
    
    # Benchmark performance
    benchmark_return = Column(Float, nullable=False)
    benchmark_volatility = Column(Float)
    benchmark_sharpe_ratio = Column(Float)
    benchmark_max_drawdown = Column(Float)
    
    # Comparison metrics
    excess_return = Column(Float, nullable=False)  # Portfolio - Benchmark
    tracking_error = Column(Float)  # Volatility of excess returns
    information_ratio = Column(Float)  # Excess return / Tracking error
    
    # Relative performance
    beta = Column(Float)  # Portfolio sensitivity to benchmark
    alpha = Column(Float)  # Risk-adjusted excess return
    r_squared = Column(Float)  # Correlation coefficient squared
    
    # Up/Down market analysis
    up_market_capture = Column(Float)  # Performance in rising markets
    down_market_capture = Column(Float)  # Performance in falling markets
    
    # Performance periods
    period_type = Column(Enum(PerformancePeriod), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    performance = relationship("PortfolioPerformance", back_populates="benchmark_comparisons")
    
    def __repr__(self):
        return f"<BenchmarkComparison(id={self.id}, benchmark='{self.benchmark_name}', excess_return={self.excess_return:.2f}%)>"


class AttributionAnalysis(Base):
    """Performance attribution analysis"""
    __tablename__ = "attribution_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("portfolio_performance.id"), nullable=False, index=True)
    
    # Attribution details
    attribution_type = Column(Enum(AttributionType), nullable=False)
    attribution_name = Column(String(100), nullable=False)
    
    # Attribution values
    attribution_return = Column(Float, nullable=False)  # Contribution to return
    attribution_percentage = Column(Float, nullable=False)  # % of total return
    
    # Sector/Asset class breakdown
    sector_name = Column(String(50))
    asset_class = Column(String(50))
    
    # Security-level attribution
    security_symbol = Column(String(50))
    security_name = Column(String(255))
    security_weight = Column(Float)
    security_return = Column(Float)
    security_contribution = Column(Float)
    
    # Benchmark comparison
    benchmark_weight = Column(Float)
    benchmark_return = Column(Float)
    active_weight = Column(Float)  # Portfolio weight - Benchmark weight
    
    # Attribution components
    allocation_effect = Column(Float, default=0)  # Asset allocation impact
    selection_effect = Column(Float, default=0)  # Security selection impact
    interaction_effect = Column(Float, default=0)  # Interaction between allocation and selection
    
    # Analysis period
    analysis_period = Column(Enum(PerformancePeriod), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    performance = relationship("PortfolioPerformance", back_populates="attribution_analysis")
    
    def __repr__(self):
        return f"<AttributionAnalysis(id={self.id}, type='{self.attribution_type}', return={self.attribution_return:.2f}%)>"


class PerformanceReport(Base):
    """Generated performance reports"""
    __tablename__ = "performance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    
    # Report details
    report_type = Column(Enum(ReportType), nullable=False)
    report_title = Column(String(255), nullable=False)
    report_description = Column(Text)
    
    # Report period
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Report data (JSON)
    report_data = Column(Text, nullable=False)  # JSON with complete report data
    
    # Report metadata
    total_portfolios = Column(Integer, default=1)
    total_value = Column(Float)
    total_return = Column(Float)
    best_performer = Column(String(255))
    worst_performer = Column(String(255))
    
    # Report status
    is_generated = Column(Boolean, default=False)
    generation_date = Column(DateTime(timezone=True))
    is_shared = Column(Boolean, default=False)
    share_token = Column(String(100))
    
    # File information
    file_path = Column(String(500))  # Path to generated PDF/Excel file
    file_size = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    portfolio = relationship("Portfolio")
    
    def __repr__(self):
        return f"<PerformanceReport(id={self.id}, type='{self.report_type}', title='{self.report_title}')>"


class PerformanceBenchmark(Base):
    """Performance benchmarks and indices"""
    __tablename__ = "performance_benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Benchmark details
    benchmark_name = Column(String(100), nullable=False)
    benchmark_symbol = Column(String(20), nullable=False, unique=True, index=True)
    benchmark_type = Column(Enum(BenchmarkType), nullable=False)
    
    # Benchmark characteristics
    description = Column(Text)
    asset_class = Column(String(50))
    geography = Column(String(50), default="India")
    currency = Column(String(10), default="INR")
    
    # Performance data
    current_value = Column(Float)
    day_change = Column(Float, default=0)
    day_change_percentage = Column(Float, default=0)
    
    # Historical performance
    week_return = Column(Float, default=0)
    month_return = Column(Float, default=0)
    quarter_return = Column(Float, default=0)
    year_return = Column(Float, default=0)
    three_year_return = Column(Float, default=0)
    five_year_return = Column(Float, default=0)
    
    # Risk metrics
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    maximum_drawdown = Column(Float)
    
    # Benchmark metadata
    inception_date = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True))
    data_provider = Column(String(50))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PerformanceBenchmark(id={self.id}, name='{self.benchmark_name}', symbol='{self.benchmark_symbol}')>"


class PerformanceAlert(Base):
    """Performance-related alerts and notifications"""
    __tablename__ = "performance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # underperformance, milestone, etc.
    alert_title = Column(String(255), nullable=False)
    alert_message = Column(Text, nullable=False)
    
    # Performance context
    triggered_metric = Column(String(50))  # Which metric triggered the alert
    threshold_value = Column(Float)  # Threshold that was breached
    current_value = Column(Float)  # Current value of the metric
    
    # Alert severity
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Alert data (JSON)
    alert_data = Column(Text)  # JSON with additional alert data
    
    # Status
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    portfolio = relationship("Portfolio")
    
    def __repr__(self):
        return f"<PerformanceAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
