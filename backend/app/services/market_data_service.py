"""
Market Data Service - Real-time market data integration with Redis caching
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging
import asyncio
import aiohttp
import redis
from decimal import Decimal

from app.models.market_data import (
    Security, PriceData, HistoricalData, FundamentalData, MutualFundData,
    MarketIndex, DataFeed, SecurityType, Exchange, MarketStatus, DataSource
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for real-time market data integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            decode_responses=True
        )
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    # Security Management
    def create_security(self, security_data: Dict[str, Any]) -> Security:
        """Create a new security"""
        try:
            security = Security(
                symbol=security_data["symbol"].upper(),
                name=security_data["name"],
                isin=security_data.get("isin"),
                security_type=SecurityType(security_data["security_type"]),
                exchange=Exchange(security_data["exchange"]),
                sector=security_data.get("sector"),
                industry=security_data.get("industry"),
                lot_size=security_data.get("lot_size", 1),
                tick_size=security_data.get("tick_size", 0.05),
                face_value=security_data.get("face_value"),
                market_cap=security_data.get("market_cap"),
                listing_date=security_data.get("listing_date"),
                description=security_data.get("description"),
                website=security_data.get("website")
            )
            
            self.db.add(security)
            self.db.commit()
            self.db.refresh(security)
            
            logger.info(f"Created security {security.symbol} ({security.id})")
            return security
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create security: {str(e)}")
            raise
    
    def get_security(self, symbol: str, exchange: str) -> Optional[Security]:
        """Get security by symbol and exchange"""
        return self.db.query(Security).filter(
            and_(
                Security.symbol == symbol.upper(),
                Security.exchange == Exchange(exchange.lower()),
                Security.is_active == True
            )
        ).first()
    
    def search_securities(self, query: str, security_type: Optional[str] = None,
                         exchange: Optional[str] = None, limit: int = 50) -> List[Security]:
        """Search securities by name or symbol"""
        search_filter = or_(
            Security.symbol.ilike(f"%{query.upper()}%"),
            Security.name.ilike(f"%{query}%")
        )
        
        query_obj = self.db.query(Security).filter(
            and_(
                search_filter,
                Security.is_active == True
            )
        )
        
        if security_type:
            query_obj = query_obj.filter(Security.security_type == SecurityType(security_type))
        
        if exchange:
            query_obj = query_obj.filter(Security.exchange == Exchange(exchange))
        
        return query_obj.limit(limit).all()
    
    # Real-time Price Data
    def update_price_data(self, symbol: str, exchange: str, price_data: Dict[str, Any]) -> PriceData:
        """Update real-time price data"""
        try:
            security = self.get_security(symbol, exchange)
            if not security:
                raise ValueError(f"Security {symbol} not found on {exchange}")
            
            # Create new price data record
            price_record = PriceData(
                security_id=security.id,
                current_price=float(price_data["current_price"]),
                open_price=price_data.get("open_price"),
                high_price=price_data.get("high_price"),
                low_price=price_data.get("low_price"),
                previous_close=price_data.get("previous_close"),
                volume=price_data.get("volume", 0),
                value=price_data.get("value", 0),
                average_price=price_data.get("average_price"),
                bid_price=price_data.get("bid_price"),
                bid_quantity=price_data.get("bid_quantity"),
                ask_price=price_data.get("ask_price"),
                ask_quantity=price_data.get("ask_quantity"),
                vwap=price_data.get("vwap"),
                total_traded_quantity=price_data.get("total_traded_quantity"),
                total_traded_value=price_data.get("total_traded_value"),
                week_52_high=price_data.get("week_52_high"),
                week_52_low=price_data.get("week_52_low"),
                market_status=MarketStatus(price_data.get("market_status", "closed")),
                last_trade_time=price_data.get("last_trade_time"),
                data_source=DataSource(price_data.get("data_source", "internal")),
                data_quality_score=price_data.get("data_quality_score", 1.0)
            )
            
            # Calculate change metrics
            if price_record.previous_close and price_record.previous_close > 0:
                price_record.price_change = price_record.current_price - price_record.previous_close
                price_record.price_change_percent = (price_record.price_change / price_record.previous_close) * 100
            
            self.db.add(price_record)
            self.db.commit()
            self.db.refresh(price_record)
            
            # Cache the latest price data
            self._cache_price_data(symbol, exchange, price_record)
            
            logger.info(f"Updated price data for {symbol} ({exchange}): ₹{price_record.current_price}")
            return price_record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update price data for {symbol}: {str(e)}")
            raise
    
    def get_latest_price(self, symbol: str, exchange: str) -> Optional[PriceData]:
        """Get latest price data for a security"""
        # Try cache first
        cached_data = self._get_cached_price_data(symbol, exchange)
        if cached_data:
            return cached_data
        
        # Fallback to database
        security = self.get_security(symbol, exchange)
        if not security:
            return None
        
        price_data = self.db.query(PriceData).filter(
            PriceData.security_id == security.id
        ).order_by(desc(PriceData.timestamp)).first()
        
        if price_data:
            self._cache_price_data(symbol, exchange, price_data)
        
        return price_data
    
    def get_multiple_prices(self, symbols: List[Tuple[str, str]]) -> Dict[str, PriceData]:
        """Get latest prices for multiple securities"""
        results = {}
        
        for symbol, exchange in symbols:
            price_data = self.get_latest_price(symbol, exchange)
            if price_data:
                results[f"{symbol}:{exchange}"] = price_data
        
        return results
    
    # Historical Data
    def add_historical_data(self, symbol: str, exchange: str, 
                           historical_data: List[Dict[str, Any]]) -> List[HistoricalData]:
        """Add historical price data"""
        try:
            security = self.get_security(symbol, exchange)
            if not security:
                raise ValueError(f"Security {symbol} not found on {exchange}")
            
            records = []
            for data_point in historical_data:
                record = HistoricalData(
                    security_id=security.id,
                    date=data_point["date"],
                    timeframe=data_point.get("timeframe", "1D"),
                    open_price=float(data_point["open"]),
                    high_price=float(data_point["high"]),
                    low_price=float(data_point["low"]),
                    close_price=float(data_point["close"]),
                    volume=data_point.get("volume", 0),
                    adjusted_close=data_point.get("adjusted_close"),
                    vwap=data_point.get("vwap"),
                    trades_count=data_point.get("trades_count"),
                    data_source=DataSource(data_point.get("data_source", "internal"))
                )
                records.append(record)
            
            self.db.add_all(records)
            self.db.commit()
            
            logger.info(f"Added {len(records)} historical data points for {symbol}")
            return records
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add historical data for {symbol}: {str(e)}")
            raise
    
    def get_historical_data(self, symbol: str, exchange: str, 
                           start_date: datetime, end_date: datetime,
                           timeframe: str = "1D") -> List[HistoricalData]:
        """Get historical data for a security"""
        security = self.get_security(symbol, exchange)
        if not security:
            return []
        
        return self.db.query(HistoricalData).filter(
            and_(
                HistoricalData.security_id == security.id,
                HistoricalData.timeframe == timeframe,
                HistoricalData.date >= start_date,
                HistoricalData.date <= end_date
            )
        ).order_by(HistoricalData.date).all()
    
    # Fundamental Data
    def update_fundamental_data(self, symbol: str, exchange: str, 
                               fundamental_data: Dict[str, Any]) -> FundamentalData:
        """Update fundamental data for a security"""
        try:
            security = self.get_security(symbol, exchange)
            if not security:
                raise ValueError(f"Security {symbol} not found on {exchange}")
            
            # Check if fundamental data already exists for this period
            existing_data = self.db.query(FundamentalData).filter(
                and_(
                    FundamentalData.security_id == security.id,
                    FundamentalData.period_end_date == fundamental_data.get("period_end_date")
                )
            ).first()
            
            if existing_data:
                # Update existing record
                for key, value in fundamental_data.items():
                    if hasattr(existing_data, key) and value is not None:
                        setattr(existing_data, key, value)
                record = existing_data
            else:
                # Create new record
                record = FundamentalData(
                    security_id=security.id,
                    **fundamental_data
                )
                self.db.add(record)
            
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"Updated fundamental data for {symbol}")
            return record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update fundamental data for {symbol}: {str(e)}")
            raise
    
    def get_fundamental_data(self, symbol: str, exchange: str) -> Optional[FundamentalData]:
        """Get latest fundamental data for a security"""
        security = self.get_security(symbol, exchange)
        if not security:
            return None
        
        return self.db.query(FundamentalData).filter(
            FundamentalData.security_id == security.id
        ).order_by(desc(FundamentalData.period_end_date)).first()
    
    # Market Indices
    def update_market_index(self, index_data: Dict[str, Any]) -> MarketIndex:
        """Update market index data"""
        try:
            # Check if index exists
            index = self.db.query(MarketIndex).filter(
                MarketIndex.index_code == index_data["index_code"]
            ).first()
            
            if index:
                # Update existing index
                for key, value in index_data.items():
                    if hasattr(index, key) and value is not None:
                        setattr(index, key, value)
            else:
                # Create new index
                index = MarketIndex(**index_data)
                self.db.add(index)
            
            index.last_updated = datetime.now()
            
            self.db.commit()
            self.db.refresh(index)
            
            # Cache index data
            self._cache_index_data(index)
            
            logger.info(f"Updated market index {index.index_name}: {index.current_value}")
            return index
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update market index: {str(e)}")
            raise
    
    def get_market_indices(self, exchange: Optional[str] = None) -> List[MarketIndex]:
        """Get market indices"""
        query = self.db.query(MarketIndex)
        
        if exchange:
            query = query.filter(MarketIndex.exchange == Exchange(exchange))
        
        return query.order_by(MarketIndex.index_name).all()
    
    # Cache Management
    def _cache_price_data(self, symbol: str, exchange: str, price_data: PriceData):
        """Cache price data in Redis"""
        try:
            cache_key = f"price:{symbol}:{exchange}"
            cache_data = {
                "current_price": price_data.current_price,
                "price_change": price_data.price_change,
                "price_change_percent": price_data.price_change_percent,
                "volume": price_data.volume,
                "market_status": price_data.market_status.value if price_data.market_status else "closed",
                "timestamp": price_data.timestamp.isoformat(),
                "last_trade_time": price_data.last_trade_time.isoformat() if price_data.last_trade_time else None
            }
            
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache price data: {str(e)}")
    
    def _get_cached_price_data(self, symbol: str, exchange: str) -> Optional[Dict[str, Any]]:
        """Get cached price data from Redis"""
        try:
            cache_key = f"price:{symbol}:{exchange}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
        except Exception as e:
            logger.warning(f"Failed to get cached price data: {str(e)}")
        
        return None
    
    def _cache_index_data(self, index: MarketIndex):
        """Cache market index data"""
        try:
            cache_key = f"index:{index.index_code}"
            cache_data = {
                "index_name": index.index_name,
                "current_value": index.current_value,
                "change": index.change,
                "change_percent": index.change_percent,
                "market_status": index.market_status.value if index.market_status else "closed",
                "last_updated": index.last_updated.isoformat() if index.last_updated else None
            }
            
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache index data: {str(e)}")
    
    # Market Status
    def get_market_status(self, exchange: str) -> MarketStatus:
        """Get current market status for an exchange"""
        # This would implement actual market hours logic
        # For now, return a simple time-based status
        
        current_time = datetime.now().time()
        
        # NSE/BSE trading hours: 9:15 AM to 3:30 PM IST
        if exchange.lower() in ["nse", "bse"]:
            if current_time >= datetime.strptime("09:15", "%H:%M").time() and \
               current_time <= datetime.strptime("15:30", "%H:%M").time():
                return MarketStatus.OPEN
            elif current_time >= datetime.strptime("09:00", "%H:%M").time() and \
                 current_time < datetime.strptime("09:15", "%H:%M").time():
                return MarketStatus.PRE_OPEN
            else:
                return MarketStatus.CLOSED
        
        return MarketStatus.CLOSED
    
    # Data Quality and Monitoring
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Get data quality report"""
        try:
            # Count securities by type
            security_counts = self.db.query(
                Security.security_type,
                func.count(Security.id).label('count')
            ).filter(Security.is_active == True).group_by(Security.security_type).all()
            
            # Count recent price updates
            recent_cutoff = datetime.now() - timedelta(hours=1)
            recent_updates = self.db.query(PriceData).filter(
                PriceData.timestamp >= recent_cutoff
            ).count()
            
            # Data feed status
            active_feeds = self.db.query(DataFeed).filter(DataFeed.is_active == True).count()
            
            return {
                "security_counts": {st.value: count for st, count in security_counts},
                "recent_price_updates": recent_updates,
                "active_data_feeds": active_feeds,
                "cache_status": self._get_cache_status(),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate data quality report: {str(e)}")
            return {}
    
    def _get_cache_status(self) -> Dict[str, Any]:
        """Get Redis cache status"""
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
