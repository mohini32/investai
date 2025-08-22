"""
AI Analysis endpoints - Expose AI agent functionality through REST API
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.ai.crew import InvestAICrew

router = APIRouter()

# Initialize AI crew
ai_crew = InvestAICrew()


# Pydantic models for request/response
class StockAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE)")
    exchange: str = Field(default="NSE", description="Exchange (NSE/BSE)")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")
    investment_amount: Optional[float] = Field(default=100000, description="Investment amount in INR")


class PortfolioOptimizationRequest(BaseModel):
    portfolio_data: Dict[str, Any] = Field(..., description="Current portfolio data")
    goals: List[Dict[str, Any]] = Field(default=[], description="Financial goals")
    optimization_type: str = Field(default="comprehensive", description="Optimization type")


class FinancialPlanningRequest(BaseModel):
    goals: List[Dict[str, Any]] = Field(..., description="Financial goals")
    current_portfolio: Optional[Dict[str, Any]] = Field(default={}, description="Current portfolio")
    transactions: List[Dict[str, Any]] = Field(default=[], description="Transaction history")
    planning_horizon: int = Field(default=10, description="Planning horizon in years")


class RiskProfilingRequest(BaseModel):
    questionnaire_responses: Dict[str, Any] = Field(..., description="Risk questionnaire responses")
    assessment_type: str = Field(default="comprehensive", description="Assessment type")


class TaxPlanningRequest(BaseModel):
    transactions: List[Dict[str, Any]] = Field(..., description="Transaction history")
    financial_year: str = Field(default="2024-25", description="Financial year")
    planning_type: str = Field(default="comprehensive", description="Planning type")


class MarketOutlookRequest(BaseModel):
    time_horizon: str = Field(default="medium_term", description="Time horizon")
    sectors: List[str] = Field(default=["Technology", "Banking", "Pharmaceuticals"], description="Sectors to analyze")


@router.post("/stock-analysis", response_model=Dict[str, Any])
async def analyze_stock(
    request: StockAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Perform comprehensive stock analysis using AI agents
    """
    try:
        # Prepare user profile
        user_profile = {
            "id": current_user.id,
            "risk_profile": current_user.risk_profile,
            "investment_experience": current_user.investment_experience,
            "age": current_user.age,
            "annual_income": current_user.annual_income,
            "investment_horizon_years": current_user.investment_horizon_years
        }
        
        # Prepare analysis request
        analysis_request = {
            "request_id": f"stock_analysis_{current_user.id}_{request.symbol}",
            "symbol": request.symbol,
            "exchange": request.exchange,
            "investment_amount": request.investment_amount,
            "user_profile": user_profile,
            "analysis_type": request.analysis_type
        }
        
        # Perform analysis using AI crew
        result = ai_crew.comprehensive_investment_analysis(analysis_request)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "data": result,
            "message": f"Stock analysis completed for {request.symbol}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stock analysis failed: {str(e)}"
        )


@router.post("/portfolio-optimization", response_model=Dict[str, Any])
async def optimize_portfolio(
    request: PortfolioOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Optimize portfolio using AI agents
    """
    try:
        # Prepare user profile
        user_profile = {
            "id": current_user.id,
            "risk_profile": current_user.risk_profile,
            "investment_experience": current_user.investment_experience,
            "age": current_user.age,
            "annual_income": current_user.annual_income,
            "monthly_expenses": current_user.monthly_expenses,
            "investment_horizon_years": current_user.investment_horizon_years
        }
        
        # Prepare optimization request
        optimization_request = {
            "request_id": f"portfolio_opt_{current_user.id}",
            "portfolio_data": request.portfolio_data,
            "user_profile": user_profile,
            "goals": request.goals,
            "optimization_type": request.optimization_type
        }
        
        # Perform optimization using AI crew
        result = ai_crew.portfolio_optimization_analysis(optimization_request)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "data": result,
            "message": "Portfolio optimization completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio optimization failed: {str(e)}"
        )


@router.post("/financial-planning", response_model=Dict[str, Any])
async def create_financial_plan(
    request: FinancialPlanningRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create comprehensive financial plan using AI agents
    """
    try:
        # Prepare user profile
        user_profile = {
            "id": current_user.id,
            "risk_profile": current_user.risk_profile,
            "investment_experience": current_user.investment_experience,
            "age": current_user.age,
            "annual_income": current_user.annual_income,
            "monthly_expenses": current_user.monthly_expenses,
            "current_savings": current_user.current_savings,
            "investment_horizon_years": current_user.investment_horizon_years,
            "financial_goals": current_user.financial_goals
        }
        
        # Prepare planning request
        planning_request = {
            "request_id": f"financial_plan_{current_user.id}",
            "user_profile": user_profile,
            "goals": request.goals,
            "current_portfolio": request.current_portfolio,
            "transactions": request.transactions,
            "planning_horizon": request.planning_horizon
        }
        
        # Create financial plan using AI crew
        result = ai_crew.financial_planning_consultation(planning_request)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "data": result,
            "message": "Financial planning consultation completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Financial planning failed: {str(e)}"
        )


