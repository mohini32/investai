"""
Portfolio management endpoints - Enhanced with comprehensive portfolio features
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.portfolio import AssetType, TransactionType
from app.services.portfolio_service import PortfolioService
from app.services.market_service import MarketService

router = APIRouter()


# Enhanced Pydantic models
class PortfolioCreate(BaseModel):
    name: str = Field(..., description="Portfolio name")
    description: Optional[str] = Field(None, description="Portfolio description")
    is_default: bool = Field(default=False, description="Set as default portfolio")


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Portfolio name")
    description: Optional[str] = Field(None, description="Portfolio description")
    is_default: Optional[bool] = Field(None, description="Set as default portfolio")


class HoldingCreate(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company/Asset name")
    asset_type: AssetType = Field(..., description="Type of asset")
    exchange: str = Field(default="NSE", description="Exchange")


class TransactionCreate(BaseModel):
    transaction_type: TransactionType = Field(..., description="Transaction type")
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company/Asset name")
    asset_type: AssetType = Field(default=AssetType.STOCK, description="Asset type")
    quantity: float = Field(..., gt=0, description="Quantity")
    price: float = Field(..., gt=0, description="Price per unit")
    total_amount: float = Field(..., gt=0, description="Total transaction amount")
    brokerage: float = Field(default=0.0, ge=0, description="Brokerage charges")
    taxes: float = Field(default=0.0, ge=0, description="Tax charges")
    other_charges: float = Field(default=0.0, ge=0, description="Other charges")
    net_amount: float = Field(..., description="Net amount")
    exchange: str = Field(default="NSE", description="Exchange")
    order_id: Optional[str] = Field(None, description="Broker order ID")
    trade_id: Optional[str] = Field(None, description="Trade ID")
    notes: Optional[str] = Field(None, description="Transaction notes")
    transaction_date: Optional[datetime] = Field(None, description="Transaction date")


class WatchlistCreate(BaseModel):
    name: str = Field(..., description="Watchlist name")
    description: Optional[str] = Field(None, description="Watchlist description")


class WatchlistItemCreate(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company/Asset name")
    asset_type: AssetType = Field(..., description="Asset type")
    exchange: str = Field(default="NSE", description="Exchange")
    target_price: Optional[float] = Field(None, description="Target price")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    notes: Optional[str] = Field(None, description="Notes")


# Portfolio CRUD endpoints
@router.post("/", response_model=Dict[str, Any])
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new portfolio"""
    try:
        portfolio_service = PortfolioService(db)
        portfolio = portfolio_service.create_portfolio(
            user_id=current_user.id,
            name=portfolio_data.name,
            description=portfolio_data.description,
            is_default=portfolio_data.is_default
        )
        
        return {
            "status": "success",
            "data": {
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "is_default": portfolio.is_default,
                "created_at": portfolio.created_at.isoformat()
            },
            "message": f"Portfolio '{portfolio.name}' created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create portfolio: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_user_portfolios(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all portfolios for the current user"""
    try:
        portfolio_service = PortfolioService(db)
        portfolios = portfolio_service.get_user_portfolios(current_user.id)
        
        portfolio_data = []
        for portfolio in portfolios:
            portfolio_data.append({
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "is_default": portfolio.is_default,
                "total_invested": portfolio.total_invested or 0,
                "current_value": portfolio.current_value or 0,
                "total_returns": portfolio.total_returns or 0,
                "returns_percentage": portfolio.returns_percentage or 0,
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat() if portfolio.updated_at else None
            })
        
        return {
            "status": "success",
            "data": {
                "portfolios": portfolio_data,
                "count": len(portfolio_data)
            },
            "message": f"Retrieved {len(portfolio_data)} portfolios"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve portfolios: {str(e)}"
        )


@router.get("/overview", response_model=Dict[str, Any])
async def get_portfolio_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive overview of all user portfolios"""
    try:
        portfolio_service = PortfolioService(db)
        overview = portfolio_service.get_user_portfolio_overview(current_user.id)
        
        return {
            "status": "success",
            "data": overview,
            "message": "Portfolio overview retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio overview: {str(e)}"
        )


@router.get("/{portfolio_id}", response_model=Dict[str, Any])
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific portfolio details"""
    try:
        portfolio_service = PortfolioService(db)
        portfolio = portfolio_service.get_portfolio(portfolio_id, current_user.id)
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "is_default": portfolio.is_default,
                "total_invested": portfolio.total_invested or 0,
                "current_value": portfolio.current_value or 0,
                "total_returns": portfolio.total_returns or 0,
                "returns_percentage": portfolio.returns_percentage or 0,
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat() if portfolio.updated_at else None
            },
            "message": "Portfolio retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve portfolio: {str(e)}"
        )


