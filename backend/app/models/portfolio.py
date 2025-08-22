"""
Portfolio and investment models for InvestAI application
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class AssetType(str, enum.Enum):
    """Asset type enumeration"""
    STOCK = "stock"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    BOND = "bond"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    CASH = "cash"
    OTHER = "other"


class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    BONUS = "bonus"
    SPLIT = "split"
    RIGHTS = "rights"


class Portfolio(Base):
    """Portfolio model"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Portfolio details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    
    # Portfolio metrics
    total_invested = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    total_returns = Column(Float, default=0.0)
    returns_percentage = Column(Float, default=0.0)
    
    # Risk metrics
    portfolio_beta = Column(Float)
    sharpe_ratio = Column(Float)
    volatility = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_rebalanced = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    @property
    def total_holdings_count(self) -> int:
        """Get total number of holdings"""
        return len(self.holdings) if self.holdings else 0
    
    @property
    def asset_allocation(self) -> dict:
        """Get asset allocation breakdown"""
        if not self.holdings:
            return {}
        
        allocation = {}
        total_value = sum(holding.current_value or 0 for holding in self.holdings)
        
        if total_value == 0:
            return {}
        
        for holding in self.holdings:
            asset_type = holding.asset_type
            current_value = holding.current_value or 0
            percentage = (current_value / total_value) * 100
            
            if asset_type in allocation:
                allocation[asset_type] += percentage
            else:
                allocation[asset_type] = percentage
        
        return allocation


class Holding(Base):
    """Individual holding within a portfolio"""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Asset details
    symbol = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    exchange = Column(String(10))  # NSE, BSE, etc.
    
    # Holding details
    quantity = Column(Float, nullable=False, default=0.0)
    average_price = Column(Float, nullable=False, default=0.0)
    current_price = Column(Float, default=0.0)
    
    # Calculated values
    invested_amount = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_percentage = Column(Float, default=0.0)
    
    # Additional metrics
    day_change = Column(Float, default=0.0)
    day_change_percentage = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_price_update = Column(DateTime(timezone=True))
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    transactions = relationship("Transaction", back_populates="holding", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Holding(id={self.id}, symbol='{self.symbol}', quantity={self.quantity})>"
    
    def update_metrics(self):
        """Update calculated metrics based on current price"""
        if self.quantity and self.average_price:
            self.invested_amount = self.quantity * self.average_price
            
            if self.current_price:
                self.current_value = self.quantity * self.current_price
                self.unrealized_pnl = self.current_value - self.invested_amount
                
                if self.invested_amount > 0:
                    self.unrealized_pnl_percentage = (self.unrealized_pnl / self.invested_amount) * 100


class Transaction(Base):
    """Transaction model for buy/sell activities"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    holding_id = Column(Integer, ForeignKey("holdings.id"), index=True)
    
    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    symbol = Column(String(50), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Fees and charges
    brokerage = Column(Float, default=0.0)
    taxes = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    
    # Transaction metadata
    exchange = Column(String(10))
    order_id = Column(String(100))
    trade_id = Column(String(100))
    notes = Column(Text)
    
    # Timestamps
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    portfolio = relationship("Portfolio", back_populates="transactions")
    holding = relationship("Holding", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type}', symbol='{self.symbol}')>"


class PortfolioSnapshot(Base):
    """Portfolio snapshot for historical tracking"""
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)

    # Snapshot data
    snapshot_date = Column(DateTime(timezone=True), nullable=False)
    total_invested = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    total_returns = Column(Float, nullable=False)
    returns_percentage = Column(Float, nullable=False)

    # Risk metrics at snapshot
    portfolio_beta = Column(Float)
    sharpe_ratio = Column(Float)
    volatility = Column(Float)

    # Asset allocation at snapshot (JSON)
    asset_allocation = Column(Text)  # JSON string

    # Holdings count
    holdings_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    portfolio = relationship("Portfolio")

    def __repr__(self):
        return f"<PortfolioSnapshot(id={self.id}, portfolio_id={self.portfolio_id}, date={self.snapshot_date})>"


class Watchlist(Base):
    """User watchlist for tracking potential investments"""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Watchlist details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    watchlist_items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Watchlist(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class WatchlistItem(Base):
    """Individual item in a watchlist"""
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False, index=True)

    # Asset details
    symbol = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    exchange = Column(String(10))

    # Price tracking
    added_price = Column(Float)  # Price when added to watchlist
    current_price = Column(Float)
    target_price = Column(Float)  # User's target price
    stop_loss = Column(Float)    # User's stop loss

    # Alerts
    price_alert_enabled = Column(Boolean, default=False)
    price_alert_threshold = Column(Float)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_price_update = Column(DateTime(timezone=True))

    # Relationships
    watchlist = relationship("Watchlist", back_populates="watchlist_items")

    def __repr__(self):
        return f"<WatchlistItem(id={self.id}, symbol='{self.symbol}', watchlist_id={self.watchlist_id})>"


class PortfolioAlert(Base):
    """Portfolio alerts and notifications"""
    __tablename__ = "portfolio_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)

    # Alert details
    alert_type = Column(String(50), nullable=False)  # price_change, portfolio_loss, rebalance_needed, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # info, warning, critical

    # Alert data (JSON)
    alert_data = Column(Text)  # JSON string with additional data

    # Status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User")
    portfolio = relationship("Portfolio")

    def __repr__(self):
        return f"<PortfolioAlert(id={self.id}, type='{self.alert_type}', user_id={self.user_id})>"
