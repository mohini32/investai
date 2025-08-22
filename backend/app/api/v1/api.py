"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, portfolios, market_data, goals, ai_analysis, dashboard, goal_dashboard, risk_management, risk_dashboard, tax_planning, tax_dashboard, performance_analytics, performance_dashboard, social_trading, social_analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(market_data.router, prefix="/market", tags=["market-data"])
api_router.include_router(goals.router, prefix="/goals", tags=["financial-goals"])
api_router.include_router(goal_dashboard.router, prefix="/goals/dashboard", tags=["goal-dashboard"])
api_router.include_router(risk_management.router, prefix="/risk", tags=["risk-management"])
api_router.include_router(risk_dashboard.router, prefix="/risk/dashboard", tags=["risk-dashboard"])
api_router.include_router(tax_planning.router, prefix="/tax", tags=["tax-planning"])
api_router.include_router(tax_dashboard.router, prefix="/tax/dashboard", tags=["tax-dashboard"])
api_router.include_router(performance_analytics.router, prefix="/performance", tags=["performance-analytics"])
api_router.include_router(performance_dashboard.router, prefix="/performance/dashboard", tags=["performance-dashboard"])
api_router.include_router(social_trading.router, prefix="/social", tags=["social-trading"])
api_router.include_router(social_analytics.router, prefix="/social/analytics", tags=["social-analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ai_analysis.router, prefix="/ai", tags=["ai-analysis"])