@router.post("/risk-profiling", response_model=Dict[str, Any])
async def conduct_risk_profiling(
    request: RiskProfilingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Conduct comprehensive risk profiling using AI risk agent
    """
    try:
        # Prepare user profile
        user_profile = {
            "id": current_user.id,
            "age": current_user.age,
            "annual_income": current_user.annual_income,
            "monthly_expenses": current_user.monthly_expenses,
            "current_savings": current_user.current_savings,
            "investment_experience": current_user.investment_experience,
            "investment_horizon_years": current_user.investment_horizon_years
        }
        
        # Conduct risk profiling
        result = ai_crew.risk_agent.conduct_risk_profiling(
            request.questionnaire_responses, user_profile
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Update user's risk profile if assessment is complete
        if result.get("overall_risk_profile", {}).get("overall_risk_profile"):
            current_user.risk_profile = result["overall_risk_profile"]["overall_risk_profile"].lower()
            current_user.risk_assessment_score = result["overall_risk_profile"]["risk_score"]
            current_user.risk_assessment_date = db.query(func.now()).scalar()
            db.commit()
        
        return {
            "status": "success",
            "data": result,
            "message": "Risk profiling completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk profiling failed: {str(e)}"
        )


@router.post("/tax-planning", response_model=Dict[str, Any])
async def create_tax_plan(
    request: TaxPlanningRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create comprehensive tax plan using AI tax agent
    """
    try:
        # Prepare user profile
        user_profile = {
            "id": current_user.id,
            "annual_income": current_user.annual_income,
            "tax_bracket": current_user.tax_bracket,
            "pan_number": current_user.pan_number,
            "age": current_user.age
        }
        
        # Create tax plan
        result = ai_crew.tax_agent.create_comprehensive_tax_plan(
            user_profile, request.transactions, request.financial_year
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "data": result,
            "message": f"Tax planning completed for FY {request.financial_year}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tax planning failed: {str(e)}"
        )


@router.post("/market-outlook", response_model=Dict[str, Any])
async def get_market_outlook(
    request: MarketOutlookRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get comprehensive market outlook and investment themes
    """
    try:
        # Prepare market analysis request
        market_request = {
            "request_id": f"market_outlook_{current_user.id}",
            "time_horizon": request.time_horizon,
            "sectors": request.sectors
        }
        
        # Get market outlook using AI crew
        result = ai_crew.market_outlook_analysis(market_request)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "data": result,
            "message": f"Market outlook analysis completed for {request.time_horizon} horizon"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market outlook analysis failed: {str(e)}"
        )


@router.get("/agent-status", response_model=Dict[str, Any])
async def get_agent_status(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get status of all AI agents
    """
    try:
        status = ai_crew.get_agent_status()
        available_analyses = ai_crew.get_available_analyses()
        
        return {
            "status": "success",
            "data": {
                "agent_status": status,
                "available_analyses": available_analyses,
                "system_health": "Operational"
            },
            "message": "AI system status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/mutual-fund-analysis", response_model=Dict[str, Any])
async def analyze_mutual_fund(
    scheme_code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze mutual fund using AI analyst agent
    """
    try:
        # Analyze mutual fund
        result = ai_crew.analyst_agent.analyze_mutual_fund(scheme_code)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "data": result,
            "message": f"Mutual fund analysis completed for scheme {scheme_code}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mutual fund analysis failed: {str(e)}"
        )


@router.post("/compare-investments", response_model=Dict[str, Any])
async def compare_investments(
    investments: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Compare multiple investments using AI analyst agent
    """
    try:
        # Compare investments
        result = ai_crew.analyst_agent.compare_investments(investments)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "data": result,
            "message": f"Investment comparison completed for {len(investments)} investments"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investment comparison failed: {str(e)}"
        )
