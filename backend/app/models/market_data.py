"""
Market Data Models - Real-time market data for NSE/BSE stocks, mutual funds, and other securities
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class SecurityType(enum.Enum):
    """Types of securities"""
    EQUITY = "equity"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    BOND = "bond"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    INDEX = "index"
    DERIVATIVE = "derivative"


class Exchange(enum.Enum):
    """Stock exchanges"""
    NSE = "nse"
    BSE = "bse"
    MCX = "mcx"
    NCDEX = "ncdex"


class MarketStatus(enum.Enum):
    """Market status"""
    OPEN = "open"
    CLOSED = "closed"
    PRE_OPEN = "pre_open"
    POST_CLOSE = "post_close"
    HOLIDAY = "holiday"


class DataSource(enum.Enum):
    """Data source providers"""
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    NSE_API = "nse_api"
    BSE_API = "bse_api"
    MUTUAL_FUND_API = "mutual_fund_api"
    INTERNAL = "internal"


class Security(Base):
    """Master security information"""
    __tablename__ = "securities"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    symbol = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    isin = Column(String(20), unique=True, index=True)

    # Classification
    security_type = Column(Enum(SecurityType), nullable=False, index=True)
    exchange = Column(Enum(Exchange), nullable=False, index=True)
    sector = Column(String(100))
    industry = Column(String(100))

    # Trading information
    lot_size = Column(Integer, default=1)
    tick_size = Column(Float, default=0.05)
    face_value = Column(Float)
    market_cap = Column(Float)

    # Status
    is_active = Column(Boolean, default=True)
    is_tradable = Column(Boolean, default=True)
    listing_date = Column(DateTime(timezone=True))
    delisting_date = Column(DateTime(timezone=True))

    # Additional information
    description = Column(Text)
    website = Column(String(255))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    price_data = relationship("PriceData", back_populates="security", cascade="all, delete-orphan")
    historical_data = relationship("HistoricalData", back_populates="security", cascade="all, delete-orphan")
    fundamental_data = relationship("FundamentalData", back_populates="security", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_security_symbol_exchange', 'symbol', 'exchange'),
        Index('idx_security_type_active', 'security_type', 'is_active'),
    )

    def __repr__(self):
        return f"<Security(id={self.id}, symbol='{self.symbol}', exchange='{self.exchange.value}')>"


class PriceData(Base):
    """Real-time price data"""
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False, index=True)

    # Price information
    current_price = Column(Float, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    previous_close = Column(Float)

    # Change metrics
    price_change = Column(Float)
    price_change_percent = Column(Float)

    # Volume information
    volume = Column(Integer, default=0)
    value = Column(Float, default=0)  # Volume * Price
    average_price = Column(Float)

    # Market depth (Level 1)
    bid_price = Column(Float)
    bid_quantity = Column(Integer)
    ask_price = Column(Float)
    ask_quantity = Column(Integer)

    # Additional metrics
    vwap = Column(Float)  # Volume Weighted Average Price
    total_traded_quantity = Column(Integer)
    total_traded_value = Column(Float)

    # 52-week data
    week_52_high = Column(Float)
    week_52_low = Column(Float)

    # Market status
    market_status = Column(Enum(MarketStatus), default=MarketStatus.CLOSED)
    last_trade_time = Column(DateTime(timezone=True))

    # Data source and quality
    data_source = Column(Enum(DataSource), nullable=False)
    data_quality_score = Column(Float, default=1.0)  # 0-1 score

    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    security = relationship("Security", back_populates="price_data")

    # Indexes
    __table_args__ = (
        Index('idx_price_security_timestamp', 'security_id', 'timestamp'),
        Index('idx_price_timestamp', 'timestamp'),
    )

    @property
    def is_data_stale(self) -> bool:
        """Check if market data is stale (older than 15 minutes during trading hours)"""
        if not self.timestamp:
            return True

        time_diff = datetime.utcnow() - self.timestamp.replace(tzinfo=None)
        return time_diff.total_seconds() > 900  # 15 minutes

    def __repr__(self):
        return f"<PriceData(id={self.id}, security_id={self.security_id}, price={self.current_price})>"


class HistoricalData(Base):
    """Historical price data (OHLCV)"""
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False, index=True)

    # Date and timeframe
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, default="1D")  # 1D, 1H, 5M, etc.

    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, default=0)

    # Additional metrics
    adjusted_close = Column(Float)  # Adjusted for splits/dividends
    vwap = Column(Float)
    trades_count = Column(Integer)

    # Data source
    data_source = Column(Enum(DataSource), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    security = relationship("Security", back_populates="historical_data")

    # Indexes
    __table_args__ = (
        Index('idx_historical_security_date', 'security_id', 'date'),
        Index('idx_historical_date_timeframe', 'date', 'timeframe'),
    )

    def __repr__(self):
        return f"<HistoricalData(id={self.id}, security_id={self.security_id}, date={self.date}, close={self.close_price})>"


class FundamentalData(Base):
    """Fundamental data for securities"""
    __tablename__ = "fundamental_data"

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False, index=True)

    # Financial metrics
    market_cap = Column(Float)
    enterprise_value = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    dividend_yield = Column(Float)

    # Profitability ratios
    roe = Column(Float)  # Return on Equity
    roa = Column(Float)  # Return on Assets
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)

    # Liquidity ratios
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    debt_to_equity = Column(Float)

    # Growth metrics
    revenue_growth = Column(Float)
    earnings_growth = Column(Float)
    book_value_per_share = Column(Float)

    # Per share metrics
    eps = Column(Float)  # Earnings Per Share
    book_value = Column(Float)
    sales_per_share = Column(Float)

    # Analyst data
    analyst_rating = Column(String(20))  # Buy, Hold, Sell
    target_price = Column(Float)
    analyst_count = Column(Integer)

    # AI analysis
    fundamental_score = Column(Float)  # AI-generated fundamental score (0-100)
    technical_score = Column(Float)   # AI-generated technical score (0-100)
    overall_rating = Column(String(10))  # BUY, HOLD, SELL
    ai_analysis_summary = Column(Text)

    # Risk metrics
    beta = Column(Float)
    volatility = Column(Float)

    # Data period
    period_type = Column(String(20))  # Annual, Quarterly
    period_end_date = Column(DateTime(timezone=True))

    # Data source
    data_source = Column(Enum(DataSource), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_analysis_date = Column(DateTime(timezone=True))

    # Relationships
    security = relationship("Security", back_populates="fundamental_data")

    # Indexes
    __table_args__ = (
        Index('idx_fundamental_security_period', 'security_id', 'period_end_date'),
    )

    def __repr__(self):
        return f"<FundamentalData(id={self.id}, security_id={self.security_id}, pe_ratio={self.pe_ratio})>"


class MutualFundData(Base):
    """Mutual fund specific data"""
    __tablename__ = "mutual_fund_data"

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False, index=True)

    # Fund information
    fund_house = Column(String(255))
    fund_manager = Column(String(255))
    fund_category = Column(String(100))
    fund_type = Column(String(50))  # Equity, Debt, Hybrid, etc.

    # NAV information
    nav = Column(Float, nullable=False)
    nav_date = Column(DateTime(timezone=True), nullable=False)

    # Fund metrics
    aum = Column(Float)  # Assets Under Management
    expense_ratio = Column(Float)
    exit_load = Column(Float)
    minimum_investment = Column(Float)

    # Performance metrics
    returns_1d = Column(Float)
    returns_1w = Column(Float)
    returns_1m = Column(Float)
    returns_3m = Column(Float)
    returns_6m = Column(Float)
    returns_1y = Column(Float)
    returns_3y = Column(Float)
    returns_5y = Column(Float)

    # Risk metrics
    standard_deviation = Column(Float)
    sharpe_ratio = Column(Float)
    beta = Column(Float)
    alpha = Column(Float)

    # Ratings
    crisil_rating = Column(String(10))
    morningstar_rating = Column(Integer)  # 1-5 stars

    # AI analysis
    ai_recommendation = Column(String(10))  # BUY, HOLD, SELL
    risk_score = Column(Float)  # 0-100
    suitability_score = Column(Float)  # 0-100
    ai_analysis_summary = Column(Text)

    # Portfolio composition (top holdings)
    top_holdings = Column(Text)  # JSON string
    sector_allocation = Column(Text)  # JSON string

    # Data source
    data_source = Column(Enum(DataSource), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_analysis_date = Column(DateTime(timezone=True))

    # Relationships
    security = relationship("Security")

    # Indexes
    __table_args__ = (
        Index('idx_mf_security_nav_date', 'security_id', 'nav_date'),
        Index('idx_mf_category_type', 'fund_category', 'fund_type'),
    )

    @property
    def is_equity_fund(self) -> bool:
        """Check if this is an equity fund"""
        return self.fund_category and "equity" in self.fund_category.lower()

    @property
    def is_debt_fund(self) -> bool:
        """Check if this is a debt fund"""
        return self.fund_category and "debt" in self.fund_category.lower()

    def __repr__(self):
        return f"<MutualFundData(id={self.id}, security_id={self.security_id}, nav={self.nav})>"


class MarketIndex(Base):
    """Market indices data"""
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, index=True)

    # Index information
    index_name = Column(String(100), nullable=False, unique=True)
    index_code = Column(String(50), nullable=False, unique=True)
    exchange = Column(Enum(Exchange), nullable=False)

    # Current values
    current_value = Column(Float, nullable=False)
    previous_close = Column(Float)
    change = Column(Float)
    change_percent = Column(Float)

    # Daily metrics
    day_high = Column(Float)
    day_low = Column(Float)

    # 52-week metrics
    week_52_high = Column(Float)
    week_52_low = Column(Float)

    # Market status
    market_status = Column(Enum(MarketStatus), default=MarketStatus.CLOSED)
    last_updated = Column(DateTime(timezone=True))

    # Data source
    data_source = Column(Enum(DataSource), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_index_code_exchange', 'index_code', 'exchange'),
    )

    def __repr__(self):
        return f"<MarketIndex(id={self.id}, name='{self.index_name}', value={self.current_value})>"


class DataFeed(Base):
    """Data feed configuration and status"""
    __tablename__ = "data_feeds"

    id = Column(Integer, primary_key=True, index=True)

    # Feed information
    feed_name = Column(String(100), nullable=False, unique=True)
    data_source = Column(Enum(DataSource), nullable=False)
    feed_type = Column(String(50), nullable=False)  # real_time, historical, fundamental

    # Configuration
    api_endpoint = Column(String(500))
    api_key_required = Column(Boolean, default=False)
    rate_limit = Column(Integer)  # Requests per minute

    # Status
    is_active = Column(Boolean, default=True)
    last_successful_update = Column(DateTime(timezone=True))
    last_error = Column(Text)
    error_count = Column(Integer, default=0)

    # Performance metrics
    success_rate = Column(Float, default=1.0)
    average_response_time = Column(Float)  # in seconds

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DataFeed(id={self.id}, name='{self.feed_name}', source='{self.data_source.value}')>"
