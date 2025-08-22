"""
Market Data endpoints - Real-time market data and analysis
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.market_data_service import MarketDataService

router = APIRouter()


# Pydantic models
class SymbolSearch(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")


class MultipleSymbolsRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of symbols")
    exchange: str = Field(default="NSE", description="Exchange")


class SecurityCreate(BaseModel):
    symbol: str = Field(..., max_length=50, description="Security symbol")
    name: str = Field(..., max_length=255, description="Security name")
    isin: Optional[str] = Field(None, max_length=20, description="ISIN code")
    security_type: str = Field(..., description="Security type: equity, mutual_fund, etf, bond, etc.")
    exchange: str = Field(..., description="Exchange: nse, bse, mcx, ncdex")
    sector: Optional[str] = Field(None, max_length=100, description="Sector")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    lot_size: int = Field(1, ge=1, description="Lot size")
    tick_size: float = Field(0.05, gt=0, description="Tick size")
    face_value: Optional[float] = Field(None, gt=0, description="Face value")
    market_cap: Optional[float] = Field(None, gt=0, description="Market capitalization")
    listing_date: Optional[datetime] = Field(None, description="Listing date")
    description: Optional[str] = Field(None, description="Security description")
    website: Optional[str] = Field(None, description="Company website")


class PriceDataUpdate(BaseModel):
    current_price: float = Field(..., gt=0, description="Current price")
    open_price: Optional[float] = Field(None, gt=0, description="Opening price")
    high_price: Optional[float] = Field(None, gt=0, description="Day high price")
    low_price: Optional[float] = Field(None, gt=0, description="Day low price")
    previous_close: Optional[float] = Field(None, gt=0, description="Previous close price")
    volume: Optional[int] = Field(None, ge=0, description="Volume traded")
    value: Optional[float] = Field(None, ge=0, description="Value traded")
    average_price: Optional[float] = Field(None, gt=0, description="Average price")
    bid_price: Optional[float] = Field(None, gt=0, description="Bid price")
    bid_quantity: Optional[int] = Field(None, ge=0, description="Bid quantity")
    ask_price: Optional[float] = Field(None, gt=0, description="Ask price")
    ask_quantity: Optional[int] = Field(None, ge=0, description="Ask quantity")
    vwap: Optional[float] = Field(None, gt=0, description="Volume weighted average price")
    week_52_high: Optional[float] = Field(None, gt=0, description="52-week high")
    week_52_low: Optional[float] = Field(None, gt=0, description="52-week low")
    market_status: str = Field("closed", description="Market status")
    last_trade_time: Optional[datetime] = Field(None, description="Last trade time")
    data_source: str = Field("internal", description="Data source")
    data_quality_score: float = Field(1.0, ge=0, le=1, description="Data quality score")


@router.get("/current-price/{symbol}", response_model=Dict[str, Any])
async def get_current_price(
    symbol: str,
    exchange: str = Query("nse", description="Exchange (nse/bse)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current price for a symbol"""
    try:
        market_service = MarketDataService(db)
        price_data = market_service.get_latest_price(symbol, exchange)

        if not price_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Price data not found for {symbol} on {exchange.upper()}"
            )

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "exchange": exchange.upper(),
                "current_price": price_data.current_price,
                "price_change": price_data.price_change,
                "price_change_percent": price_data.price_change_percent,
                "open_price": price_data.open_price,
                "high_price": price_data.high_price,
                "low_price": price_data.low_price,
                "previous_close": price_data.previous_close,
                "volume": price_data.volume,
                "vwap": price_data.vwap,
                "week_52_high": price_data.week_52_high,
                "week_52_low": price_data.week_52_low,
                "market_status": price_data.market_status.value if price_data.market_status else "closed",
                "last_trade_time": price_data.last_trade_time.isoformat() if price_data.last_trade_time else None,
                "timestamp": price_data.timestamp.isoformat(),
                "data_quality_score": price_data.data_quality_score,
                "is_stale": price_data.is_data_stale
            },
            "message": f"Current price retrieved for {symbol}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current price: {str(e)}"
        )


