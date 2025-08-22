"""
Market Service - Real-time market data and analysis
"""

from typing import Dict, List, Any, Optional
import yfinance as yf
import requests
from datetime import datetime, timedelta
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

logger = logging.getLogger(__name__)


class MarketService:
    """Service for market data operations"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = 300  # 5 minutes cache
    
    def get_current_price(self, symbol: str, exchange: str = "NSE") -> Optional[Dict[str, Any]]:
        """Get current price for a symbol"""
        try:
            cache_key = f"{symbol}_{exchange}_current"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Convert to Yahoo Finance format
            yf_symbol = self._get_yahoo_symbol(symbol, exchange)
            ticker = yf.Ticker(yf_symbol)
            
            # Get current data
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', hist['Close'].iloc[-1])
            
            market_data = {
                "symbol": symbol,
                "exchange": exchange,
                "current_price": float(current_price),
                "previous_close": float(previous_close),
                "open_price": float(hist['Open'].iloc[-1]),
                "high_price": float(hist['High'].iloc[-1]),
                "low_price": float(hist['Low'].iloc[-1]),
                "volume": int(hist['Volume'].iloc[-1]),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "pb_ratio": info.get('priceToBook'),
                "dividend_yield": info.get('dividendYield'),
                "week_52_high": info.get('fiftyTwoWeekHigh'),
                "week_52_low": info.get('fiftyTwoWeekLow'),
                "last_updated": datetime.now().isoformat()
            }
            
            # Calculate price change
            if previous_close and previous_close > 0:
                price_change = current_price - previous_close
                price_change_percentage = (price_change / previous_close) * 100
                market_data.update({
                    "price_change": float(price_change),
                    "price_change_percentage": float(price_change_percentage)
                })
            
            # Cache the result
            self._cache_data(cache_key, market_data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, exchange: str = "NSE", 
                          period: str = "1y") -> Optional[pd.DataFrame]:
        """Get historical price data"""
        try:
            cache_key = f"{symbol}_{exchange}_hist_{period}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            yf_symbol = self._get_yahoo_symbol(symbol, exchange)
            ticker = yf.Ticker(yf_symbol)
            
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"No historical data found for {symbol}")
                return None
            
            # Cache the result
            self._cache_data(cache_key, hist)
            
            return hist
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {str(e)}")
            return None
    
    def get_multiple_prices(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, Any]:
        """Get current prices for multiple symbols"""
        try:
            results = {}
            
            # Use ThreadPoolExecutor for parallel requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_symbol = {
                    executor.submit(self.get_current_price, symbol, exchange): symbol 
                    for symbol in symbols
                }
                
                for future in future_to_symbol:
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result(timeout=30)
                        results[symbol] = result
                    except Exception as e:
                        logger.error(f"Failed to get price for {symbol}: {str(e)}")
                        results[symbol] = None
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get multiple prices: {str(e)}")
            return {}
    
    def get_market_indices(self) -> Dict[str, Any]:
        """Get major Indian market indices"""
        try:
            indices = {
                "NIFTY50": "^NSEI",
                "SENSEX": "^BSESN",
                "NIFTY_BANK": "^NSEBANK",
                "NIFTY_IT": "^CNXIT",
                "NIFTY_PHARMA": "^CNXPHARMA"
            }
            
            results = {}
            
            for index_name, yahoo_symbol in indices.items():
                try:
                    ticker = yf.Ticker(yahoo_symbol)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_value = hist['Close'].iloc[-1]
                        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_value
                        
                        change = current_value - previous_close
                        change_percentage = (change / previous_close) * 100 if previous_close > 0 else 0
                        
                        results[index_name] = {
                            "value": float(current_value),
                            "change": float(change),
                            "change_percentage": float(change_percentage),
                            "high": float(hist['High'].iloc[-1]),
                            "low": float(hist['Low'].iloc[-1]),
                            "volume": int(hist['Volume'].iloc[-1]),
                            "last_updated": datetime.now().isoformat()
                        }
                    
                except Exception as e:
                    logger.error(f"Failed to get data for {index_name}: {str(e)}")
                    results[index_name] = None
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get market indices: {str(e)}")
            return {}
    
    def search_symbols(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for stock symbols"""
        try:
            # This is a simplified search - in production, you'd use a proper API
            # For now, we'll return some common Indian stocks that match the query
            
            common_stocks = [
                {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "exchange": "NSE"},
                {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "exchange": "NSE"},
                {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "exchange": "NSE"},
                {"symbol": "INFY", "name": "Infosys Ltd", "exchange": "NSE"},
                {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "exchange": "NSE"},
                {"symbol": "ITC", "name": "ITC Ltd", "exchange": "NSE"},
                {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "exchange": "NSE"},
                {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd", "exchange": "NSE"},
                {"symbol": "LT", "name": "Larsen & Toubro Ltd", "exchange": "NSE"},
                {"symbol": "AXISBANK", "name": "Axis Bank Ltd", "exchange": "NSE"},
                {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "exchange": "NSE"},
                {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd", "exchange": "NSE"},
                {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "exchange": "NSE"},
                {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Ltd", "exchange": "NSE"},
                {"symbol": "TITAN", "name": "Titan Company Ltd", "exchange": "NSE"}
            ]
            
            # Filter based on query
            query_lower = query.lower()
            results = []
            
            for stock in common_stocks:
                if (query_lower in stock["symbol"].lower() or 
                    query_lower in stock["name"].lower()):
                    results.append(stock)
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search symbols: {str(e)}")
            return []
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector-wise performance"""
        try:
            # Sector indices mapping
            sectors = {
                "Banking": "^NSEBANK",
                "IT": "^CNXIT",
                "Pharma": "^CNXPHARMA",
                "FMCG": "^CNXFMCG",
                "Auto": "^CNXAUTO",
                "Metal": "^CNXMETAL",
                "Energy": "^CNXENERGY",
                "Realty": "^CNXREALTY"
            }
            
            results = {}
            
            for sector_name, yahoo_symbol in sectors.items():
                try:
                    ticker = yf.Ticker(yahoo_symbol)
                    hist = ticker.history(period="5d")  # Get 5 days for better comparison
                    
                    if len(hist) >= 2:
                        current_value = hist['Close'].iloc[-1]
                        previous_value = hist['Close'].iloc[-2]
                        
                        change = current_value - previous_value
                        change_percentage = (change / previous_value) * 100 if previous_value > 0 else 0
                        
                        # Calculate weekly performance
                        week_start_value = hist['Close'].iloc[0]
                        week_change = current_value - week_start_value
                        week_change_percentage = (week_change / week_start_value) * 100 if week_start_value > 0 else 0
                        
                        results[sector_name] = {
                            "current_value": float(current_value),
                            "day_change": float(change),
                            "day_change_percentage": float(change_percentage),
                            "week_change": float(week_change),
                            "week_change_percentage": float(week_change_percentage),
                            "last_updated": datetime.now().isoformat()
                        }
                    
                except Exception as e:
                    logger.error(f"Failed to get data for sector {sector_name}: {str(e)}")
                    results[sector_name] = None
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get sector performance: {str(e)}")
            return {}
    
    def get_top_gainers_losers(self, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Get top gainers and losers (simplified version)"""
        try:
            # In a real implementation, this would fetch from NSE/BSE APIs
            # For now, we'll return mock data structure
            
            return {
                "top_gainers": [
                    {
                        "symbol": "EXAMPLE1",
                        "name": "Example Company 1",
                        "current_price": 1250.50,
                        "change": 125.25,
                        "change_percentage": 11.13,
                        "volume": 1500000
                    }
                ],
                "top_losers": [
                    {
                        "symbol": "EXAMPLE2", 
                        "name": "Example Company 2",
                        "current_price": 850.25,
                        "change": -95.75,
                        "change_percentage": -10.13,
                        "volume": 2000000
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get top gainers/losers: {str(e)}")
            return {"top_gainers": [], "top_losers": []}
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        try:
            now = datetime.now()
            
            # Indian market hours: 9:15 AM to 3:30 PM IST, Monday to Friday
            market_open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
            
            is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6
            is_market_hours = market_open_time <= now <= market_close_time
            
            if is_weekend:
                status = "CLOSED"
                message = "Market is closed (Weekend)"
            elif is_market_hours:
                status = "OPEN"
                message = "Market is open"
            else:
                status = "CLOSED"
                if now < market_open_time:
                    message = f"Market opens at {market_open_time.strftime('%H:%M')}"
                else:
                    message = f"Market closed at {market_close_time.strftime('%H:%M')}"
            
            return {
                "status": status,
                "message": message,
                "market_open_time": market_open_time.strftime('%H:%M'),
                "market_close_time": market_close_time.strftime('%H:%M'),
                "current_time": now.strftime('%Y-%m-%d %H:%M:%S'),
                "is_trading_day": not is_weekend
            }
            
        except Exception as e:
            logger.error(f"Failed to get market status: {str(e)}")
            return {"status": "UNKNOWN", "message": "Unable to determine market status"}
    
    # Helper methods
    def _get_yahoo_symbol(self, symbol: str, exchange: str) -> str:
        """Convert Indian stock symbol to Yahoo Finance format"""
        if exchange.upper() == "NSE":
            return f"{symbol}.NS"
        elif exchange.upper() == "BSE":
            return f"{symbol}.BO"
        else:
            return symbol
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]["timestamp"]
        return (datetime.now() - cached_time).seconds < self.cache_duration
    
    def _cache_data(self, cache_key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("Market data cache cleared")
