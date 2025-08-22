"""
Portfolio Service - Core portfolio management functionality
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging

from app.models.portfolio import (
    Portfolio, Holding, Transaction, PortfolioSnapshot, 
    Watchlist, WatchlistItem, PortfolioAlert, AssetType, TransactionType
)
from app.models.user import User
from app.services.market_data_service import MarketDataService
from app.ai.crew import InvestAICrew

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_service = MarketDataService(db)
        self.ai_crew = InvestAICrew()
    
    # Portfolio CRUD Operations
    def create_portfolio(self, user_id: int, name: str, description: str = None, 
                        is_default: bool = False) -> Portfolio:
        """Create a new portfolio"""
        try:
            # If this is set as default, unset other default portfolios
            if is_default:
                self.db.query(Portfolio).filter(
                    and_(Portfolio.user_id == user_id, Portfolio.is_default == True)
                ).update({"is_default": False})
            
            portfolio = Portfolio(
                user_id=user_id,
                name=name,
                description=description,
                is_default=is_default
            )
            
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
            
            logger.info(f"Created portfolio {portfolio.id} for user {user_id}")
            return portfolio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create portfolio: {str(e)}")
            raise
    
    def get_user_portfolios(self, user_id: int) -> List[Portfolio]:
        """Get all portfolios for a user"""
        return self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id
        ).order_by(desc(Portfolio.is_default), Portfolio.created_at).all()
    
    def get_portfolio(self, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio"""
        return self.db.query(Portfolio).filter(
            and_(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
        ).first()
    
    def update_portfolio(self, portfolio_id: int, user_id: int, **updates) -> Optional[Portfolio]:
        """Update portfolio details"""
        try:
            portfolio = self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                return None
            
            # Handle default portfolio logic
            if updates.get("is_default"):
                self.db.query(Portfolio).filter(
                    and_(Portfolio.user_id == user_id, Portfolio.id != portfolio_id)
                ).update({"is_default": False})
            
            for key, value in updates.items():
                if hasattr(portfolio, key):
                    setattr(portfolio, key, value)
            
            self.db.commit()
            self.db.refresh(portfolio)
            
            logger.info(f"Updated portfolio {portfolio_id}")
            return portfolio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update portfolio {portfolio_id}: {str(e)}")
            raise
    
    def delete_portfolio(self, portfolio_id: int, user_id: int) -> bool:
        """Delete a portfolio"""
        try:
            portfolio = self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                return False
            
            self.db.delete(portfolio)
            self.db.commit()
            
            logger.info(f"Deleted portfolio {portfolio_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete portfolio {portfolio_id}: {str(e)}")
            raise
    
    # Holdings Management
    def add_holding(self, portfolio_id: int, user_id: int, symbol: str, name: str,
                   asset_type: AssetType, exchange: str = "NSE") -> Holding:
        """Add a new holding to portfolio"""
        try:
            # Check if portfolio belongs to user
            portfolio = self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            # Check if holding already exists
            existing_holding = self.db.query(Holding).filter(
                and_(
                    Holding.portfolio_id == portfolio_id,
                    Holding.symbol == symbol,
                    Holding.exchange == exchange
                )
            ).first()
            
            if existing_holding:
                return existing_holding
            
            # Get current market price
            market_data = self.market_service.get_current_price(symbol, exchange)
            current_price = market_data.get("current_price", 0.0) if market_data else 0.0
            
            holding = Holding(
                portfolio_id=portfolio_id,
                symbol=symbol,
                name=name,
                asset_type=asset_type,
                exchange=exchange,
                current_price=current_price,
                last_price_update=datetime.now()
            )
            
            self.db.add(holding)
            self.db.commit()
            self.db.refresh(holding)
            
            logger.info(f"Added holding {symbol} to portfolio {portfolio_id}")
            return holding
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add holding {symbol}: {str(e)}")
            raise
    
    def get_portfolio_holdings(self, portfolio_id: int, user_id: int) -> List[Holding]:
        """Get all holdings in a portfolio"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return []
        
        return self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id
        ).order_by(desc(Holding.current_value)).all()
    
    def update_holding_prices(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Update current prices for all holdings in portfolio"""
        try:
            holdings = self.get_portfolio_holdings(portfolio_id, user_id)
            updated_count = 0
            errors = []
            
            for holding in holdings:
                try:
                    market_data = self.market_service.get_current_price(
                        holding.symbol, holding.exchange
                    )
                    
                    if market_data and "current_price" in market_data:
                        old_price = holding.current_price
                        new_price = market_data["current_price"]
                        
                        holding.current_price = new_price
                        holding.last_price_update = datetime.now()
                        
                        # Calculate day change
                        if old_price and old_price > 0:
                            holding.day_change = new_price - old_price
                            holding.day_change_percentage = (holding.day_change / old_price) * 100
                        
                        # Update calculated metrics
                        holding.update_metrics()
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Failed to update {holding.symbol}: {str(e)}")
                    logger.error(f"Failed to update price for {holding.symbol}: {str(e)}")
            
            # Update portfolio metrics
            self._update_portfolio_metrics(portfolio_id)
            
            self.db.commit()
            
            return {
                "updated_count": updated_count,
                "total_holdings": len(holdings),
                "errors": errors,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update holding prices: {str(e)}")
            raise
    
    # Transaction Management
    def add_transaction(self, user_id: int, portfolio_id: int, transaction_data: Dict[str, Any]) -> Transaction:
        """Add a new transaction"""
        try:
            # Validate portfolio ownership
            portfolio = self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                portfolio_id=portfolio_id,
                transaction_type=TransactionType(transaction_data["transaction_type"]),
                symbol=transaction_data["symbol"],
                quantity=transaction_data["quantity"],
                price=transaction_data["price"],
                total_amount=transaction_data["total_amount"],
                brokerage=transaction_data.get("brokerage", 0.0),
                taxes=transaction_data.get("taxes", 0.0),
                other_charges=transaction_data.get("other_charges", 0.0),
                net_amount=transaction_data["net_amount"],
                exchange=transaction_data.get("exchange", "NSE"),
                order_id=transaction_data.get("order_id"),
                trade_id=transaction_data.get("trade_id"),
                notes=transaction_data.get("notes"),
                transaction_date=transaction_data.get("transaction_date", datetime.now())
            )
            
            self.db.add(transaction)
            
            # Update or create holding
            self._process_transaction_for_holding(transaction, transaction_data)
            
            # Update portfolio metrics
            self._update_portfolio_metrics(portfolio_id)
            
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Added transaction {transaction.id} for {transaction.symbol}")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add transaction: {str(e)}")
            raise
    
    def get_portfolio_transactions(self, portfolio_id: int, user_id: int, 
                                 limit: int = 50, offset: int = 0) -> List[Transaction]:
        """Get transactions for a portfolio"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return []
        
        return self.db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id
        ).order_by(desc(Transaction.transaction_date)).offset(offset).limit(limit).all()
    
    def get_user_transactions(self, user_id: int, limit: int = 100, 
                            offset: int = 0) -> List[Transaction]:
        """Get all transactions for a user"""
        return self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(desc(Transaction.transaction_date)).offset(offset).limit(limit).all()
    
    # Portfolio Analytics
    def get_portfolio_summary(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        try:
            portfolio = self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                return {}
            
            holdings = self.get_portfolio_holdings(portfolio_id, user_id)
            
            # Basic metrics
            total_invested = sum(h.invested_amount or 0 for h in holdings)
            current_value = sum(h.current_value or 0 for h in holdings)
            total_returns = current_value - total_invested
            returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0
            
            # Asset allocation
            asset_allocation = {}
            if current_value > 0:
                for holding in holdings:
                    asset_type = holding.asset_type.value
                    value = holding.current_value or 0
                    percentage = (value / current_value) * 100
                    
                    if asset_type in asset_allocation:
                        asset_allocation[asset_type] += percentage
                    else:
                        asset_allocation[asset_type] = percentage
            
            # Top holdings
            top_holdings = sorted(holdings, key=lambda h: h.current_value or 0, reverse=True)[:5]
            
            # Recent transactions
            recent_transactions = self.get_portfolio_transactions(portfolio_id, user_id, limit=10)
            
            return {
                "portfolio_id": portfolio_id,
                "name": portfolio.name,
                "total_invested": total_invested,
                "current_value": current_value,
                "total_returns": total_returns,
                "returns_percentage": returns_percentage,
                "holdings_count": len(holdings),
                "asset_allocation": asset_allocation,
                "top_holdings": [
                    {
                        "symbol": h.symbol,
                        "name": h.name,
                        "current_value": h.current_value,
                        "returns_percentage": h.unrealized_pnl_percentage
                    } for h in top_holdings
                ],
                "recent_transactions": [
                    {
                        "id": t.id,
                        "type": t.transaction_type.value,
                        "symbol": t.symbol,
                        "quantity": t.quantity,
                        "price": t.price,
                        "date": t.transaction_date.isoformat()
                    } for t in recent_transactions
                ],
                "last_updated": portfolio.updated_at.isoformat() if portfolio.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {str(e)}")
            raise
    
    def get_portfolio_performance(self, portfolio_id: int, user_id: int, 
                                period_days: int = 30) -> Dict[str, Any]:
        """Get portfolio performance over time"""
        try:
            # Get portfolio snapshots for the period
            start_date = datetime.now() - timedelta(days=period_days)
            
            snapshots = self.db.query(PortfolioSnapshot).filter(
                and_(
                    PortfolioSnapshot.portfolio_id == portfolio_id,
                    PortfolioSnapshot.snapshot_date >= start_date
                )
            ).order_by(PortfolioSnapshot.snapshot_date).all()
            
            if not snapshots:
                # Create current snapshot if none exist
                self.create_portfolio_snapshot(portfolio_id, user_id)
                return {"message": "No historical data available"}
            
            # Calculate performance metrics
            first_snapshot = snapshots[0]
            last_snapshot = snapshots[-1]
            
            period_return = ((last_snapshot.current_value - first_snapshot.current_value) / 
                           first_snapshot.current_value * 100) if first_snapshot.current_value > 0 else 0
            
            # Daily returns for volatility calculation
            daily_returns = []
            for i in range(1, len(snapshots)):
                prev_value = snapshots[i-1].current_value
                curr_value = snapshots[i].current_value
                if prev_value > 0:
                    daily_return = (curr_value - prev_value) / prev_value
                    daily_returns.append(daily_return)
            
            # Calculate volatility (standard deviation of returns)
            volatility = 0
            if len(daily_returns) > 1:
                mean_return = sum(daily_returns) / len(daily_returns)
                variance = sum((r - mean_return) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
                volatility = (variance ** 0.5) * (252 ** 0.5)  # Annualized
            
            return {
                "period_days": period_days,
                "period_return_percentage": period_return,
                "volatility": volatility,
                "snapshots_count": len(snapshots),
                "performance_data": [
                    {
                        "date": s.snapshot_date.isoformat(),
                        "value": s.current_value,
                        "returns": s.returns_percentage
                    } for s in snapshots
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio performance: {str(e)}")
            raise

    # Portfolio Optimization and AI Integration
    def analyze_portfolio_with_ai(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze portfolio using AI agents"""
        try:
            portfolio = self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")

            # Get user profile
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            user_profile = {
                "id": user.id,
                "age": user.age,
                "annual_income": user.annual_income,
                "monthly_expenses": user.monthly_expenses,
                "risk_profile": user.risk_profile,
                "investment_experience": user.investment_experience,
                "investment_horizon_years": user.investment_horizon_years
            }

            # Prepare portfolio data
            holdings = self.get_portfolio_holdings(portfolio_id, user_id)
            portfolio_data = {
                "id": portfolio_id,
                "name": portfolio.name,
                "holdings": [
                    {
                        "symbol": h.symbol,
                        "name": h.name,
                        "asset_type": h.asset_type.value,
                        "quantity": h.quantity,
                        "average_price": h.average_price,
                        "current_price": h.current_price,
                        "invested_amount": h.invested_amount,
                        "current_value": h.current_value,
                        "unrealized_pnl": h.unrealized_pnl,
                        "unrealized_pnl_percentage": h.unrealized_pnl_percentage,
                        "exchange": h.exchange
                    } for h in holdings
                ]
            }

            # Use AI crew for analysis
            analysis_request = {
                "request_id": f"portfolio_analysis_{portfolio_id}_{user_id}",
                "portfolio_data": portfolio_data,
                "user_profile": user_profile
            }

            ai_analysis = self.ai_crew.portfolio_optimization_analysis(analysis_request)

            return ai_analysis

        except Exception as e:
            logger.error(f"Failed to analyze portfolio with AI: {str(e)}")
            raise

    def get_rebalancing_recommendations(self, portfolio_id: int, user_id: int) -> Dict[str, Any]:
        """Get AI-powered rebalancing recommendations"""
        try:
            ai_analysis = self.analyze_portfolio_with_ai(portfolio_id, user_id)

            if "error" in ai_analysis:
                return ai_analysis

            # Extract rebalancing recommendations
            optimization = ai_analysis.get("optimization_recommendations", {})
            current_analysis = ai_analysis.get("current_portfolio_analysis", {})

            return {
                "rebalancing_needed": optimization.get("rebalancing_required", False),
                "recommendations": optimization.get("recommended_changes", []),
                "expected_improvement": optimization.get("expected_improvement", {}),
                "current_allocation": current_analysis.get("advisor_analysis", {}).get("asset_allocation", {}),
                "risk_assessment": current_analysis.get("risk_analysis", {}),
                "implementation_plan": ai_analysis.get("implementation_plan", {})
            }

        except Exception as e:
            logger.error(f"Failed to get rebalancing recommendations: {str(e)}")
            raise

    # Portfolio Snapshots
    def create_portfolio_snapshot(self, portfolio_id: int, user_id: int) -> PortfolioSnapshot:
        """Create a portfolio snapshot for historical tracking"""
        try:
            portfolio = self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")

            holdings = self.get_portfolio_holdings(portfolio_id, user_id)

            # Calculate current metrics
            total_invested = sum(h.invested_amount or 0 for h in holdings)
            current_value = sum(h.current_value or 0 for h in holdings)
            total_returns = current_value - total_invested
            returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0

            # Asset allocation
            asset_allocation = {}
            if current_value > 0:
                for holding in holdings:
                    asset_type = holding.asset_type.value
                    value = holding.current_value or 0
                    percentage = (value / current_value) * 100

                    if asset_type in asset_allocation:
                        asset_allocation[asset_type] += percentage
                    else:
                        asset_allocation[asset_type] = percentage

            snapshot = PortfolioSnapshot(
                portfolio_id=portfolio_id,
                snapshot_date=datetime.now(),
                total_invested=total_invested,
                current_value=current_value,
                total_returns=total_returns,
                returns_percentage=returns_percentage,
                portfolio_beta=portfolio.portfolio_beta,
                sharpe_ratio=portfolio.sharpe_ratio,
                volatility=portfolio.volatility,
                asset_allocation=json.dumps(asset_allocation),
                holdings_count=len(holdings)
            )

            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)

            logger.info(f"Created portfolio snapshot for portfolio {portfolio_id}")
            return snapshot

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create portfolio snapshot: {str(e)}")
            raise

    def get_portfolio_snapshots(self, portfolio_id: int, user_id: int,
                              days: int = 30) -> List[PortfolioSnapshot]:
        """Get portfolio snapshots for a period"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return []

        start_date = datetime.now() - timedelta(days=days)

        return self.db.query(PortfolioSnapshot).filter(
            and_(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.snapshot_date >= start_date
            )
        ).order_by(PortfolioSnapshot.snapshot_date).all()

    # Watchlist Management
    def create_watchlist(self, user_id: int, name: str, description: str = None) -> Watchlist:
        """Create a new watchlist"""
        try:
            watchlist = Watchlist(
                user_id=user_id,
                name=name,
                description=description
            )

            self.db.add(watchlist)
            self.db.commit()
            self.db.refresh(watchlist)

            logger.info(f"Created watchlist {watchlist.id} for user {user_id}")
            return watchlist

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create watchlist: {str(e)}")
            raise

    def add_to_watchlist(self, watchlist_id: int, user_id: int, symbol: str,
                        name: str, asset_type: AssetType, exchange: str = "NSE",
                        target_price: float = None, stop_loss: float = None) -> WatchlistItem:
        """Add item to watchlist"""
        try:
            # Verify watchlist ownership
            watchlist = self.db.query(Watchlist).filter(
                and_(Watchlist.id == watchlist_id, Watchlist.user_id == user_id)
            ).first()

            if not watchlist:
                raise ValueError("Watchlist not found")

            # Check if item already exists
            existing_item = self.db.query(WatchlistItem).filter(
                and_(
                    WatchlistItem.watchlist_id == watchlist_id,
                    WatchlistItem.symbol == symbol,
                    WatchlistItem.exchange == exchange
                )
            ).first()

            if existing_item:
                return existing_item

            # Get current price
            market_data = self.market_service.get_current_price(symbol, exchange)
            current_price = market_data.get("current_price", 0.0) if market_data else 0.0

            watchlist_item = WatchlistItem(
                watchlist_id=watchlist_id,
                symbol=symbol,
                name=name,
                asset_type=asset_type,
                exchange=exchange,
                added_price=current_price,
                current_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                last_price_update=datetime.now()
            )

            self.db.add(watchlist_item)
            self.db.commit()
            self.db.refresh(watchlist_item)

            logger.info(f"Added {symbol} to watchlist {watchlist_id}")
            return watchlist_item

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add to watchlist: {str(e)}")
            raise

    def get_user_watchlists(self, user_id: int) -> List[Watchlist]:
        """Get all watchlists for a user"""
        return self.db.query(Watchlist).filter(
            Watchlist.user_id == user_id
        ).order_by(Watchlist.created_at).all()

    def update_watchlist_prices(self, watchlist_id: int, user_id: int) -> Dict[str, Any]:
        """Update prices for all items in watchlist"""
        try:
            # Verify watchlist ownership
            watchlist = self.db.query(Watchlist).filter(
                and_(Watchlist.id == watchlist_id, Watchlist.user_id == user_id)
            ).first()

            if not watchlist:
                raise ValueError("Watchlist not found")

            items = watchlist.watchlist_items
            updated_count = 0
            alerts_generated = []

            for item in items:
                try:
                    market_data = self.market_service.get_current_price(
                        item.symbol, item.exchange
                    )

                    if market_data and "current_price" in market_data:
                        old_price = item.current_price
                        new_price = market_data["current_price"]

                        item.current_price = new_price
                        item.last_price_update = datetime.now()
                        updated_count += 1

                        # Check for price alerts
                        if item.price_alert_enabled and item.price_alert_threshold:
                            if (old_price < item.price_alert_threshold <= new_price or
                                old_price > item.price_alert_threshold >= new_price):

                                alert = self._create_price_alert(
                                    user_id, item, old_price, new_price
                                )
                                alerts_generated.append(alert)

                        # Check target price and stop loss
                        if item.target_price and new_price >= item.target_price:
                            alert = self._create_target_reached_alert(user_id, item, new_price)
                            alerts_generated.append(alert)

                        if item.stop_loss and new_price <= item.stop_loss:
                            alert = self._create_stop_loss_alert(user_id, item, new_price)
                            alerts_generated.append(alert)

                except Exception as e:
                    logger.error(f"Failed to update price for {item.symbol}: {str(e)}")

            self.db.commit()

            return {
                "updated_count": updated_count,
                "total_items": len(items),
                "alerts_generated": len(alerts_generated),
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update watchlist prices: {str(e)}")
            raise

    # Helper Methods
    def _process_transaction_for_holding(self, transaction: Transaction, transaction_data: Dict[str, Any]):
        """Process transaction and update holding"""
        try:
            # Find or create holding
            holding = self.db.query(Holding).filter(
                and_(
                    Holding.portfolio_id == transaction.portfolio_id,
                    Holding.symbol == transaction.symbol,
                    Holding.exchange == transaction.exchange
                )
            ).first()

            if not holding:
                # Create new holding
                holding = Holding(
                    portfolio_id=transaction.portfolio_id,
                    symbol=transaction.symbol,
                    name=transaction_data.get("name", transaction.symbol),
                    asset_type=AssetType(transaction_data.get("asset_type", "stock")),
                    exchange=transaction.exchange,
                    quantity=0,
                    average_price=0,
                    invested_amount=0
                )
                self.db.add(holding)

            # Update holding based on transaction type
            if transaction.transaction_type == TransactionType.BUY:
                # Calculate new average price
                total_invested = holding.invested_amount + transaction.net_amount
                total_quantity = holding.quantity + transaction.quantity

                holding.average_price = total_invested / total_quantity if total_quantity > 0 else 0
                holding.quantity = total_quantity
                holding.invested_amount = total_invested

            elif transaction.transaction_type == TransactionType.SELL:
                # Reduce quantity and invested amount proportionally
                if holding.quantity >= transaction.quantity:
                    sell_ratio = transaction.quantity / holding.quantity
                    holding.invested_amount -= holding.invested_amount * sell_ratio
                    holding.quantity -= transaction.quantity

                    if holding.quantity <= 0:
                        holding.quantity = 0
                        holding.invested_amount = 0
                        holding.average_price = 0
                else:
                    logger.warning(f"Sell quantity exceeds holding for {transaction.symbol}")

            # Update current price if available
            if transaction_data.get("current_price"):
                holding.current_price = transaction_data["current_price"]
                holding.last_price_update = datetime.now()

            # Update calculated metrics
            holding.update_metrics()

            # Link transaction to holding
            transaction.holding_id = holding.id

        except Exception as e:
            logger.error(f"Failed to process transaction for holding: {str(e)}")
            raise

    def _update_portfolio_metrics(self, portfolio_id: int):
        """Update portfolio-level metrics"""
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return

            holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

            # Calculate basic metrics
            total_invested = sum(h.invested_amount or 0 for h in holdings)
            current_value = sum(h.current_value or 0 for h in holdings)
            total_returns = current_value - total_invested
            returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0

            # Update portfolio
            portfolio.total_invested = total_invested
            portfolio.current_value = current_value
            portfolio.total_returns = total_returns
            portfolio.returns_percentage = returns_percentage
            portfolio.updated_at = datetime.now()

            # TODO: Calculate advanced metrics (beta, sharpe ratio, volatility)
            # This would require historical price data and market benchmark data

        except Exception as e:
            logger.error(f"Failed to update portfolio metrics: {str(e)}")
            raise

    def _create_price_alert(self, user_id: int, watchlist_item: WatchlistItem,
                          old_price: float, new_price: float) -> PortfolioAlert:
        """Create price alert"""
        try:
            alert = PortfolioAlert(
                user_id=user_id,
                alert_type="price_alert",
                title=f"Price Alert: {watchlist_item.symbol}",
                message=f"{watchlist_item.symbol} price changed from ₹{old_price:.2f} to ₹{new_price:.2f}",
                severity="info",
                alert_data=json.dumps({
                    "symbol": watchlist_item.symbol,
                    "old_price": old_price,
                    "new_price": new_price,
                    "threshold": watchlist_item.price_alert_threshold
                })
            )

            self.db.add(alert)
            return alert

        except Exception as e:
            logger.error(f"Failed to create price alert: {str(e)}")
            raise

    def _create_target_reached_alert(self, user_id: int, watchlist_item: WatchlistItem,
                                   current_price: float) -> PortfolioAlert:
        """Create target price reached alert"""
        try:
            alert = PortfolioAlert(
                user_id=user_id,
                alert_type="target_reached",
                title=f"Target Reached: {watchlist_item.symbol}",
                message=f"{watchlist_item.symbol} has reached your target price of ₹{watchlist_item.target_price:.2f}",
                severity="info",
                alert_data=json.dumps({
                    "symbol": watchlist_item.symbol,
                    "target_price": watchlist_item.target_price,
                    "current_price": current_price
                })
            )

            self.db.add(alert)
            return alert

        except Exception as e:
            logger.error(f"Failed to create target reached alert: {str(e)}")
            raise

    def _create_stop_loss_alert(self, user_id: int, watchlist_item: WatchlistItem,
                              current_price: float) -> PortfolioAlert:
        """Create stop loss alert"""
        try:
            alert = PortfolioAlert(
                user_id=user_id,
                alert_type="stop_loss",
                title=f"Stop Loss Triggered: {watchlist_item.symbol}",
                message=f"{watchlist_item.symbol} has hit your stop loss at ₹{watchlist_item.stop_loss:.2f}",
                severity="warning",
                alert_data=json.dumps({
                    "symbol": watchlist_item.symbol,
                    "stop_loss": watchlist_item.stop_loss,
                    "current_price": current_price
                })
            )

            self.db.add(alert)
            return alert

        except Exception as e:
            logger.error(f"Failed to create stop loss alert: {str(e)}")
            raise

    # Alert Management
    def get_user_alerts(self, user_id: int, unread_only: bool = False,
                       limit: int = 50) -> List[PortfolioAlert]:
        """Get alerts for a user"""
        query = self.db.query(PortfolioAlert).filter(PortfolioAlert.user_id == user_id)

        if unread_only:
            query = query.filter(PortfolioAlert.is_read == False)

        return query.order_by(desc(PortfolioAlert.created_at)).limit(limit).all()

    def mark_alert_as_read(self, alert_id: int, user_id: int) -> bool:
        """Mark alert as read"""
        try:
            alert = self.db.query(PortfolioAlert).filter(
                and_(PortfolioAlert.id == alert_id, PortfolioAlert.user_id == user_id)
            ).first()

            if alert:
                alert.is_read = True
                alert.read_at = datetime.now()
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to mark alert as read: {str(e)}")
            raise

    def dismiss_alert(self, alert_id: int, user_id: int) -> bool:
        """Dismiss an alert"""
        try:
            alert = self.db.query(PortfolioAlert).filter(
                and_(PortfolioAlert.id == alert_id, PortfolioAlert.user_id == user_id)
            ).first()

            if alert:
                alert.is_dismissed = True
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to dismiss alert: {str(e)}")
            raise

    # Bulk Operations
    def bulk_update_portfolio_prices(self, user_id: int) -> Dict[str, Any]:
        """Update prices for all portfolios of a user"""
        try:
            portfolios = self.get_user_portfolios(user_id)
            results = {}

            for portfolio in portfolios:
                try:
                    result = self.update_holding_prices(portfolio.id, user_id)
                    results[portfolio.id] = result
                except Exception as e:
                    results[portfolio.id] = {"error": str(e)}

            return {
                "portfolios_processed": len(portfolios),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to bulk update portfolio prices: {str(e)}")
            raise

    def get_user_portfolio_overview(self, user_id: int) -> Dict[str, Any]:
        """Get overview of all user portfolios"""
        try:
            portfolios = self.get_user_portfolios(user_id)

            total_invested = 0
            total_current_value = 0
            total_holdings = 0

            portfolio_summaries = []

            for portfolio in portfolios:
                summary = self.get_portfolio_summary(portfolio.id, user_id)
                portfolio_summaries.append(summary)

                total_invested += summary.get("total_invested", 0)
                total_current_value += summary.get("current_value", 0)
                total_holdings += summary.get("holdings_count", 0)

            total_returns = total_current_value - total_invested
            total_returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0

            return {
                "user_id": user_id,
                "portfolios_count": len(portfolios),
                "total_invested": total_invested,
                "total_current_value": total_current_value,
                "total_returns": total_returns,
                "total_returns_percentage": total_returns_percentage,
                "total_holdings": total_holdings,
                "portfolios": portfolio_summaries,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get user portfolio overview: {str(e)}")
            raise