@router.post("/multiple-prices", response_model=Dict[str, Any])
async def get_multiple_prices(
    request: MultipleSymbolsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current prices for multiple symbols"""
    try:
        market_service = MarketDataService(db)
        # Prepare symbol-exchange pairs
        symbol_pairs = [(symbol, request.exchange.lower()) for symbol in request.symbols]
        prices_data = market_service.get_multiple_prices(symbol_pairs)

        # Convert to expected format
        prices = {}
        for symbol in request.symbols:
            key = f"{symbol}:{request.exchange.lower()}"
            if key in prices_data:
                price_data = prices_data[key]
                prices[symbol] = {
                    "current_price": price_data.current_price,
                    "price_change": price_data.price_change,
                    "price_change_percent": price_data.price_change_percent,
                    "volume": price_data.volume
                }
            else:
                prices[symbol] = None
        
        return {
            "status": "success",
            "data": {
                "prices": prices,
                "symbols_requested": len(request.symbols),
                "symbols_found": len([p for p in prices.values() if p is not None])
            },
            "message": f"Retrieved prices for {len(request.symbols)} symbols"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get multiple prices: {str(e)}"
        )


@router.get("/historical/{symbol}", response_model=Dict[str, Any])
async def get_historical_data(
    symbol: str,
    exchange: str = Query("NSE", description="Exchange (NSE/BSE)"),
    period: str = Query("1y", description="Period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get historical price data for a symbol"""
    try:
        market_service = MarketDataService(db)
        # Convert period to date range
        end_date = datetime.now()
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "5d":
            start_date = end_date - timedelta(days=5)
        elif period == "1mo":
            start_date = end_date - timedelta(days=30)
        elif period == "3mo":
            start_date = end_date - timedelta(days=90)
        elif period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)  # Default to 1 year

        hist_data = market_service.get_historical_data(symbol, exchange.lower(), start_date, end_date, "1D")
        
        if hist_data is None or hist_data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Historical data not found for {symbol}"
            )
        
        # Convert DataFrame to list of dictionaries
        historical_data = []
        for date, row in hist_data.iterrows():
            historical_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "exchange": exchange,
                "period": period,
                "data_points": len(historical_data),
                "historical_data": historical_data
            },
            "message": f"Historical data retrieved for {symbol}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get historical data: {str(e)}"
        )


@router.get("/indices", response_model=Dict[str, Any])
async def get_market_indices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get major Indian market indices"""
    try:
        market_service = MarketService()
        indices = market_service.get_market_indices()
        
        return {
            "status": "success",
            "data": {
                "indices": indices,
                "count": len(indices)
            },
            "message": f"Retrieved {len(indices)} market indices"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market indices: {str(e)}"
        )


@router.post("/search", response_model=Dict[str, Any])
async def search_symbols(
    search_request: SymbolSearch,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Search for stock symbols"""
    try:
        market_service = MarketService()
        results = market_service.search_symbols(search_request.query, search_request.limit)
        
        return {
            "status": "success",
            "data": {
                "query": search_request.query,
                "results": results,
                "count": len(results)
            },
            "message": f"Found {len(results)} symbols matching '{search_request.query}'"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search symbols: {str(e)}"
        )


