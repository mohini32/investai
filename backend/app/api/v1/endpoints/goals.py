"""
Financial Goals endpoints - Comprehensive goal-based financial planning
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.goals import GoalType, GoalStatus, GoalPriority
from app.services.goal_service import GoalPlanningService

router = APIRouter()


# Pydantic models
class GoalCreate(BaseModel):
    name: str = Field(..., description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    goal_type: GoalType = Field(..., description="Type of financial goal")
    priority: GoalPriority = Field(default=GoalPriority.MEDIUM, description="Goal priority")
    target_amount: float = Field(..., gt=0, description="Target amount")
    current_amount: float = Field(default=0.0, ge=0, description="Current amount")
    monthly_contribution: float = Field(default=0.0, ge=0, description="Monthly contribution")
    target_date: datetime = Field(..., description="Target completion date")
    risk_level: str = Field(default="moderate", description="Risk level (conservative/moderate/aggressive)")
    inflation_rate: float = Field(default=6.0, ge=0, le=20, description="Expected inflation rate")
    expected_return_rate: float = Field(default=12.0, ge=0, le=30, description="Expected return rate")


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    priority: Optional[GoalPriority] = Field(None, description="Goal priority")
    target_amount: Optional[float] = Field(None, gt=0, description="Target amount")
    monthly_contribution: Optional[float] = Field(None, ge=0, description="Monthly contribution")
    target_date: Optional[datetime] = Field(None, description="Target completion date")
    status: Optional[GoalStatus] = Field(None, description="Goal status")
    risk_level: Optional[str] = Field(None, description="Risk level")
    inflation_rate: Optional[float] = Field(None, ge=0, le=20, description="Inflation rate")
    expected_return_rate: Optional[float] = Field(None, ge=0, le=30, description="Expected return rate")


class ContributionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Contribution amount")
    contribution_date: Optional[datetime] = Field(None, description="Contribution date")
    contribution_type: str = Field(default="manual", description="Contribution type")
    source_account: Optional[str] = Field(None, description="Source account")
    transaction_reference: Optional[str] = Field(None, description="Transaction reference")
    notes: Optional[str] = Field(None, description="Notes")


class MilestoneCreate(BaseModel):
    name: str = Field(..., description="Milestone name")
    description: Optional[str] = Field(None, description="Milestone description")
    target_amount: float = Field(..., gt=0, description="Target amount")
    target_date: datetime = Field(..., description="Target date")


class RetirementCalculationRequest(BaseModel):
    current_age: int = Field(..., ge=18, le=65, description="Current age")
    retirement_age: int = Field(default=60, ge=50, le=75, description="Retirement age")
    current_monthly_expenses: float = Field(..., gt=0, description="Current monthly expenses")
    inflation_rate: float = Field(default=6.0, ge=0, le=20, description="Inflation rate")
    expected_return: float = Field(default=12.0, ge=0, le=30, description="Expected return")
    life_expectancy: int = Field(default=80, ge=70, le=100, description="Life expectancy")


class EducationCalculationRequest(BaseModel):
    current_education_cost: float = Field(..., gt=0, description="Current education cost")
    years_to_education: int = Field(..., gt=0, le=25, description="Years to education")
    education_inflation: float = Field(default=10.0, ge=0, le=25, description="Education inflation rate")
    expected_return: float = Field(default=12.0, ge=0, le=30, description="Expected return")


class EmergencyFundRequest(BaseModel):
    monthly_expenses: float = Field(..., gt=0, description="Monthly expenses")
    months_coverage: int = Field(default=6, ge=3, le=12, description="Months of coverage")
    current_emergency_fund: float = Field(default=0.0, ge=0, description="Current emergency fund")
    build_timeline_months: int = Field(default=12, ge=1, le=60, description="Timeline to build fund")


class HomePurchaseRequest(BaseModel):
    property_cost: float = Field(..., gt=0, description="Current property cost")
    down_payment_percentage: float = Field(default=20.0, ge=10, le=50, description="Down payment percentage")
    years_to_purchase: int = Field(..., gt=0, le=20, description="Years to purchase")
    property_appreciation: float = Field(default=8.0, ge=0, le=20, description="Property appreciation rate")
    expected_return: float = Field(default=12.0, ge=0, le=30, description="Expected return")
    loan_tenure_years: int = Field(default=20, ge=5, le=30, description="Loan tenure")
    loan_interest_rate: float = Field(default=9.0, ge=5, le=15, description="Loan interest rate")


# Goal CRUD endpoints
@router.post("/", response_model=Dict[str, Any])
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new financial goal"""
    try:
        goal_service = GoalPlanningService(db)
        goal = goal_service.create_goal(current_user.id, goal_data.dict())
        
        return {
            "status": "success",
            "data": {
                "id": goal.id,
                "name": goal.name,
                "goal_type": goal.goal_type.value,
                "target_amount": goal.target_amount,
                "target_date": goal.target_date.isoformat(),
                "required_monthly_amount": goal.required_monthly_amount,
                "progress_percentage": goal.progress_percentage,
                "is_on_track": goal.is_on_track
            },
            "message": f"Goal '{goal.name}' created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create goal: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_user_goals(
    status_filter: Optional[GoalStatus] = Query(None, description="Filter by goal status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all goals for the current user"""
    try:
        goal_service = GoalPlanningService(db)
        goals = goal_service.get_user_goals(current_user.id, status_filter)
        
        goals_data = []
        for goal in goals:
            goals_data.append({
                "id": goal.id,
                "name": goal.name,
                "description": goal.description,
                "goal_type": goal.goal_type.value,
                "priority": goal.priority.value,
                "status": goal.status.value,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "monthly_contribution": goal.monthly_contribution,
                "target_date": goal.target_date.isoformat(),
                "progress_percentage": goal.progress_percentage,
                "is_on_track": goal.is_on_track,
                "required_monthly_amount": goal.required_monthly_amount,
                "months_remaining": goal.months_remaining,
                "created_at": goal.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "data": {
                "goals": goals_data,
                "count": len(goals_data)
            },
            "message": f"Retrieved {len(goals_data)} goals"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve goals: {str(e)}"
        )


@router.get("/overview", response_model=Dict[str, Any])
async def get_goals_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive overview of user's goals"""
    try:
        goal_service = GoalPlanningService(db)
        overview = goal_service.get_user_goal_overview(current_user.id)
        
        return {
            "status": "success",
            "data": overview,
            "message": "Goals overview retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goals overview: {str(e)}"
        )


@router.get("/{goal_id}", response_model=Dict[str, Any])
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific goal details"""
    try:
        goal_service = GoalPlanningService(db)
        goal = goal_service.get_goal(goal_id, current_user.id)
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": goal.id,
                "name": goal.name,
                "description": goal.description,
                "goal_type": goal.goal_type.value,
                "priority": goal.priority.value,
                "status": goal.status.value,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "monthly_contribution": goal.monthly_contribution,
                "target_date": goal.target_date.isoformat(),
                "start_date": goal.start_date.isoformat(),
                "progress_percentage": goal.progress_percentage,
                "is_on_track": goal.is_on_track,
                "required_monthly_amount": goal.required_monthly_amount,
                "months_remaining": goal.months_remaining,
                "risk_level": goal.risk_level,
                "inflation_rate": goal.inflation_rate,
                "expected_return_rate": goal.expected_return_rate,
                "created_at": goal.created_at.isoformat(),
                "updated_at": goal.updated_at.isoformat() if goal.updated_at else None
            },
            "message": "Goal retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve goal: {str(e)}"
        )


@router.put("/{goal_id}", response_model=Dict[str, Any])
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update goal details"""
    try:
        goal_service = GoalPlanningService(db)
        
        # Prepare update data (exclude None values)
        update_data = {k: v for k, v in goal_data.dict().items() if v is not None}
        
        goal = goal_service.update_goal(goal_id, current_user.id, update_data)
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": goal.id,
                "name": goal.name,
                "target_amount": goal.target_amount,
                "progress_percentage": goal.progress_percentage,
                "is_on_track": goal.is_on_track,
                "required_monthly_amount": goal.required_monthly_amount,
                "updated_at": goal.updated_at.isoformat() if goal.updated_at else None
            },
            "message": "Goal updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update goal: {str(e)}"
        )


@router.delete("/{goal_id}", response_model=Dict[str, Any])
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a goal"""
    try:
        goal_service = GoalPlanningService(db)
        success = goal_service.delete_goal(goal_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return {
            "status": "success",
            "message": "Goal deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete goal: {str(e)}"
        )


# Goal Calculators
@router.post("/calculators/retirement", response_model=Dict[str, Any])
async def calculate_retirement_goal(
    request: RetirementCalculationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate retirement goal requirements"""
    try:
        goal_service = GoalPlanningService(db)
        calculation = goal_service.calculate_retirement_goal(request.dict())

        return {
            "status": "success",
            "data": {
                "calculation_type": "retirement",
                "inputs": request.dict(),
                "results": calculation,
                "recommendations": [
                    f"Start investing ₹{calculation['monthly_sip_required']:,.0f} monthly",
                    f"Your retirement corpus will be ₹{calculation['corpus_required']:,.0f}",
                    f"Total wealth creation: ₹{calculation['wealth_creation']:,.0f}",
                    "Consider increasing SIP by 10% annually"
                ]
            },
            "message": "Retirement calculation completed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate retirement goal: {str(e)}"
        )


@router.post("/calculators/education", response_model=Dict[str, Any])
async def calculate_education_goal(
    request: EducationCalculationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate education goal requirements"""
    try:
        goal_service = GoalPlanningService(db)
        calculation = goal_service.calculate_education_goal(request.dict())

        return {
            "status": "success",
            "data": {
                "calculation_type": "education",
                "inputs": request.dict(),
                "results": calculation,
                "recommendations": [
                    f"Start investing ₹{calculation['monthly_sip_required']:,.0f} monthly",
                    f"Education cost will be ₹{calculation['future_cost']:,.0f}",
                    f"Cost will increase by {calculation['cost_inflation_factor']:.1f}x",
                    "Consider child education plans and ELSS funds"
                ]
            },
            "message": "Education calculation completed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate education goal: {str(e)}"
        )


@router.post("/calculators/emergency-fund", response_model=Dict[str, Any])
async def calculate_emergency_fund(
    request: EmergencyFundRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate emergency fund requirements"""
    try:
        goal_service = GoalPlanningService(db)
        calculation = goal_service.calculate_emergency_fund(request.dict())

        return {
            "status": "success",
            "data": {
                "calculation_type": "emergency_fund",
                "inputs": request.dict(),
                "results": calculation,
                "recommendations": [
                    f"Build emergency fund of ₹{calculation['required_amount']:,.0f}",
                    f"Save ₹{calculation['monthly_contribution_required']:,.0f} monthly",
                    f"You're {calculation['completion_percentage']:.1f}% there",
                    "Keep emergency fund in liquid investments"
                ]
            },
            "message": "Emergency fund calculation completed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate emergency fund: {str(e)}"
        )


@router.post("/calculators/home-purchase", response_model=Dict[str, Any])
async def calculate_home_purchase_goal(
    request: HomePurchaseRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Calculate home purchase goal requirements"""
    try:
        goal_service = GoalPlanningService(db)
        calculation = goal_service.calculate_home_purchase_goal(request.dict())

        return {
            "status": "success",
            "data": {
                "calculation_type": "home_purchase",
                "inputs": request.dict(),
                "results": calculation,
                "recommendations": [
                    f"Save ₹{calculation['monthly_sip_required']:,.0f} monthly for down payment",
                    f"Down payment required: ₹{calculation['down_payment_required']:,.0f}",
                    f"Estimated EMI: ₹{calculation['estimated_emi']:,.0f}",
                    "Consider home loan pre-approval"
                ]
            },
            "message": "Home purchase calculation completed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate home purchase goal: {str(e)}"
        )


# Contributions
@router.post("/{goal_id}/contributions", response_model=Dict[str, Any])
async def add_contribution(
    goal_id: int,
    contribution_data: ContributionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Add a contribution to a goal"""
    try:
        goal_service = GoalPlanningService(db)
        contribution = goal_service.add_contribution(
            goal_id, current_user.id, contribution_data.dict()
        )

        return {
            "status": "success",
            "data": {
                "id": contribution.id,
                "amount": contribution.amount,
                "contribution_date": contribution.contribution_date.isoformat(),
                "contribution_type": contribution.contribution_type,
                "notes": contribution.notes
            },
            "message": f"Added contribution of ₹{contribution.amount:,.0f}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add contribution: {str(e)}"
        )


@router.get("/{goal_id}/contributions", response_model=Dict[str, Any])
async def get_goal_contributions(
    goal_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get contributions for a goal"""
    try:
        goal_service = GoalPlanningService(db)
        contributions = goal_service.get_goal_contributions(goal_id, current_user.id, limit)

        contributions_data = []
        for contribution in contributions:
            contributions_data.append({
                "id": contribution.id,
                "amount": contribution.amount,
                "contribution_date": contribution.contribution_date.isoformat(),
                "contribution_type": contribution.contribution_type,
                "source_account": contribution.source_account,
                "transaction_reference": contribution.transaction_reference,
                "notes": contribution.notes,
                "created_at": contribution.created_at.isoformat()
            })

        return {
            "status": "success",
            "data": {
                "contributions": contributions_data,
                "count": len(contributions_data)
            },
            "message": f"Retrieved {len(contributions_data)} contributions"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contributions: {str(e)}"
        )


# Milestones
@router.post("/{goal_id}/milestones", response_model=Dict[str, Any])
async def create_milestone(
    goal_id: int,
    milestone_data: MilestoneCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a milestone for a goal"""
    try:
        goal_service = GoalPlanningService(db)
        milestone = goal_service.create_milestone(
            goal_id, current_user.id, milestone_data.dict()
        )

        return {
            "status": "success",
            "data": {
                "id": milestone.id,
                "name": milestone.name,
                "description": milestone.description,
                "target_amount": milestone.target_amount,
                "target_date": milestone.target_date.isoformat(),
                "is_completed": milestone.is_completed
            },
            "message": f"Milestone '{milestone.name}' created successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create milestone: {str(e)}"
        )


@router.get("/{goal_id}/milestones", response_model=Dict[str, Any])
async def get_goal_milestones(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get milestones for a goal"""
    try:
        goal_service = GoalPlanningService(db)
        milestones = goal_service.get_goal_milestones(goal_id, current_user.id)

        milestones_data = []
        for milestone in milestones:
            milestones_data.append({
                "id": milestone.id,
                "name": milestone.name,
                "description": milestone.description,
                "target_amount": milestone.target_amount,
                "target_date": milestone.target_date.isoformat(),
                "is_completed": milestone.is_completed,
                "completed_at": milestone.completed_at.isoformat() if milestone.completed_at else None,
                "created_at": milestone.created_at.isoformat()
            })

        return {
            "status": "success",
            "data": {
                "milestones": milestones_data,
                "count": len(milestones_data),
                "completed_count": len([m for m in milestones_data if m["is_completed"]])
            },
            "message": f"Retrieved {len(milestones_data)} milestones"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get milestones: {str(e)}"
        )


# AI Analysis
@router.post("/{goal_id}/analyze", response_model=Dict[str, Any])
async def analyze_goal_with_ai(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Analyze goal using AI"""
    try:
        goal_service = GoalPlanningService(db)
        analysis = goal_service.analyze_goal_with_ai(goal_id, current_user.id)

        return {
            "status": "success",
            "data": analysis,
            "message": "Goal AI analysis completed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze goal: {str(e)}"
        )


@router.get("/{goal_id}/recommendations", response_model=Dict[str, Any])
async def get_goal_recommendations(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-generated recommendations for a goal"""
    try:
        goal_service = GoalPlanningService(db)
        recommendations = goal_service.get_goal_recommendations(goal_id, current_user.id)

        recommendations_data = []
        for rec in recommendations:
            recommendations_data.append({
                "id": rec.id,
                "recommendation_type": rec.recommendation_type,
                "title": rec.title,
                "description": rec.description,
                "confidence_score": rec.confidence_score,
                "potential_impact": rec.potential_impact,
                "is_accepted": rec.is_accepted,
                "created_at": rec.created_at.isoformat()
            })

        return {
            "status": "success",
            "data": {
                "recommendations": recommendations_data,
                "count": len(recommendations_data)
            },
            "message": f"Retrieved {len(recommendations_data)} recommendations"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )
