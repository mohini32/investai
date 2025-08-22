"""
Tax Planning endpoints - Comprehensive tax optimization for Indian investors
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.tax import TaxRegime
from app.services.tax_service import TaxPlanningService

router = APIRouter()


# Pydantic models
class TaxProfileCreate(BaseModel):
    tax_regime: str = Field(..., description="Tax regime: old_regime or new_regime")
    annual_income: float = Field(..., ge=0, description="Annual income")
    age: int = Field(..., ge=18, le=100, description="Age")
    is_senior_citizen: bool = Field(default=False, description="Senior citizen status")
    is_super_senior_citizen: bool = Field(default=False, description="Super senior citizen status")
    has_disability: bool = Field(default=False, description="Disability status")
    employer_pf_contribution: float = Field(default=0, ge=0, description="Employer PF contribution")
    employer_nps_contribution: float = Field(default=0, ge=0, description="Employer NPS contribution")
    professional_tax: float = Field(default=0, ge=0, description="Professional tax")
    section_80c_investments: float = Field(default=0, ge=0, description="Current 80C investments")
    section_80d_premium: float = Field(default=0, ge=0, description="Health insurance premium")
    home_loan_interest: float = Field(default=0, ge=0, description="Home loan interest")
    home_loan_principal: float = Field(default=0, ge=0, description="Home loan principal")
    education_loan_interest: float = Field(default=0, ge=0, description="Education loan interest")
    risk_appetite_for_tax_saving: str = Field(default="moderate", description="Risk appetite")
    preferred_lock_in_period: int = Field(default=3, ge=1, le=30, description="Preferred lock-in period")
    assessment_year: str = Field(default="2024-25", description="Assessment year")


class TaxProfileUpdate(BaseModel):
    tax_regime: Optional[str] = Field(None, description="Tax regime")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income")
    age: Optional[int] = Field(None, ge=18, le=100, description="Age")
    is_senior_citizen: Optional[bool] = Field(None, description="Senior citizen status")
    is_super_senior_citizen: Optional[bool] = Field(None, description="Super senior citizen status")
    has_disability: Optional[bool] = Field(None, description="Disability status")
    employer_pf_contribution: Optional[float] = Field(None, ge=0, description="Employer PF contribution")
    employer_nps_contribution: Optional[float] = Field(None, ge=0, description="Employer NPS contribution")
    professional_tax: Optional[float] = Field(None, ge=0, description="Professional tax")
    section_80c_investments: Optional[float] = Field(None, ge=0, description="Current 80C investments")
    section_80d_premium: Optional[float] = Field(None, ge=0, description="Health insurance premium")
    home_loan_interest: Optional[float] = Field(None, ge=0, description="Home loan interest")
    home_loan_principal: Optional[float] = Field(None, ge=0, description="Home loan principal")
    education_loan_interest: Optional[float] = Field(None, ge=0, description="Education loan interest")
    risk_appetite_for_tax_saving: Optional[str] = Field(None, description="Risk appetite")
    preferred_lock_in_period: Optional[int] = Field(None, ge=1, le=30, description="Preferred lock-in period")


@router.post("/profile", response_model=Dict[str, Any])
async def create_tax_profile(
    profile_data: TaxProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create tax profile for user"""
    try:
        tax_service = TaxPlanningService(db)
        tax_profile = tax_service.create_tax_profile(
            current_user.id, 
            profile_data.dict()
        )
        
        return {
            "status": "success",
            "data": {
                "id": tax_profile.id,
                "tax_regime": tax_profile.tax_regime.value,
                "annual_income": tax_profile.annual_income,
                "age": tax_profile.age,
                "assessment_year": tax_profile.assessment_year,
                "created_at": tax_profile.created_at.isoformat()
            },
            "message": "Tax profile created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tax profile: {str(e)}"
        )