@router.get("/sectors", response_model=Dict[str, Any])
async def get_sector_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get sector-wise performance"""
    try:
        market_service = MarketService()
        sectors = market_service.get_sector_performance()
        
        return {
            "status": "success",
            "data": {
                "sectors": sectors,
                "count": len(sectors)
            },
            "message": f"Retrieved performance for {len(sectors)} sectors"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sector performance: {str(e)}"
        )


# New Enhanced Endpoints
@router.post("/securities", response_model=Dict[str, Any])
async def create_security(
    security_data: SecurityCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new security"""
    try:
        market_service = MarketDataService(db)
        security = market_service.create_security(security_data.dict())

        return {
            "status": "success",
            "data": {
                "id": security.id,
                "symbol": security.symbol,
                "name": security.name,
                "security_type": security.security_type.value,
                "exchange": security.exchange.value,
                "sector": security.sector,
                "industry": security.industry,
                "created_at": security.created_at.isoformat()
            },
            "message": f"Security {security.symbol} created successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create security: {str(e)}"
        )


@router.get("/securities/search", response_model=Dict[str, Any])
async def search_securities(
    query: str = Query(..., min_length=1, description="Search query"),
    security_type: Optional[str] = Query(None, description="Filter by security type"),
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Search securities by name or symbol"""
    try:
        market_service = MarketDataService(db)
        securities = market_service.search_securities(query, security_type, exchange, limit)

        securities_data = []
        for security in securities:
            securities_data.append({
                "id": security.id,
                "symbol": security.symbol,
                "name": security.name,
                "isin": security.isin,
                "security_type": security.security_type.value,
                "exchange": security.exchange.value,
                "sector": security.sector,
                "industry": security.industry,
                "market_cap": security.market_cap,
                "listing_date": security.listing_date.isoformat() if security.listing_date else None
            })

        return {
            "status": "success",
            "data": {
                "securities": securities_data,
                "count": len(securities_data),
                "query": query
            },
            "message": f"Found {len(securities_data)} securities matching '{query}'"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search securities: {str(e)}"
        )


@router.put("/price/{symbol}", response_model=Dict[str, Any])
async def update_price_data(
    symbol: str,
    price_data: PriceDataUpdate,
    exchange: str = Query("nse", description="Exchange"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update real-time price data for a security"""
    try:
        market_service = MarketDataService(db)
        updated_price = market_service.update_price_data(symbol, exchange, price_data.dict())

        return {
            "status": "success",
            "data": {
                "id": updated_price.id,
                "symbol": symbol,
                "exchange": exchange.upper(),
                "current_price": updated_price.current_price,
                "price_change": updated_price.price_change,
                "price_change_percent": updated_price.price_change_percent,
                "volume": updated_price.volume,
                "market_status": updated_price.market_status.value,
                "timestamp": updated_price.timestamp.isoformat(),
                "data_source": updated_price.data_source.value
            },
            "message": f"Price data updated for {symbol}"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update price data: {str(e)}"
        )


@router.get("/historical/{symbol}", response_model=Dict[str, Any])
async def get_historical_data(
    symbol: str,
    exchange: str = Query("nse", description="Exchange"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    timeframe: str = Query("1D", description="Timeframe (1D, 1H, 5M)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get historical price data for a security"""
    try:
        market_service = MarketDataService(db)
        historical_data = market_service.get_historical_data(symbol, exchange, start_date, end_date, timeframe)

        data_points = []
        for data in historical_data:
            data_points.append({
                "date": data.date.isoformat(),
                "open": data.open_price,
                "high": data.high_price,
                "low": data.low_price,
                "close": data.close_price,
                "volume": data.volume,
                "adjusted_close": data.adjusted_close,
                "vwap": data.vwap
            })

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "exchange": exchange.upper(),
                "timeframe": timeframe,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "data_points": data_points,
                "count": len(data_points)
            },
            "message": f"Retrieved {len(data_points)} historical data points for {symbol}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get historical data: {str(e)}"
        )


@router.get("/indices", response_model=Dict[str, Any])
async def get_market_indices(
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get market indices"""
    try:
        market_service = MarketDataService(db)
        indices = market_service.get_market_indices(exchange)

        indices_data = []
        for index in indices:
            indices_data.append({
                "id": index.id,
                "index_name": index.index_name,
                "index_code": index.index_code,
                "exchange": index.exchange.value,
                "current_value": index.current_value,
                "previous_close": index.previous_close,
                "change": index.change,
                "change_percent": index.change_percent,
                "day_high": index.day_high,
                "day_low": index.day_low,
                "week_52_high": index.week_52_high,
                "week_52_low": index.week_52_low,
                "market_status": index.market_status.value if index.market_status else "closed",
                "last_updated": index.last_updated.isoformat() if index.last_updated else None
            })

        return {
            "status": "success",
            "data": {
                "indices": indices_data,
                "count": len(indices_data),
                "exchange_filter": exchange
            },
            "message": f"Retrieved {len(indices_data)} market indices"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market indices: {str(e)}"
        )


@router.get("/fundamental/{symbol}", response_model=Dict[str, Any])
async def get_fundamental_data(
    symbol: str,
    exchange: str = Query("nse", description="Exchange"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get fundamental data for a security"""
    try:
        market_service = MarketDataService(db)
        fundamental_data = market_service.get_fundamental_data(symbol, exchange)

        if not fundamental_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fundamental data not found for {symbol} on {exchange.upper()}"
            )

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "exchange": exchange.upper(),
                "market_cap": fundamental_data.market_cap,
                "pe_ratio": fundamental_data.pe_ratio,
                "pb_ratio": fundamental_data.pb_ratio,
                "dividend_yield": fundamental_data.dividend_yield,
                "roe": fundamental_data.roe,
                "roa": fundamental_data.roa,
                "debt_to_equity": fundamental_data.debt_to_equity,
                "current_ratio": fundamental_data.current_ratio,
                "eps": fundamental_data.eps,
                "book_value": fundamental_data.book_value,
                "revenue_growth": fundamental_data.revenue_growth,
                "earnings_growth": fundamental_data.earnings_growth,
                "beta": fundamental_data.beta,
                "volatility": fundamental_data.volatility,
                "analyst_rating": fundamental_data.analyst_rating,
                "target_price": fundamental_data.target_price,
                "fundamental_score": fundamental_data.fundamental_score,
                "technical_score": fundamental_data.technical_score,
                "overall_rating": fundamental_data.overall_rating,
                "ai_analysis_summary": fundamental_data.ai_analysis_summary,
                "period_end_date": fundamental_data.period_end_date.isoformat() if fundamental_data.period_end_date else None,
                "last_updated": fundamental_data.updated_at.isoformat() if fundamental_data.updated_at else None
            },
            "message": f"Fundamental data retrieved for {symbol}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fundamental data: {str(e)}"
        )


