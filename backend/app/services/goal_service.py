"""
Goal Service - Comprehensive financial goal planning and management
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta, date
import json
import logging
import math

from app.models.goals import (
    FinancialGoal, GoalMilestone, GoalContribution, GoalTemplate, 
    GoalRecommendation, GoalAlert, GoalType, GoalStatus, GoalPriority
)
from app.models.user import User
from app.ai.crew import InvestAICrew

logger = logging.getLogger(__name__)


class GoalPlanningService:
    """Service for comprehensive goal planning and management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_crew = InvestAICrew()
    
    # Goal CRUD Operations
    def create_goal(self, user_id: int, goal_data: Dict[str, Any]) -> FinancialGoal:
        """Create a new financial goal"""
        try:
            goal = FinancialGoal(
                user_id=user_id,
                name=goal_data["name"],
                description=goal_data.get("description"),
                goal_type=GoalType(goal_data["goal_type"]),
                priority=GoalPriority(goal_data.get("priority", "medium")),
                target_amount=goal_data["target_amount"],
                current_amount=goal_data.get("current_amount", 0.0),
                monthly_contribution=goal_data.get("monthly_contribution", 0.0),
                target_date=goal_data["target_date"],
                risk_level=goal_data.get("risk_level", "moderate"),
                inflation_rate=goal_data.get("inflation_rate", 6.0),
                expected_return_rate=goal_data.get("expected_return_rate", 12.0)
            )
            
            # Calculate derived fields
            self._calculate_goal_metrics(goal)
            
            self.db.add(goal)
            self.db.commit()
            self.db.refresh(goal)
            
            # Create default milestones
            self._create_default_milestones(goal)
            
            # Generate initial recommendations
            self._generate_goal_recommendations(goal)
            
            logger.info(f"Created goal {goal.id} for user {user_id}")
            return goal
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create goal: {str(e)}")
            raise
    
    def get_user_goals(self, user_id: int, status: Optional[GoalStatus] = None) -> List[FinancialGoal]:
        """Get all goals for a user"""
        query = self.db.query(FinancialGoal).filter(FinancialGoal.user_id == user_id)
        
        if status:
            query = query.filter(FinancialGoal.status == status)
        
        return query.order_by(desc(FinancialGoal.priority), FinancialGoal.target_date).all()
    
    def get_goal(self, goal_id: int, user_id: int) -> Optional[FinancialGoal]:
        """Get a specific goal"""
        return self.db.query(FinancialGoal).filter(
            and_(FinancialGoal.id == goal_id, FinancialGoal.user_id == user_id)
        ).first()
    
    def update_goal(self, goal_id: int, user_id: int, updates: Dict[str, Any]) -> Optional[FinancialGoal]:
        """Update goal details"""
        try:
            goal = self.get_goal(goal_id, user_id)
            if not goal:
                return None
            
            # Update fields
            for key, value in updates.items():
                if hasattr(goal, key):
                    setattr(goal, key, value)
            
            # Recalculate metrics
            self._calculate_goal_metrics(goal)
            
            self.db.commit()
            self.db.refresh(goal)
            
            # Generate new recommendations if significant changes
            if any(key in updates for key in ["target_amount", "target_date", "monthly_contribution"]):
                self._generate_goal_recommendations(goal)
            
            logger.info(f"Updated goal {goal_id}")
            return goal
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update goal {goal_id}: {str(e)}")
            raise
    
    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        """Delete a goal"""
        try:
            goal = self.get_goal(goal_id, user_id)
            if not goal:
                return False
            
            self.db.delete(goal)
            self.db.commit()
            
            logger.info(f"Deleted goal {goal_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete goal {goal_id}: {str(e)}")
            raise
    
    # Goal Calculations and Analysis
    def calculate_retirement_goal(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate retirement goal requirements"""
        try:
            current_age = user_data["current_age"]
            retirement_age = user_data.get("retirement_age", 60)
            current_monthly_expenses = user_data["current_monthly_expenses"]
            inflation_rate = user_data.get("inflation_rate", 6.0) / 100
            expected_return = user_data.get("expected_return", 12.0) / 100
            life_expectancy = user_data.get("life_expectancy", 80)
            
            years_to_retirement = retirement_age - current_age
            retirement_years = life_expectancy - retirement_age
            
            # Calculate future monthly expenses at retirement
            future_monthly_expenses = current_monthly_expenses * ((1 + inflation_rate) ** years_to_retirement)
            
            # Calculate corpus required (considering inflation during retirement)
            # Using present value of annuity formula
            real_return_during_retirement = (expected_return - inflation_rate) / (1 + inflation_rate)
            
            if real_return_during_retirement > 0:
                corpus_required = future_monthly_expenses * 12 * (
                    (1 - (1 + real_return_during_retirement) ** (-retirement_years)) / real_return_during_retirement
                )
            else:
                corpus_required = future_monthly_expenses * 12 * retirement_years
            
            # Calculate monthly SIP required
            monthly_return = expected_return / 12
            months_to_retirement = years_to_retirement * 12
            
            if monthly_return > 0:
                monthly_sip = corpus_required * monthly_return / (((1 + monthly_return) ** months_to_retirement) - 1)
            else:
                monthly_sip = corpus_required / months_to_retirement
            
            return {
                "years_to_retirement": years_to_retirement,
                "future_monthly_expenses": future_monthly_expenses,
                "corpus_required": corpus_required,
                "monthly_sip_required": monthly_sip,
                "total_investment": monthly_sip * months_to_retirement,
                "wealth_creation": corpus_required - (monthly_sip * months_to_retirement),
                "replacement_ratio": (future_monthly_expenses / current_monthly_expenses) * 100
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate retirement goal: {str(e)}")
            raise
    
    def calculate_education_goal(self, education_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate education goal requirements"""
        try:
            current_cost = education_data["current_education_cost"]
            years_to_education = education_data["years_to_education"]
            education_inflation = education_data.get("education_inflation", 10.0) / 100
            expected_return = education_data.get("expected_return", 12.0) / 100
            
            # Calculate future cost of education
            future_cost = current_cost * ((1 + education_inflation) ** years_to_education)
            
            # Calculate monthly SIP required
            monthly_return = expected_return / 12
            months = years_to_education * 12
            
            if monthly_return > 0:
                monthly_sip = future_cost * monthly_return / (((1 + monthly_return) ** months) - 1)
            else:
                monthly_sip = future_cost / months
            
            return {
                "current_cost": current_cost,
                "future_cost": future_cost,
                "years_to_education": years_to_education,
                "monthly_sip_required": monthly_sip,
                "total_investment": monthly_sip * months,
                "cost_inflation_factor": future_cost / current_cost
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate education goal: {str(e)}")
            raise
    
    def calculate_emergency_fund(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate emergency fund requirements"""
        try:
            monthly_expenses = user_data["monthly_expenses"]
            months_coverage = user_data.get("months_coverage", 6)
            current_emergency_fund = user_data.get("current_emergency_fund", 0)
            
            required_amount = monthly_expenses * months_coverage
            shortfall = max(0, required_amount - current_emergency_fund)
            
            # Suggest timeline to build emergency fund (typically 6-12 months)
            build_timeline_months = user_data.get("build_timeline_months", 12)
            monthly_contribution = shortfall / build_timeline_months if build_timeline_months > 0 else 0
            
            return {
                "required_amount": required_amount,
                "current_amount": current_emergency_fund,
                "shortfall": shortfall,
                "months_coverage": months_coverage,
                "monthly_contribution_required": monthly_contribution,
                "build_timeline_months": build_timeline_months,
                "completion_percentage": (current_emergency_fund / required_amount * 100) if required_amount > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate emergency fund: {str(e)}")
            raise
    
    def calculate_home_purchase_goal(self, home_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate home purchase goal requirements"""
        try:
            property_cost = home_data["property_cost"]
            down_payment_percentage = home_data.get("down_payment_percentage", 20) / 100
            years_to_purchase = home_data["years_to_purchase"]
            property_appreciation = home_data.get("property_appreciation", 8.0) / 100
            expected_return = home_data.get("expected_return", 12.0) / 100
            
            # Calculate future property cost
            future_property_cost = property_cost * ((1 + property_appreciation) ** years_to_purchase)
            
            # Calculate down payment required
            down_payment_required = future_property_cost * down_payment_percentage
            
            # Calculate monthly SIP for down payment
            monthly_return = expected_return / 12
            months = years_to_purchase * 12
            
            if monthly_return > 0:
                monthly_sip = down_payment_required * monthly_return / (((1 + monthly_return) ** months) - 1)
            else:
                monthly_sip = down_payment_required / months
            
            # Calculate loan details
            loan_amount = future_property_cost - down_payment_required
            loan_tenure_years = home_data.get("loan_tenure_years", 20)
            loan_interest_rate = home_data.get("loan_interest_rate", 9.0) / 100
            
            # Calculate EMI
            monthly_loan_rate = loan_interest_rate / 12
            loan_months = loan_tenure_years * 12
            
            if monthly_loan_rate > 0:
                emi = loan_amount * monthly_loan_rate * ((1 + monthly_loan_rate) ** loan_months) / (((1 + monthly_loan_rate) ** loan_months) - 1)
            else:
                emi = loan_amount / loan_months
            
            return {
                "current_property_cost": property_cost,
                "future_property_cost": future_property_cost,
                "down_payment_required": down_payment_required,
                "loan_amount": loan_amount,
                "monthly_sip_required": monthly_sip,
                "estimated_emi": emi,
                "total_investment_for_down_payment": monthly_sip * months,
                "years_to_purchase": years_to_purchase
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate home purchase goal: {str(e)}")
            raise
    
    # Contribution Management
    def add_contribution(self, goal_id: int, user_id: int, contribution_data: Dict[str, Any]) -> GoalContribution:
        """Add a contribution to a goal"""
        try:
            goal = self.get_goal(goal_id, user_id)
            if not goal:
                raise ValueError("Goal not found")
            
            contribution = GoalContribution(
                goal_id=goal_id,
                amount=contribution_data["amount"],
                contribution_date=contribution_data.get("contribution_date", datetime.now()),
                contribution_type=contribution_data.get("contribution_type", "manual"),
                source_account=contribution_data.get("source_account"),
                transaction_reference=contribution_data.get("transaction_reference"),
                notes=contribution_data.get("notes")
            )
            
            self.db.add(contribution)
            
            # Update goal current amount
            goal.current_amount += contribution.amount
            
            # Recalculate goal metrics
            self._calculate_goal_metrics(goal)
            
            # Check for milestone completion
            self._check_milestone_completion(goal)
            
            # Generate alerts if needed
            self._check_goal_alerts(goal)
            
            self.db.commit()
            self.db.refresh(contribution)
            
            logger.info(f"Added contribution of ₹{contribution.amount} to goal {goal_id}")
            return contribution
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add contribution: {str(e)}")
            raise
    
    def get_goal_contributions(self, goal_id: int, user_id: int, limit: int = 50) -> List[GoalContribution]:
        """Get contributions for a goal"""
        goal = self.get_goal(goal_id, user_id)
        if not goal:
            return []
        
        return self.db.query(GoalContribution).filter(
            GoalContribution.goal_id == goal_id
        ).order_by(desc(GoalContribution.contribution_date)).limit(limit).all()
    
    # Milestone Management
    def create_milestone(self, goal_id: int, user_id: int, milestone_data: Dict[str, Any]) -> GoalMilestone:
        """Create a milestone for a goal"""
        try:
            goal = self.get_goal(goal_id, user_id)
            if not goal:
                raise ValueError("Goal not found")
            
            milestone = GoalMilestone(
                goal_id=goal_id,
                name=milestone_data["name"],
                description=milestone_data.get("description"),
                target_amount=milestone_data["target_amount"],
                target_date=milestone_data["target_date"]
            )
            
            self.db.add(milestone)
            self.db.commit()
            self.db.refresh(milestone)
            
            logger.info(f"Created milestone {milestone.id} for goal {goal_id}")
            return milestone
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create milestone: {str(e)}")
            raise
    
    def get_goal_milestones(self, goal_id: int, user_id: int) -> List[GoalMilestone]:
        """Get milestones for a goal"""
        goal = self.get_goal(goal_id, user_id)
        if not goal:
            return []
        
        return self.db.query(GoalMilestone).filter(
            GoalMilestone.goal_id == goal_id
        ).order_by(GoalMilestone.target_date).all()

    # AI-Powered Goal Analysis
    def analyze_goal_with_ai(self, goal_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze goal using AI agents"""
        try:
            goal = self.get_goal(goal_id, user_id)
            if not goal:
                raise ValueError("Goal not found")

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

            # Prepare goal data
            goal_data = {
                "id": goal.id,
                "name": goal.name,
                "goal_type": goal.goal_type.value,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "target_date": goal.target_date.isoformat(),
                "monthly_contribution": goal.monthly_contribution,
                "expected_return_rate": goal.expected_return_rate,
                "inflation_rate": goal.inflation_rate,
                "progress_percentage": goal.progress_percentage,
                "is_on_track": goal.is_on_track
            }

            # Use AI crew for analysis
            analysis_request = {
                "request_id": f"goal_analysis_{goal_id}_{user_id}",
                "goal_data": goal_data,
                "user_profile": user_profile
            }

            # For now, return a structured analysis (would integrate with AI crew)
            ai_analysis = {
                "goal_feasibility": self._analyze_goal_feasibility(goal, user),
                "optimization_suggestions": self._get_optimization_suggestions(goal, user),
                "risk_assessment": self._assess_goal_risk(goal, user),
                "timeline_analysis": self._analyze_timeline(goal),
                "investment_strategy": self._suggest_investment_strategy(goal, user)
            }

            return ai_analysis

        except Exception as e:
            logger.error(f"Failed to analyze goal with AI: {str(e)}")
            raise

    def get_goal_recommendations(self, goal_id: int, user_id: int) -> List[GoalRecommendation]:
        """Get AI-generated recommendations for a goal"""
        return self.db.query(GoalRecommendation).filter(
            and_(
                GoalRecommendation.goal_id == goal_id,
                GoalRecommendation.user_id == user_id,
                GoalRecommendation.is_dismissed == False
            )
        ).order_by(desc(GoalRecommendation.confidence_score)).all()

    def get_user_goal_overview(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive overview of user's goals"""
        try:
            goals = self.get_user_goals(user_id)

            overview = {
                "user_id": user_id,
                "total_goals": len(goals),
                "active_goals": len([g for g in goals if g.status == GoalStatus.ACTIVE]),
                "completed_goals": len([g for g in goals if g.status == GoalStatus.COMPLETED]),
                "total_target_amount": sum(g.target_amount for g in goals if g.status == GoalStatus.ACTIVE),
                "total_current_amount": sum(g.current_amount for g in goals if g.status == GoalStatus.ACTIVE),
                "total_monthly_contribution": sum(g.monthly_contribution for g in goals if g.status == GoalStatus.ACTIVE),
                "goals_on_track": len([g for g in goals if g.status == GoalStatus.ACTIVE and g.is_on_track]),
                "goals_off_track": len([g for g in goals if g.status == GoalStatus.ACTIVE and not g.is_on_track]),
                "goal_breakdown": {},
                "priority_breakdown": {},
                "upcoming_milestones": []
            }

            # Calculate overall progress
            if overview["total_target_amount"] > 0:
                overview["overall_progress_percentage"] = (overview["total_current_amount"] / overview["total_target_amount"]) * 100
            else:
                overview["overall_progress_percentage"] = 0

            # Goal type breakdown
            goal_types = {}
            for goal in goals:
                if goal.status == GoalStatus.ACTIVE:
                    goal_type = goal.goal_type.value
                    if goal_type not in goal_types:
                        goal_types[goal_type] = {"count": 0, "target_amount": 0, "current_amount": 0}
                    goal_types[goal_type]["count"] += 1
                    goal_types[goal_type]["target_amount"] += goal.target_amount
                    goal_types[goal_type]["current_amount"] += goal.current_amount

            overview["goal_breakdown"] = goal_types

            # Priority breakdown
            priority_breakdown = {}
            for goal in goals:
                if goal.status == GoalStatus.ACTIVE:
                    priority = goal.priority.value
                    if priority not in priority_breakdown:
                        priority_breakdown[priority] = 0
                    priority_breakdown[priority] += 1

            overview["priority_breakdown"] = priority_breakdown

            # Upcoming milestones
            upcoming_milestones = []
            for goal in goals:
                if goal.status == GoalStatus.ACTIVE:
                    milestones = self.get_goal_milestones(goal.id, user_id)
                    for milestone in milestones:
                        if not milestone.is_completed and milestone.target_date >= datetime.now():
                            upcoming_milestones.append({
                                "goal_name": goal.name,
                                "milestone_name": milestone.name,
                                "target_amount": milestone.target_amount,
                                "target_date": milestone.target_date.isoformat(),
                                "days_remaining": (milestone.target_date.date() - date.today()).days
                            })

            # Sort by date and take top 5
            upcoming_milestones.sort(key=lambda x: x["days_remaining"])
            overview["upcoming_milestones"] = upcoming_milestones[:5]

            return overview

        except Exception as e:
            logger.error(f"Failed to get goal overview: {str(e)}")
            raise

    # Goal Templates
    def get_goal_templates(self, goal_type: Optional[GoalType] = None) -> List[GoalTemplate]:
        """Get available goal templates"""
        query = self.db.query(GoalTemplate).filter(GoalTemplate.is_active == True)

        if goal_type:
            query = query.filter(GoalTemplate.goal_type == goal_type)

        return query.order_by(desc(GoalTemplate.usage_count)).all()

    def create_goal_from_template(self, user_id: int, template_id: int, customizations: Dict[str, Any]) -> FinancialGoal:
        """Create a goal from a template"""
        try:
            template = self.db.query(GoalTemplate).filter(GoalTemplate.id == template_id).first()
            if not template:
                raise ValueError("Template not found")

            # Merge template defaults with customizations
            goal_data = {
                "name": customizations.get("name", template.name),
                "description": customizations.get("description", template.description),
                "goal_type": template.goal_type.value,
                "target_amount": customizations["target_amount"],
                "target_date": customizations["target_date"],
                "inflation_rate": customizations.get("inflation_rate", template.default_inflation_rate),
                "expected_return_rate": customizations.get("expected_return_rate", template.default_expected_return),
                "risk_level": customizations.get("risk_level", template.recommended_risk_level),
                "priority": customizations.get("priority", "medium")
            }

            goal = self.create_goal(user_id, goal_data)

            # Update template usage count
            template.usage_count += 1
            self.db.commit()

            return goal

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create goal from template: {str(e)}")
            raise

    # Helper Methods
    def _calculate_goal_metrics(self, goal: FinancialGoal):
        """Calculate and update goal metrics"""
        try:
            # Calculate months remaining
            if goal.target_date:
                days_remaining = (goal.target_date.date() - date.today()).days
                goal.months_remaining = max(0, int(days_remaining / 30.44))

            # Calculate required monthly amount
            goal.required_monthly_amount = goal.calculate_required_monthly_amount()

            # Calculate completion percentage
            goal.completion_percentage = goal.progress_percentage

        except Exception as e:
            logger.error(f"Failed to calculate goal metrics: {str(e)}")

    def _create_default_milestones(self, goal: FinancialGoal):
        """Create default milestones for a goal"""
        try:
            if goal.goal_type == GoalType.RETIREMENT:
                # Create milestones at 25%, 50%, 75% of target
                milestones = [
                    {"name": "Quarter Progress", "percentage": 25},
                    {"name": "Halfway There", "percentage": 50},
                    {"name": "Three-Quarter Mark", "percentage": 75}
                ]
            elif goal.goal_type == GoalType.EDUCATION:
                # Create milestones based on education timeline
                milestones = [
                    {"name": "Initial Fund", "percentage": 30},
                    {"name": "Mid-term Goal", "percentage": 70}
                ]
            else:
                # Generic milestones
                milestones = [
                    {"name": "First Milestone", "percentage": 33},
                    {"name": "Second Milestone", "percentage": 67}
                ]

            for milestone_data in milestones:
                # Calculate milestone date (proportional to target date)
                total_days = (goal.target_date.date() - goal.start_date.date()).days
                milestone_days = int(total_days * milestone_data["percentage"] / 100)
                milestone_date = goal.start_date + timedelta(days=milestone_days)

                milestone = GoalMilestone(
                    goal_id=goal.id,
                    name=milestone_data["name"],
                    description=f"Reach {milestone_data['percentage']}% of your goal",
                    target_amount=goal.target_amount * milestone_data["percentage"] / 100,
                    target_date=milestone_date
                )

                self.db.add(milestone)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to create default milestones: {str(e)}")

    def _generate_goal_recommendations(self, goal: FinancialGoal):
        """Generate AI-powered recommendations for a goal"""
        try:
            recommendations = []

            # Check if goal is on track
            if not goal.is_on_track:
                recommendations.append({
                    "type": "increase_contribution",
                    "title": "Increase Monthly Contribution",
                    "description": f"Your goal is off track. Consider increasing monthly contribution to ₹{goal.calculate_sip_amount():.0f}",
                    "confidence": 85
                })

            # Check if timeline is too aggressive
            required_monthly = goal.calculate_sip_amount()
            if required_monthly > goal.monthly_contribution * 2:
                recommendations.append({
                    "type": "extend_timeline",
                    "title": "Consider Extending Timeline",
                    "description": "Your current timeline may be too aggressive. Consider extending the target date.",
                    "confidence": 75
                })

            # Save recommendations to database
            for rec_data in recommendations:
                recommendation = GoalRecommendation(
                    user_id=goal.user_id,
                    goal_id=goal.id,
                    recommendation_type=rec_data["type"],
                    title=rec_data["title"],
                    description=rec_data["description"],
                    confidence_score=rec_data["confidence"],
                    recommendation_data=json.dumps(rec_data)
                )
                self.db.add(recommendation)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")

    def _check_milestone_completion(self, goal: FinancialGoal):
        """Check and mark completed milestones"""
        try:
            milestones = self.get_goal_milestones(goal.id, goal.user_id)

            for milestone in milestones:
                if not milestone.is_completed and goal.current_amount >= milestone.target_amount:
                    milestone.is_completed = True
                    milestone.completed_at = datetime.now()

                    # Create milestone completion alert
                    alert = GoalAlert(
                        user_id=goal.user_id,
                        goal_id=goal.id,
                        alert_type="milestone_reached",
                        title=f"Milestone Achieved: {milestone.name}",
                        message=f"Congratulations! You've reached the '{milestone.name}' milestone for your {goal.name} goal.",
                        severity="info"
                    )
                    self.db.add(alert)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to check milestone completion: {str(e)}")

    def _check_goal_alerts(self, goal: FinancialGoal):
        """Check and generate goal-related alerts"""
        try:
            alerts = []

            # Check if goal is completed
            if goal.current_amount >= goal.target_amount and goal.status != GoalStatus.COMPLETED:
                alerts.append({
                    "type": "goal_completed",
                    "title": f"Goal Completed: {goal.name}",
                    "message": f"Congratulations! You've successfully achieved your {goal.name} goal.",
                    "severity": "info"
                })

            # Check if goal is significantly off track
            elif not goal.is_on_track and goal.progress_percentage < 50:
                alerts.append({
                    "type": "goal_off_track",
                    "title": f"Goal Off Track: {goal.name}",
                    "message": f"Your {goal.name} goal is falling behind schedule. Consider reviewing your strategy.",
                    "severity": "warning"
                })

            # Save alerts
            for alert_data in alerts:
                alert = GoalAlert(
                    user_id=goal.user_id,
                    goal_id=goal.id,
                    alert_type=alert_data["type"],
                    title=alert_data["title"],
                    message=alert_data["message"],
                    severity=alert_data["severity"]
                )
                self.db.add(alert)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to check goal alerts: {str(e)}")

    # AI Analysis Helper Methods
    def _analyze_goal_feasibility(self, goal: FinancialGoal, user: User) -> Dict[str, Any]:
        """Analyze if goal is feasible given user's financial situation"""
        try:
            # Calculate affordability
            monthly_income = user.annual_income / 12 if user.annual_income else 0
            monthly_expenses = user.monthly_expenses or 0
            available_income = monthly_income - monthly_expenses

            required_monthly = goal.calculate_sip_amount()
            affordability_ratio = (required_monthly / available_income * 100) if available_income > 0 else 100

            # Determine feasibility
            if affordability_ratio <= 20:
                feasibility = "Highly Feasible"
                feasibility_score = 90
            elif affordability_ratio <= 40:
                feasibility = "Feasible"
                feasibility_score = 70
            elif affordability_ratio <= 60:
                feasibility = "Challenging"
                feasibility_score = 50
            else:
                feasibility = "Difficult"
                feasibility_score = 30

            return {
                "feasibility": feasibility,
                "feasibility_score": feasibility_score,
                "affordability_ratio": affordability_ratio,
                "required_monthly": required_monthly,
                "available_income": available_income,
                "recommendations": self._get_feasibility_recommendations(affordability_ratio)
            }

        except Exception as e:
            logger.error(f"Failed to analyze goal feasibility: {str(e)}")
            return {"feasibility": "Unknown", "feasibility_score": 0}

    def _get_optimization_suggestions(self, goal: FinancialGoal, user: User) -> List[Dict[str, Any]]:
        """Get optimization suggestions for the goal"""
        suggestions = []

        try:
            # Timeline optimization
            if goal.months_remaining and goal.months_remaining < 12:
                suggestions.append({
                    "type": "timeline",
                    "suggestion": "Consider extending timeline for better affordability",
                    "impact": "Reduce monthly contribution requirement",
                    "priority": "high"
                })

            # Contribution optimization
            current_sip = goal.calculate_sip_amount()
            if goal.monthly_contribution < current_sip:
                suggestions.append({
                    "type": "contribution",
                    "suggestion": f"Increase monthly contribution to ₹{current_sip:.0f}",
                    "impact": "Stay on track to meet goal",
                    "priority": "high"
                })

            # Return optimization
            if goal.expected_return_rate < 15:
                suggestions.append({
                    "type": "returns",
                    "suggestion": "Consider equity-heavy portfolio for higher returns",
                    "impact": "Potentially reduce required contributions",
                    "priority": "medium"
                })

            return suggestions

        except Exception as e:
            logger.error(f"Failed to get optimization suggestions: {str(e)}")
            return []

    def _assess_goal_risk(self, goal: FinancialGoal, user: User) -> Dict[str, Any]:
        """Assess risk factors for the goal"""
        try:
            risk_factors = []
            risk_score = 0

            # Timeline risk
            if goal.months_remaining and goal.months_remaining < 24:
                risk_factors.append("Short timeline increases volatility risk")
                risk_score += 20

            # Contribution risk
            monthly_income = user.annual_income / 12 if user.annual_income else 0
            if goal.monthly_contribution > monthly_income * 0.3:
                risk_factors.append("High contribution relative to income")
                risk_score += 25

            # Market risk
            if goal.expected_return_rate > 15:
                risk_factors.append("High return expectations increase market risk")
                risk_score += 15

            # Inflation risk
            if goal.goal_type in [GoalType.EDUCATION, GoalType.HOME_PURCHASE]:
                risk_factors.append("High inflation risk for this goal type")
                risk_score += 10

            # Determine risk level
            if risk_score <= 20:
                risk_level = "Low"
            elif risk_score <= 40:
                risk_level = "Moderate"
            elif risk_score <= 60:
                risk_level = "High"
            else:
                risk_level = "Very High"

            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "mitigation_strategies": self._get_risk_mitigation_strategies(risk_factors)
            }

        except Exception as e:
            logger.error(f"Failed to assess goal risk: {str(e)}")
            return {"risk_level": "Unknown", "risk_score": 0}

    def _analyze_timeline(self, goal: FinancialGoal) -> Dict[str, Any]:
        """Analyze goal timeline"""
        try:
            timeline_analysis = {
                "months_remaining": goal.months_remaining,
                "is_realistic": True,
                "timeline_pressure": "Normal",
                "recommendations": []
            }

            if goal.months_remaining:
                if goal.months_remaining < 12:
                    timeline_analysis["timeline_pressure"] = "High"
                    timeline_analysis["is_realistic"] = False
                    timeline_analysis["recommendations"].append("Consider extending timeline")
                elif goal.months_remaining < 24:
                    timeline_analysis["timeline_pressure"] = "Moderate"
                    timeline_analysis["recommendations"].append("Monitor progress closely")

                # Check if current progress aligns with timeline
                elapsed_months = (datetime.now().date() - goal.start_date.date()).days / 30.44
                if elapsed_months > 0:
                    expected_progress = (elapsed_months / (goal.months_remaining + elapsed_months)) * 100
                    actual_progress = goal.progress_percentage

                    if actual_progress < expected_progress - 15:
                        timeline_analysis["recommendations"].append("Increase contributions or extend timeline")

            return timeline_analysis

        except Exception as e:
            logger.error(f"Failed to analyze timeline: {str(e)}")
            return {"months_remaining": 0, "is_realistic": False}

    def _suggest_investment_strategy(self, goal: FinancialGoal, user: User) -> Dict[str, Any]:
        """Suggest investment strategy based on goal and user profile"""
        try:
            strategy = {
                "recommended_allocation": {},
                "investment_products": [],
                "rebalancing_frequency": "Quarterly",
                "risk_considerations": []
            }

            # Determine allocation based on timeline and risk profile
            if goal.months_remaining:
                if goal.months_remaining > 60:  # > 5 years
                    strategy["recommended_allocation"] = {
                        "equity": 70,
                        "debt": 25,
                        "cash": 5
                    }
                    strategy["investment_products"] = ["Equity Mutual Funds", "ELSS", "Index Funds"]
                elif goal.months_remaining > 24:  # 2-5 years
                    strategy["recommended_allocation"] = {
                        "equity": 50,
                        "debt": 45,
                        "cash": 5
                    }
                    strategy["investment_products"] = ["Hybrid Funds", "Debt Funds", "Some Equity"]
                else:  # < 2 years
                    strategy["recommended_allocation"] = {
                        "equity": 20,
                        "debt": 70,
                        "cash": 10
                    }
                    strategy["investment_products"] = ["Debt Funds", "FDs", "Liquid Funds"]

            # Adjust based on goal type
            if goal.goal_type == GoalType.EMERGENCY_FUND:
                strategy["recommended_allocation"] = {"debt": 80, "cash": 20}
                strategy["investment_products"] = ["Liquid Funds", "Savings Account", "Short-term FDs"]
            elif goal.goal_type == GoalType.RETIREMENT:
                strategy["recommended_allocation"] = {"equity": 80, "debt": 20}
                strategy["investment_products"] = ["ELSS", "PPF", "NPS", "Equity Mutual Funds"]

            return strategy

        except Exception as e:
            logger.error(f"Failed to suggest investment strategy: {str(e)}")
            return {"recommended_allocation": {}, "investment_products": []}

    def _get_feasibility_recommendations(self, affordability_ratio: float) -> List[str]:
        """Get recommendations based on affordability ratio"""
        recommendations = []

        if affordability_ratio > 60:
            recommendations.extend([
                "Consider extending the goal timeline",
                "Look for additional income sources",
                "Review and optimize monthly expenses",
                "Consider a lower target amount initially"
            ])
        elif affordability_ratio > 40:
            recommendations.extend([
                "Monitor monthly budget closely",
                "Consider step-up SIP to gradually increase contributions",
                "Look for tax-saving investment options"
            ])
        else:
            recommendations.extend([
                "Goal appears financially feasible",
                "Consider increasing contributions if possible",
                "Set up automatic investments for consistency"
            ])

        return recommendations

    def _get_risk_mitigation_strategies(self, risk_factors: List[str]) -> List[str]:
        """Get risk mitigation strategies"""
        strategies = []

        for factor in risk_factors:
            if "timeline" in factor.lower():
                strategies.append("Consider systematic transfer plans (STP) to reduce volatility")
            elif "contribution" in factor.lower():
                strategies.append("Build emergency fund first to ensure consistent contributions")
            elif "return" in factor.lower():
                strategies.append("Diversify across asset classes and review expectations")
            elif "inflation" in factor.lower():
                strategies.append("Include inflation-beating assets like equity in portfolio")

        # Add general strategies
        strategies.extend([
            "Regular portfolio review and rebalancing",
            "Maintain adequate insurance coverage",
            "Keep some buffer in target amount for contingencies"
        ])

        return list(set(strategies))  # Remove duplicates