@router.get("/profile", response_model=Dict[str, Any])
async def get_tax_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax profile for user"""
    try:
        tax_service = TaxPlanningService(db)
        tax_profile = tax_service.get_tax_profile(current_user.id)
        
        if not tax_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax profile not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": tax_profile.id,
                "tax_regime": tax_profile.tax_regime.value,
                "annual_income": tax_profile.annual_income,
                "age": tax_profile.age,
                "is_senior_citizen": tax_profile.is_senior_citizen,
                "is_super_senior_citizen": tax_profile.is_super_senior_citizen,
                "has_disability": tax_profile.has_disability,
                "employer_pf_contribution": tax_profile.employer_pf_contribution,
                "employer_nps_contribution": tax_profile.employer_nps_contribution,
                "professional_tax": tax_profile.professional_tax,
                "section_80c_investments": tax_profile.section_80c_investments,
                "section_80d_premium": tax_profile.section_80d_premium,
                "home_loan_interest": tax_profile.home_loan_interest,
                "home_loan_principal": tax_profile.home_loan_principal,
                "education_loan_interest": tax_profile.education_loan_interest,
                "risk_appetite_for_tax_saving": tax_profile.risk_appetite_for_tax_saving,
                "preferred_lock_in_period": tax_profile.preferred_lock_in_period,
                "assessment_year": tax_profile.assessment_year,
                "created_at": tax_profile.created_at.isoformat(),
                "updated_at": tax_profile.updated_at.isoformat() if tax_profile.updated_at else None
            },
            "message": "Tax profile retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax profile: {str(e)}"
        )


@router.put("/profile", response_model=Dict[str, Any])
async def update_tax_profile(
    profile_data: TaxProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update tax profile"""
    try:
        tax_service = TaxPlanningService(db)
        
        # Filter out None values
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        
        tax_profile = tax_service.update_tax_profile(current_user.id, update_data)
        
        return {
            "status": "success",
            "data": {
                "id": tax_profile.id,
                "tax_regime": tax_profile.tax_regime.value,
                "annual_income": tax_profile.annual_income,
                "updated_at": tax_profile.updated_at.isoformat()
            },
            "message": "Tax profile updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tax profile: {str(e)}"
        )


@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_tax(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate comprehensive tax for user"""
    try:
        tax_service = TaxPlanningService(db)
        tax_profile = tax_service.get_tax_profile(current_user.id)
        
        if not tax_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax profile not found. Please create a tax profile first."
            )
        
        tax_calculation = tax_service.calculate_tax(tax_profile.id)
        
        return {
            "status": "success",
            "data": {
                "id": tax_calculation.id,
                "gross_income": tax_calculation.gross_income,
                "standard_deduction": tax_calculation.standard_deduction,
                "total_80c_deduction": tax_calculation.total_80c_deduction,
                "total_80d_deduction": tax_calculation.total_80d_deduction,
                "total_80ccd_1b_deduction": tax_calculation.total_80ccd_1b_deduction,
                "total_other_deductions": tax_calculation.total_other_deductions,
                "taxable_income": tax_calculation.taxable_income,
                "income_tax": tax_calculation.income_tax,
                "surcharge": tax_calculation.surcharge,
                "health_education_cess": tax_calculation.health_education_cess,
                "total_tax": tax_calculation.total_tax,
                "old_regime_tax": tax_calculation.old_regime_tax,
                "new_regime_tax": tax_calculation.new_regime_tax,
                "tax_savings_amount": tax_calculation.tax_savings_amount,
                "recommended_regime": tax_calculation.recommended_regime.value,
                "effective_tax_rate": (tax_calculation.total_tax / tax_calculation.gross_income) * 100,
                "calculation_date": tax_calculation.calculation_date.isoformat(),
                "assessment_year": tax_calculation.assessment_year
            },
            "message": "Tax calculation completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate tax: {str(e)}"
        )


@router.get("/regime-comparison", response_model=Dict[str, Any])
async def compare_tax_regimes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Compare old vs new tax regime"""
    try:
        tax_service = TaxPlanningService(db)
        comparison = tax_service.compare_tax_regimes(current_user.id)
        
        return {
            "status": "success",
            "data": comparison,
            "message": "Tax regime comparison completed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare tax regimes: {str(e)}"
        )


@router.get("/summary", response_model=Dict[str, Any])
async def get_tax_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive tax summary"""
    try:
        tax_service = TaxPlanningService(db)
        summary = tax_service.get_tax_summary(current_user.id)
        
        if "error" in summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary["error"]
            )
        
        return {
            "status": "success",
            "data": summary,
            "message": "Tax summary retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax summary: {str(e)}"
        )


@router.get("/recommendations", response_model=Dict[str, Any])
async def get_tax_saving_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get personalized tax-saving investment recommendations"""
    try:
        tax_service = TaxPlanningService(db)
        recommendations = tax_service.get_tax_saving_recommendations(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "recommendations_count": len(recommendations),
                "total_potential_savings": sum(r.get("tax_savings", 0) for r in recommendations)
            },
            "message": f"Retrieved {len(recommendations)} tax-saving recommendations"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax recommendations: {str(e)}"
        )


@router.get("/80c-optimization", response_model=Dict[str, Any])
async def get_section_80c_optimization(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get Section 80C optimization analysis"""
    try:
        tax_service = TaxPlanningService(db)
        optimization = tax_service.calculate_section_80c_optimization(current_user.id)
        
        return {
            "status": "success",
            "data": optimization,
            "message": "Section 80C optimization analysis completed"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get 80C optimization: {str(e)}"
        )


@router.post("/capital-gains/calculate", response_model=Dict[str, Any])
async def calculate_capital_gains(
    portfolio_id: Optional[int] = Query(None, description="Specific portfolio ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate capital gains from portfolio transactions"""
    try:
        tax_service = TaxPlanningService(db)
        capital_gains = tax_service.calculate_capital_gains(current_user.id, portfolio_id)

        # Aggregate data
        total_gains = sum(cg.capital_gain_loss for cg in capital_gains if cg.capital_gain_loss > 0)
        total_losses = sum(abs(cg.capital_gain_loss) for cg in capital_gains if cg.capital_gain_loss < 0)
        total_tax = sum(cg.tax_on_gain for cg in capital_gains)

        # Categorize by type
        gains_by_type = {}
        for cg in capital_gains:
            gain_type = cg.gain_type.value
            if gain_type not in gains_by_type:
                gains_by_type[gain_type] = {"count": 0, "total_gain": 0, "total_tax": 0}

            gains_by_type[gain_type]["count"] += 1
            gains_by_type[gain_type]["total_gain"] += cg.capital_gain_loss
            gains_by_type[gain_type]["total_tax"] += cg.tax_on_gain

        capital_gains_data = []
        for cg in capital_gains:
            capital_gains_data.append({
                "id": cg.id,
                "security_symbol": cg.security_symbol,
                "security_name": cg.security_name,
                "buy_date": cg.buy_date.isoformat(),
                "sell_date": cg.sell_date.isoformat(),
                "buy_price": cg.buy_price,
                "sell_price": cg.sell_price,
                "quantity": cg.sell_quantity,
                "capital_gain_loss": cg.capital_gain_loss,
                "gain_type": cg.gain_type.value,
                "holding_period_days": cg.holding_period_days,
                "applicable_tax_rate": cg.applicable_tax_rate,
                "tax_on_gain": cg.tax_on_gain,
                "assessment_year": cg.assessment_year
            })

        return {
            "status": "success",
            "data": {
                "capital_gains": capital_gains_data,
                "summary": {
                    "total_transactions": len(capital_gains),
                    "total_gains": total_gains,
                    "total_losses": total_losses,
                    "net_gains": total_gains - total_losses,
                    "total_tax": total_tax,
                    "gains_by_type": gains_by_type
                }
            },
            "message": f"Calculated capital gains for {len(capital_gains)} transactions"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate capital gains: {str(e)}"
        )


@router.get("/optimization-suggestions", response_model=Dict[str, Any])
async def get_tax_optimization_suggestions(
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, critical"),
    suggestion_type: Optional[str] = Query(None, description="Filter by suggestion type"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered tax optimization suggestions"""
    try:
        tax_service = TaxPlanningService(db)
        tax_profile = tax_service.get_tax_profile(current_user.id)

        if not tax_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax profile not found"
            )

        # Generate fresh suggestions
        suggestions = tax_service.generate_tax_optimization_suggestions(tax_profile.id)

        # Apply filters
        if priority:
            suggestions = [s for s in suggestions if s.priority == priority]

        if suggestion_type:
            suggestions = [s for s in suggestions if s.suggestion_type == suggestion_type]

        suggestions_data = []
        for suggestion in suggestions:
            suggestions_data.append({
                "id": suggestion.id,
                "suggestion_type": suggestion.suggestion_type,
                "title": suggestion.title,
                "description": suggestion.description,
                "potential_tax_savings": suggestion.potential_tax_savings,
                "investment_required": suggestion.investment_required,
                "net_benefit": suggestion.net_benefit,
                "timeline": suggestion.timeline,
                "priority": suggestion.priority,
                "risk_level": suggestion.risk_level,
                "confidence_score": suggestion.confidence_score,
                "is_implemented": suggestion.is_implemented,
                "created_at": suggestion.created_at.isoformat()
            })

        # Calculate summary
        total_potential_savings = sum(s["potential_tax_savings"] for s in suggestions_data)
        total_investment_required = sum(s["investment_required"] for s in suggestions_data)

        priority_distribution = {}
        for suggestion in suggestions_data:
            priority_level = suggestion["priority"]
            priority_distribution[priority_level] = priority_distribution.get(priority_level, 0) + 1

        return {
            "status": "success",
            "data": {
                "suggestions": suggestions_data,
                "summary": {
                    "total_suggestions": len(suggestions_data),
                    "total_potential_savings": total_potential_savings,
                    "total_investment_required": total_investment_required,
                    "net_benefit": total_potential_savings,
                    "priority_distribution": priority_distribution
                }
            },
            "message": f"Retrieved {len(suggestions_data)} tax optimization suggestions"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get optimization suggestions: {str(e)}"
        )


@router.get("/calendar", response_model=Dict[str, Any])
async def get_tax_calendar(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get tax calendar with important dates and deadlines"""
    try:
        tax_service = TaxPlanningService(db)
        calendar_events = tax_service.get_tax_calendar(current_user.id)

        # Categorize events by priority
        critical_events = [e for e in calendar_events if e["priority"] == "critical"]
        high_priority_events = [e for e in calendar_events if e["priority"] == "high"]
        upcoming_events = [e for e in calendar_events if e["action_required"]]

        return {
            "status": "success",
            "data": {
                "calendar_events": calendar_events,
                "summary": {
                    "total_events": len(calendar_events),
                    "critical_events": len(critical_events),
                    "high_priority_events": len(high_priority_events),
                    "upcoming_actions": len(upcoming_events)
                },
                "critical_deadlines": critical_events,
                "upcoming_actions": upcoming_events
            },
            "message": f"Retrieved {len(calendar_events)} tax calendar events"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax calendar: {str(e)}"
        )


@router.get("/calculators/elss", response_model=Dict[str, Any])
async def calculate_elss_returns(
    investment_amount: float = Query(..., ge=500, le=150000, description="ELSS investment amount"),
    investment_period_years: int = Query(default=5, ge=3, le=30, description="Investment period in years"),
    expected_return_rate: float = Query(default=12.0, ge=5.0, le=25.0, description="Expected annual return rate"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate ELSS investment returns and tax savings"""
    try:
        tax_service = TaxPlanningService(db)
        tax_profile = tax_service.get_tax_profile(current_user.id)

        if not tax_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax profile not found"
            )

        # Calculate tax savings
        marginal_rate = tax_service._get_marginal_tax_rate(tax_profile)
        tax_savings = investment_amount * marginal_rate * 1.04  # Including cess

        # Calculate future value
        future_value = investment_amount * ((1 + expected_return_rate / 100) ** investment_period_years)

        # Calculate effective cost
        effective_cost = investment_amount - tax_savings

        # Calculate returns
        total_returns = future_value - investment_amount
        effective_returns = future_value - effective_cost

        # Calculate CAGR
        cagr = ((future_value / investment_amount) ** (1 / investment_period_years) - 1) * 100
        effective_cagr = ((future_value / effective_cost) ** (1 / investment_period_years) - 1) * 100

        return {
            "status": "success",
            "data": {
                "investment_details": {
                    "investment_amount": investment_amount,
                    "investment_period_years": investment_period_years,
                    "expected_return_rate": expected_return_rate,
                    "marginal_tax_rate": marginal_rate * 100
                },
                "tax_benefits": {
                    "tax_savings": tax_savings,
                    "effective_cost": effective_cost,
                    "tax_savings_percentage": (tax_savings / investment_amount) * 100
                },
                "returns_projection": {
                    "future_value": future_value,
                    "total_returns": total_returns,
                    "effective_returns": effective_returns,
                    "cagr": cagr,
                    "effective_cagr": effective_cagr
                },
                "comparison": {
                    "without_tax_benefit": {
                        "investment": investment_amount,
                        "returns": total_returns,
                        "cagr": cagr
                    },
                    "with_tax_benefit": {
                        "effective_investment": effective_cost,
                        "returns": effective_returns,
                        "effective_cagr": effective_cagr
                    }
                }
            },
            "message": "ELSS calculator results generated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate ELSS returns: {str(e)}"
        )


@router.get("/calculators/ppf", response_model=Dict[str, Any])
async def calculate_ppf_returns(
    annual_investment: float = Query(..., ge=500, le=150000, description="Annual PPF investment"),
    investment_period_years: int = Query(default=15, ge=15, le=50, description="Investment period in years"),
    current_ppf_rate: float = Query(default=7.1, ge=6.0, le=10.0, description="Current PPF interest rate"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate PPF investment returns and tax benefits"""
    try:
        tax_service = TaxPlanningService(db)
        tax_profile = tax_service.get_tax_profile(current_user.id)

        if not tax_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax profile not found"
            )

        # Calculate tax savings per year
        marginal_rate = tax_service._get_marginal_tax_rate(tax_profile)
        annual_tax_savings = annual_investment * marginal_rate * 1.04

        # Calculate PPF maturity using compound interest formula
        # PPF compounds annually
        total_investment = annual_investment * investment_period_years

        # Calculate future value of annuity
        r = current_ppf_rate / 100
        future_value = annual_investment * (((1 + r) ** investment_period_years - 1) / r)

        # Calculate total tax savings
        total_tax_savings = annual_tax_savings * investment_period_years

        # Calculate effective investment
        effective_annual_investment = annual_investment - annual_tax_savings
        total_effective_investment = effective_annual_investment * investment_period_years

        # Calculate returns
        total_returns = future_value - total_investment
        effective_returns = future_value - total_effective_investment

        return {
            "status": "success",
            "data": {
                "investment_details": {
                    "annual_investment": annual_investment,
                    "investment_period_years": investment_period_years,
                    "current_ppf_rate": current_ppf_rate,
                    "total_investment": total_investment,
                    "marginal_tax_rate": marginal_rate * 100
                },
                "tax_benefits": {
                    "annual_tax_savings": annual_tax_savings,
                    "total_tax_savings": total_tax_savings,
                    "effective_annual_investment": effective_annual_investment,
                    "total_effective_investment": total_effective_investment
                },
                "maturity_details": {
                    "maturity_amount": future_value,
                    "total_returns": total_returns,
                    "effective_returns": effective_returns,
                    "tax_free_returns": True
                },
                "yearly_breakdown": [
                    {
                        "year": year,
                        "investment": annual_investment,
                        "tax_savings": annual_tax_savings,
                        "effective_investment": effective_annual_investment,
                        "accumulated_value": annual_investment * (((1 + r) ** year - 1) / r) if year > 0 else 0
                    }
                    for year in range(1, min(investment_period_years + 1, 16))  # Show first 15 years
                ]
            },
            "message": "PPF calculator results generated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate PPF returns: {str(e)}"
        )