@router.put("/{portfolio_id}", response_model=Dict[str, Any])
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update portfolio details"""
    try:
        portfolio_service = PortfolioService(db)
        
        # Prepare update data
        update_data = {}
        if portfolio_data.name is not None:
            update_data["name"] = portfolio_data.name
        if portfolio_data.description is not None:
            update_data["description"] = portfolio_data.description
        if portfolio_data.is_default is not None:
            update_data["is_default"] = portfolio_data.is_default
        
        portfolio = portfolio_service.update_portfolio(
            portfolio_id, current_user.id, **update_data
        )
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "is_default": portfolio.is_default,
                "updated_at": portfolio.updated_at.isoformat() if portfolio.updated_at else None
            },
            "message": "Portfolio updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update portfolio: {str(e)}"
        )


@router.delete("/{portfolio_id}", response_model=Dict[str, Any])
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a portfolio"""
    try:
        portfolio_service = PortfolioService(db)
        success = portfolio_service.delete_portfolio(portfolio_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        return {
            "status": "success",
            "message": "Portfolio deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete portfolio: {str(e)}"
        )


@router.get("/{portfolio_id}/summary", response_model=Dict[str, Any])
async def get_portfolio_summary(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive portfolio summary"""
    try:
        portfolio_service = PortfolioService(db)
        summary = portfolio_service.get_portfolio_summary(portfolio_id, current_user.id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        return {
            "status": "success",
            "data": summary,
            "message": "Portfolio summary retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio summary: {str(e)}"
        )


# Holdings endpoints
@router.get("/{portfolio_id}/holdings", response_model=Dict[str, Any])
async def get_portfolio_holdings(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all holdings in a portfolio"""
    try:
        portfolio_service = PortfolioService(db)
        holdings = portfolio_service.get_portfolio_holdings(portfolio_id, current_user.id)

        holdings_data = []
        for holding in holdings:
            holdings_data.append({
                "id": holding.id,
                "symbol": holding.symbol,
                "name": holding.name,
                "asset_type": holding.asset_type.value,
                "exchange": holding.exchange,
                "quantity": holding.quantity,
                "average_price": holding.average_price,
                "current_price": holding.current_price,
                "invested_amount": holding.invested_amount,
                "current_value": holding.current_value,
                "unrealized_pnl": holding.unrealized_pnl,
                "unrealized_pnl_percentage": holding.unrealized_pnl_percentage,
                "day_change": holding.day_change,
                "day_change_percentage": holding.day_change_percentage,
                "last_price_update": holding.last_price_update.isoformat() if holding.last_price_update else None
            })

        return {
            "status": "success",
            "data": {
                "holdings": holdings_data,
                "count": len(holdings_data)
            },
            "message": f"Retrieved {len(holdings_data)} holdings"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio holdings: {str(e)}"
        )


@router.post("/{portfolio_id}/holdings", response_model=Dict[str, Any])
async def add_holding(
    portfolio_id: int,
    holding_data: HoldingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Add a new holding to portfolio"""
    try:
        portfolio_service = PortfolioService(db)
        holding = portfolio_service.add_holding(
            portfolio_id=portfolio_id,
            user_id=current_user.id,
            symbol=holding_data.symbol,
            name=holding_data.name,
            asset_type=holding_data.asset_type,
            exchange=holding_data.exchange
        )

        return {
            "status": "success",
            "data": {
                "id": holding.id,
                "symbol": holding.symbol,
                "name": holding.name,
                "asset_type": holding.asset_type.value,
                "exchange": holding.exchange,
                "current_price": holding.current_price
            },
            "message": f"Added {holding.symbol} to portfolio"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add holding: {str(e)}"
        )


@router.put("/{portfolio_id}/holdings/update-prices", response_model=Dict[str, Any])
async def update_holding_prices(
    portfolio_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update current prices for all holdings in portfolio"""
    try:
        portfolio_service = PortfolioService(db)
        result = portfolio_service.update_holding_prices(portfolio_id, current_user.id)

        return {
            "status": "success",
            "data": result,
            "message": f"Updated prices for {result['updated_count']} holdings"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update holding prices: {str(e)}"
        )


# Transaction endpoints
@router.post("/{portfolio_id}/transactions", response_model=Dict[str, Any])
async def add_transaction(
    portfolio_id: int,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Add a new transaction to portfolio"""
    try:
        portfolio_service = PortfolioService(db)

        # Convert Pydantic model to dict
        transaction_dict = transaction_data.dict()
        transaction_dict["asset_type"] = transaction_data.asset_type.value
        transaction_dict["transaction_type"] = transaction_data.transaction_type.value

        transaction = portfolio_service.add_transaction(
            user_id=current_user.id,
            portfolio_id=portfolio_id,
            transaction_data=transaction_dict
        )

        return {
            "status": "success",
            "data": {
                "id": transaction.id,
                "transaction_type": transaction.transaction_type.value,
                "symbol": transaction.symbol,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "total_amount": transaction.total_amount,
                "net_amount": transaction.net_amount,
                "transaction_date": transaction.transaction_date.isoformat()
            },
            "message": f"Added {transaction.transaction_type.value} transaction for {transaction.symbol}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add transaction: {str(e)}"
        )


@router.get("/{portfolio_id}/transactions", response_model=Dict[str, Any])
async def get_portfolio_transactions(
    portfolio_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get transactions for a portfolio"""
    try:
        portfolio_service = PortfolioService(db)
        transactions = portfolio_service.get_portfolio_transactions(
            portfolio_id, current_user.id, limit, offset
        )

        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                "id": transaction.id,
                "transaction_type": transaction.transaction_type.value,
                "symbol": transaction.symbol,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "total_amount": transaction.total_amount,
                "brokerage": transaction.brokerage,
                "taxes": transaction.taxes,
                "other_charges": transaction.other_charges,
                "net_amount": transaction.net_amount,
                "exchange": transaction.exchange,
                "order_id": transaction.order_id,
                "trade_id": transaction.trade_id,
                "notes": transaction.notes,
                "transaction_date": transaction.transaction_date.isoformat()
            })

        return {
            "status": "success",
            "data": {
                "transactions": transaction_data,
                "count": len(transaction_data),
                "limit": limit,
                "offset": offset
            },
            "message": f"Retrieved {len(transaction_data)} transactions"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio transactions: {str(e)}"
        )


# AI Analysis endpoints
@router.post("/{portfolio_id}/analyze", response_model=Dict[str, Any])
async def analyze_portfolio_with_ai(
    portfolio_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Analyze portfolio using AI agents"""
    try:
        portfolio_service = PortfolioService(db)
        analysis = portfolio_service.analyze_portfolio_with_ai(portfolio_id, current_user.id)

        return {
            "status": "success",
            "data": analysis,
            "message": "Portfolio AI analysis completed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze portfolio: {str(e)}"
        )


@router.get("/{portfolio_id}/rebalancing", response_model=Dict[str, Any])
async def get_rebalancing_recommendations(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered rebalancing recommendations"""
    try:
        portfolio_service = PortfolioService(db)
        recommendations = portfolio_service.get_rebalancing_recommendations(
            portfolio_id, current_user.id
        )

        return {
            "status": "success",
            "data": recommendations,
            "message": "Rebalancing recommendations generated"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rebalancing recommendations: {str(e)}"
        )


# Performance tracking endpoints
@router.get("/{portfolio_id}/performance", response_model=Dict[str, Any])
async def get_portfolio_performance(
    portfolio_id: int,
    period_days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get portfolio performance over time"""
    try:
        portfolio_service = PortfolioService(db)
        performance = portfolio_service.get_portfolio_performance(
            portfolio_id, current_user.id, period_days
        )

        return {
            "status": "success",
            "data": performance,
            "message": f"Portfolio performance for {period_days} days retrieved"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio performance: {str(e)}"
        )


@router.post("/{portfolio_id}/snapshot", response_model=Dict[str, Any])
async def create_portfolio_snapshot(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a portfolio snapshot for historical tracking"""
    try:
        portfolio_service = PortfolioService(db)
        snapshot = portfolio_service.create_portfolio_snapshot(portfolio_id, current_user.id)

        return {
            "status": "success",
            "data": {
                "id": snapshot.id,
                "snapshot_date": snapshot.snapshot_date.isoformat(),
                "total_invested": snapshot.total_invested,
                "current_value": snapshot.current_value,
                "total_returns": snapshot.total_returns,
                "returns_percentage": snapshot.returns_percentage
            },
            "message": "Portfolio snapshot created successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create portfolio snapshot: {str(e)}"
        )


# Watchlist endpoints
@router.post("/watchlists", response_model=Dict[str, Any])
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new watchlist"""
    try:
        portfolio_service = PortfolioService(db)
        watchlist = portfolio_service.create_watchlist(
            user_id=current_user.id,
            name=watchlist_data.name,
            description=watchlist_data.description
        )

        return {
            "status": "success",
            "data": {
                "id": watchlist.id,
                "name": watchlist.name,
                "description": watchlist.description,
                "created_at": watchlist.created_at.isoformat()
            },
            "message": f"Watchlist '{watchlist.name}' created successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create watchlist: {str(e)}"
        )


@router.get("/watchlists", response_model=Dict[str, Any])
async def get_user_watchlists(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all watchlists for the current user"""
    try:
        portfolio_service = PortfolioService(db)
        watchlists = portfolio_service.get_user_watchlists(current_user.id)

        watchlist_data = []
        for watchlist in watchlists:
            watchlist_data.append({
                "id": watchlist.id,
                "name": watchlist.name,
                "description": watchlist.description,
                "items_count": len(watchlist.watchlist_items),
                "created_at": watchlist.created_at.isoformat()
            })

        return {
            "status": "success",
            "data": {
                "watchlists": watchlist_data,
                "count": len(watchlist_data)
            },
            "message": f"Retrieved {len(watchlist_data)} watchlists"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get watchlists: {str(e)}"
        )


@router.post("/watchlists/{watchlist_id}/items", response_model=Dict[str, Any])
async def add_to_watchlist(
    watchlist_id: int,
    item_data: WatchlistItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Add item to watchlist"""
    try:
        portfolio_service = PortfolioService(db)
        item = portfolio_service.add_to_watchlist(
            watchlist_id=watchlist_id,
            user_id=current_user.id,
            symbol=item_data.symbol,
            name=item_data.name,
            asset_type=item_data.asset_type,
            exchange=item_data.exchange,
            target_price=item_data.target_price,
            stop_loss=item_data.stop_loss
        )

        return {
            "status": "success",
            "data": {
                "id": item.id,
                "symbol": item.symbol,
                "name": item.name,
                "asset_type": item.asset_type.value,
                "current_price": item.current_price,
                "target_price": item.target_price,
                "stop_loss": item.stop_loss
            },
            "message": f"Added {item.symbol} to watchlist"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add to watchlist: {str(e)}"
        )


@router.put("/watchlists/{watchlist_id}/update-prices", response_model=Dict[str, Any])
async def update_watchlist_prices(
    watchlist_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update prices for all items in watchlist"""
    try:
        portfolio_service = PortfolioService(db)
        result = portfolio_service.update_watchlist_prices(watchlist_id, current_user.id)

        return {
            "status": "success",
            "data": result,
            "message": f"Updated prices for {result['updated_count']} watchlist items"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update watchlist prices: {str(e)}"
        )


# Alert endpoints
@router.get("/alerts", response_model=Dict[str, Any])
async def get_user_alerts(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get alerts for the current user"""
    try:
        portfolio_service = PortfolioService(db)
        alerts = portfolio_service.get_user_alerts(
            current_user.id, unread_only, limit
        )

        alert_data = []
        for alert in alerts:
            alert_data.append({
                "id": alert.id,
                "alert_type": alert.alert_type,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity,
                "is_read": alert.is_read,
                "is_dismissed": alert.is_dismissed,
                "created_at": alert.created_at.isoformat(),
                "read_at": alert.read_at.isoformat() if alert.read_at else None
            })

        return {
            "status": "success",
            "data": {
                "alerts": alert_data,
                "count": len(alert_data),
                "unread_count": len([a for a in alert_data if not a["is_read"]])
            },
            "message": f"Retrieved {len(alert_data)} alerts"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}/read", response_model=Dict[str, Any])
async def mark_alert_as_read(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark alert as read"""
    try:
        portfolio_service = PortfolioService(db)
        success = portfolio_service.mark_alert_as_read(alert_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )

        return {
            "status": "success",
            "message": "Alert marked as read"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to mark alert as read: {str(e)}"
        )