@router.get("/market-status/{exchange}", response_model=Dict[str, Any])
async def get_market_status(
    exchange: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current market status for an exchange"""
    try:
        market_service = MarketDataService(db)
        market_status = market_service.get_market_status(exchange)

        return {
            "status": "success",
            "data": {
                "exchange": exchange.upper(),
                "market_status": market_status.value,
                "timestamp": datetime.now().isoformat()
            },
            "message": f"Market status retrieved for {exchange.upper()}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market status: {str(e)}"
        )


@router.get("/data-quality", response_model=Dict[str, Any])
async def get_data_quality_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get data quality report"""
    try:
        market_service = MarketDataService(db)
        quality_report = market_service.get_data_quality_report()

        return {
            "status": "success",
            "data": {
                "data_quality_report": quality_report,
                "report_type": "market_data_quality",
                "generated_at": quality_report.get("generated_at", datetime.now().isoformat())
            },
            "message": "Data quality report generated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate data quality report: {str(e)}"
        )


@router.post("/bulk-prices", response_model=Dict[str, Any])
async def get_bulk_prices(
    symbols_request: MultipleSymbolsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get prices for multiple securities"""
    try:
        market_service = MarketDataService(db)

        # Prepare symbol-exchange pairs
        symbol_pairs = [(symbol, symbols_request.exchange.lower()) for symbol in symbols_request.symbols]

        # Get multiple prices
        prices_data = market_service.get_multiple_prices(symbol_pairs)

        bulk_prices = []
        for symbol in symbols_request.symbols:
            key = f"{symbol}:{symbols_request.exchange.lower()}"
            if key in prices_data:
                price_data = prices_data[key]
                bulk_prices.append({
                    "symbol": symbol,
                    "exchange": symbols_request.exchange.upper(),
                    "current_price": price_data.current_price,
                    "price_change": price_data.price_change,
                    "price_change_percent": price_data.price_change_percent,
                    "volume": price_data.volume,
                    "market_status": price_data.market_status.value if price_data.market_status else "closed",
                    "timestamp": price_data.timestamp.isoformat(),
                    "is_stale": price_data.is_data_stale
                })
            else:
                bulk_prices.append({
                    "symbol": symbol,
                    "exchange": symbols_request.exchange.upper(),
                    "error": "Price data not available"
                })

        return {
            "status": "success",
            "data": {
                "prices": bulk_prices,
                "requested_count": len(symbols_request.symbols),
                "found_count": len([p for p in bulk_prices if "error" not in p]),
                "exchange": symbols_request.exchange.upper()
            },
            "message": f"Retrieved prices for {len([p for p in bulk_prices if 'error' not in p])} out of {len(symbols_request.symbols)} symbols"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bulk prices: {str(e)}"
        )


@router.get("/top-movers", response_model=Dict[str, Any])
async def get_top_gainers_losers(
    limit: int = Query(10, ge=1, le=50, description="Number of stocks to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get top gainers and losers"""
    try:
        market_service = MarketService()
        movers = market_service.get_top_gainers_losers(limit)
        
        return {
            "status": "success",
            "data": movers,
            "message": f"Retrieved top {limit} gainers and losers"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top movers: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_market_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current market status"""
    try:
        market_service = MarketDataService(db)
        status_info = {
            "nse": market_service.get_market_status("nse").value,
            "bse": market_service.get_market_status("bse").value,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "data": status_info,
            "message": "Market status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market status: {str(e)}"
        )


@router.get("/quote/{symbol}", response_model=Dict[str, Any])
async def get_detailed_quote(
    symbol: str,
    exchange: str = Query("NSE", description="Exchange (NSE/BSE)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed quote with additional metrics"""
    try:
        market_service = MarketDataService(db)

        # Get current price data
        price_data = market_service.get_latest_price(symbol, exchange.lower())
        if not price_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote not found for {symbol}"
            )
        
        # Get recent historical data for additional metrics
        hist_data = market_service.get_historical_data(symbol, exchange, "1mo")
        
        additional_metrics = {}
        if hist_data is not None and not hist_data.empty:
            # Calculate additional metrics
            closes = hist_data['Close']
            volumes = hist_data['Volume']
            
            additional_metrics = {
                "avg_volume_30d": float(volumes.mean()),
                "volatility_30d": float(closes.pct_change().std() * (252 ** 0.5)),  # Annualized
                "price_range_30d": {
                    "high": float(closes.max()),
                    "low": float(closes.min())
                },
                "sma_20": float(closes.tail(20).mean()) if len(closes) >= 20 else None,
                "sma_50": float(closes.tail(50).mean()) if len(closes) >= 50 else None
            }
        
        # Combine all data
        detailed_quote = {
            **price_data,
            **additional_metrics
        }
        
        return {
            "status": "success",
            "data": detailed_quote,
            "message": f"Detailed quote retrieved for {symbol}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detailed quote: {str(e)}"
        )


@router.delete("/cache", response_model=Dict[str, Any])
async def clear_market_cache(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Clear market data cache (admin function)"""
    try:
        # Only allow admin users to clear cache
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can clear market cache"
            )
        
        market_service = MarketService()
        market_service.clear_cache()
        
        return {
            "status": "success",
            "message": "Market data cache cleared successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )
