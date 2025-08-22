"""
Goal Dashboard Service - Comprehensive goal planning dashboard and analytics
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta, date
import json
import logging

from app.models.goals import FinancialGoal, GoalMilestone, GoalContribution, GoalType, GoalStatus
from app.models.user import User
from app.services.goal_service import GoalPlanningService

logger = logging.getLogger(__name__)


class GoalDashboardService:
    """Service for goal planning dashboard and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.goal_service = GoalPlanningService(db)
    
    def get_goal_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive goal planning dashboard"""
        try:
            dashboard_data = {
                "user_id": user_id,
                "dashboard_type": "goal_planning",
                "generated_at": datetime.now().isoformat(),
                "goal_overview": {},
                "progress_summary": {},
                "upcoming_milestones": [],
                "contribution_analysis": {},
                "goal_performance": {},
                "recommendations": [],
                "alerts": []
            }
            
            # Goal Overview
            dashboard_data["goal_overview"] = self._get_goal_overview(user_id)
            
            # Progress Summary
            dashboard_data["progress_summary"] = self._get_progress_summary(user_id)
            
            # Upcoming Milestones
            dashboard_data["upcoming_milestones"] = self._get_upcoming_milestones(user_id)
            
            # Contribution Analysis
            dashboard_data["contribution_analysis"] = self._get_contribution_analysis(user_id)
            
            # Goal Performance
            dashboard_data["goal_performance"] = self._get_goal_performance(user_id)
            
            # Recommendations
            dashboard_data["recommendations"] = self._get_dashboard_recommendations(user_id)
            
            # Alerts
            dashboard_data["alerts"] = self._get_goal_alerts(user_id)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate goal dashboard: {str(e)}")
            raise
    
    def get_goal_analytics(self, user_id: int, goal_id: Optional[int] = None) -> Dict[str, Any]:
        """Get detailed goal analytics"""
        try:
            analytics_data = {
                "user_id": user_id,
                "goal_id": goal_id,
                "analytics_type": "detailed_goal",
                "generated_at": datetime.now().isoformat(),
                "goal_feasibility": {},
                "timeline_analysis": {},
                "contribution_patterns": {},
                "milestone_tracking": {},
                "risk_assessment": {},
                "optimization_opportunities": {}
            }
            
            if goal_id:
                # Single goal analysis
                goal = self.goal_service.get_goal(goal_id, user_id)
                if not goal:
                    return {"error": "Goal not found"}
                
                analytics_data["goal_feasibility"] = self._analyze_single_goal_feasibility(goal)
                analytics_data["timeline_analysis"] = self._analyze_single_goal_timeline(goal)
                analytics_data["contribution_patterns"] = self._analyze_single_goal_contributions(goal)
                analytics_data["milestone_tracking"] = self._analyze_single_goal_milestones(goal)
                analytics_data["risk_assessment"] = self._assess_single_goal_risk(goal)
                analytics_data["optimization_opportunities"] = self._find_single_goal_optimizations(goal)
            else:
                # All goals analysis
                goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
                analytics_data["goal_feasibility"] = self._analyze_all_goals_feasibility(goals)
                analytics_data["timeline_analysis"] = self._analyze_all_goals_timeline(goals)
                analytics_data["contribution_patterns"] = self._analyze_all_goals_contributions(goals)
                analytics_data["milestone_tracking"] = self._analyze_all_goals_milestones(goals)
                analytics_data["risk_assessment"] = self._assess_all_goals_risk(goals)
                analytics_data["optimization_opportunities"] = self._find_all_goals_optimizations(goals)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to generate goal analytics: {str(e)}")
            raise
    
    def get_goal_insights(self, user_id: int) -> Dict[str, Any]:
        """Get AI-powered goal insights"""
        try:
            insights_data = {
                "user_id": user_id,
                "insights_type": "goal_planning",
                "generated_at": datetime.now().isoformat(),
                "goal_health_score": 0,
                "key_insights": [],
                "action_items": [],
                "success_factors": [],
                "risk_factors": [],
                "optimization_suggestions": []
            }
            
            goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
            
            # Calculate goal health score
            insights_data["goal_health_score"] = self._calculate_goal_health_score(goals)
            
            # Generate key insights
            insights_data["key_insights"] = self._generate_key_insights(goals)
            
            # Generate action items
            insights_data["action_items"] = self._generate_action_items(goals)
            
            # Identify success factors
            insights_data["success_factors"] = self._identify_success_factors(goals)
            
            # Identify risk factors
            insights_data["risk_factors"] = self._identify_risk_factors(goals)
            
            # Generate optimization suggestions
            insights_data["optimization_suggestions"] = self._generate_optimization_suggestions(goals)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Failed to generate goal insights: {str(e)}")
            raise
    
    # Helper methods for dashboard components
    def _get_goal_overview(self, user_id: int) -> Dict[str, Any]:
        """Get goal overview for dashboard"""
        try:
            overview = self.goal_service.get_user_goal_overview(user_id)
            
            # Add additional metrics
            goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
            
            # Calculate average progress
            if goals:
                avg_progress = sum(goal.progress_percentage for goal in goals) / len(goals)
                on_track_percentage = (len([g for g in goals if g.is_on_track]) / len(goals)) * 100
            else:
                avg_progress = 0
                on_track_percentage = 0
            
            # Find most urgent goal
            urgent_goals = sorted(goals, key=lambda g: g.months_remaining or 999)
            most_urgent = urgent_goals[0] if urgent_goals else None
            
            # Find highest priority goal
            priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            priority_goals = sorted(goals, key=lambda g: priority_order.get(g.priority.value, 0), reverse=True)
            highest_priority = priority_goals[0] if priority_goals else None
            
            overview.update({
                "average_progress": avg_progress,
                "on_track_percentage": on_track_percentage,
                "most_urgent_goal": {
                    "name": most_urgent.name,
                    "months_remaining": most_urgent.months_remaining,
                    "progress_percentage": most_urgent.progress_percentage
                } if most_urgent else None,
                "highest_priority_goal": {
                    "name": highest_priority.name,
                    "priority": highest_priority.priority.value,
                    "progress_percentage": highest_priority.progress_percentage
                } if highest_priority else None
            })
            
            return overview
            
        except Exception as e:
            logger.error(f"Failed to get goal overview: {str(e)}")
            return {}
    
    def _get_progress_summary(self, user_id: int) -> Dict[str, Any]:
        """Get progress summary"""
        try:
            goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
            
            # Calculate progress metrics
            total_target = sum(goal.target_amount for goal in goals)
            total_current = sum(goal.current_amount for goal in goals)
            total_monthly = sum(goal.monthly_contribution for goal in goals)
            
            # Progress by goal type
            progress_by_type = {}
            for goal in goals:
                goal_type = goal.goal_type.value
                if goal_type not in progress_by_type:
                    progress_by_type[goal_type] = {
                        "count": 0,
                        "target_amount": 0,
                        "current_amount": 0,
                        "progress_percentage": 0
                    }
                
                progress_by_type[goal_type]["count"] += 1
                progress_by_type[goal_type]["target_amount"] += goal.target_amount
                progress_by_type[goal_type]["current_amount"] += goal.current_amount
            
            # Calculate progress percentages
            for goal_type in progress_by_type:
                data = progress_by_type[goal_type]
                if data["target_amount"] > 0:
                    data["progress_percentage"] = (data["current_amount"] / data["target_amount"]) * 100
            
            # Recent contributions (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_contributions = self.db.query(GoalContribution).join(FinancialGoal).filter(
                and_(
                    FinancialGoal.user_id == user_id,
                    GoalContribution.contribution_date >= thirty_days_ago
                )
            ).all()
            
            recent_contribution_amount = sum(c.amount for c in recent_contributions)
            
            return {
                "total_target_amount": total_target,
                "total_current_amount": total_current,
                "total_monthly_contribution": total_monthly,
                "overall_progress_percentage": (total_current / total_target * 100) if total_target > 0 else 0,
                "progress_by_type": progress_by_type,
                "recent_contributions": {
                    "amount": recent_contribution_amount,
                    "count": len(recent_contributions),
                    "period_days": 30
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get progress summary: {str(e)}")
            return {}
    
    def _get_upcoming_milestones(self, user_id: int) -> List[Dict[str, Any]]:
        """Get upcoming milestones"""
        try:
            # Get all active goals
            goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
            
            upcoming_milestones = []
            for goal in goals:
                milestones = self.goal_service.get_goal_milestones(goal.id, user_id)
                for milestone in milestones:
                    if not milestone.is_completed and milestone.target_date >= datetime.now():
                        days_remaining = (milestone.target_date.date() - date.today()).days
                        upcoming_milestones.append({
                            "goal_id": goal.id,
                            "goal_name": goal.name,
                            "milestone_id": milestone.id,
                            "milestone_name": milestone.name,
                            "target_amount": milestone.target_amount,
                            "target_date": milestone.target_date.isoformat(),
                            "days_remaining": days_remaining,
                            "urgency": "high" if days_remaining <= 30 else "medium" if days_remaining <= 90 else "low"
                        })
            
            # Sort by urgency and date
            upcoming_milestones.sort(key=lambda x: (x["days_remaining"], x["target_date"]))
            
            return upcoming_milestones[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Failed to get upcoming milestones: {str(e)}")
            return []
    
    def _get_contribution_analysis(self, user_id: int) -> Dict[str, Any]:
        """Get contribution analysis"""
        try:
            # Get contributions for last 12 months
            twelve_months_ago = datetime.now() - timedelta(days=365)
            contributions = self.db.query(GoalContribution).join(FinancialGoal).filter(
                and_(
                    FinancialGoal.user_id == user_id,
                    GoalContribution.contribution_date >= twelve_months_ago
                )
            ).order_by(GoalContribution.contribution_date).all()
            
            # Monthly contribution analysis
            monthly_contributions = {}
            for contribution in contributions:
                month_key = contribution.contribution_date.strftime('%Y-%m')
                if month_key not in monthly_contributions:
                    monthly_contributions[month_key] = 0
                monthly_contributions[month_key] += contribution.amount
            
            # Calculate trends
            monthly_amounts = list(monthly_contributions.values())
            if len(monthly_amounts) >= 2:
                recent_avg = sum(monthly_amounts[-3:]) / min(3, len(monthly_amounts))
                earlier_avg = sum(monthly_amounts[:-3]) / max(1, len(monthly_amounts) - 3)
                trend = "increasing" if recent_avg > earlier_avg else "decreasing" if recent_avg < earlier_avg else "stable"
            else:
                trend = "insufficient_data"
            
            # Contribution consistency
            expected_monthly = sum(goal.monthly_contribution for goal in self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE))
            actual_avg_monthly = sum(monthly_amounts) / max(1, len(monthly_amounts)) if monthly_amounts else 0
            consistency_score = min(100, (actual_avg_monthly / expected_monthly * 100)) if expected_monthly > 0 else 0
            
            return {
                "total_contributions_12m": sum(c.amount for c in contributions),
                "contribution_count_12m": len(contributions),
                "monthly_contributions": monthly_contributions,
                "average_monthly_contribution": actual_avg_monthly,
                "expected_monthly_contribution": expected_monthly,
                "consistency_score": consistency_score,
                "trend": trend,
                "contribution_frequency": self._analyze_contribution_frequency(contributions)
            }
            
        except Exception as e:
            logger.error(f"Failed to get contribution analysis: {str(e)}")
            return {}
    
    def _get_goal_performance(self, user_id: int) -> Dict[str, Any]:
        """Get goal performance metrics"""
        try:
            goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
            
            performance_metrics = {
                "best_performing_goals": [],
                "underperforming_goals": [],
                "on_track_goals": [],
                "off_track_goals": [],
                "completion_forecast": {}
            }
            
            # Categorize goals by performance
            for goal in goals:
                goal_data = {
                    "id": goal.id,
                    "name": goal.name,
                    "progress_percentage": goal.progress_percentage,
                    "is_on_track": goal.is_on_track,
                    "months_remaining": goal.months_remaining
                }
                
                if goal.progress_percentage >= 75:
                    performance_metrics["best_performing_goals"].append(goal_data)
                elif goal.progress_percentage < 25 and goal.months_remaining and goal.months_remaining < 24:
                    performance_metrics["underperforming_goals"].append(goal_data)
                
                if goal.is_on_track:
                    performance_metrics["on_track_goals"].append(goal_data)
                else:
                    performance_metrics["off_track_goals"].append(goal_data)
            
            # Sort by progress
            performance_metrics["best_performing_goals"].sort(key=lambda x: x["progress_percentage"], reverse=True)
            performance_metrics["underperforming_goals"].sort(key=lambda x: x["progress_percentage"])
            
            # Completion forecast
            completion_forecast = {}
            for goal in goals:
                if goal.monthly_contribution > 0 and goal.target_amount > goal.current_amount:
                    remaining_amount = goal.target_amount - goal.current_amount
                    months_to_complete = remaining_amount / goal.monthly_contribution
                    completion_forecast[goal.name] = {
                        "estimated_months": int(months_to_complete),
                        "estimated_completion_date": (datetime.now() + timedelta(days=months_to_complete * 30.44)).strftime('%Y-%m-%d')
                    }
            
            performance_metrics["completion_forecast"] = completion_forecast
            
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Failed to get goal performance: {str(e)}")
            return {}
    
    def _get_dashboard_recommendations(self, user_id: int) -> List[str]:
        """Get dashboard recommendations"""
        try:
            recommendations = []
            goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
            
            if not goals:
                recommendations.append("Start by creating your first financial goal")
                return recommendations
            
            # Check for off-track goals
            off_track_goals = [g for g in goals if not g.is_on_track]
            if off_track_goals:
                recommendations.append(f"Review {len(off_track_goals)} goals that are off track")
            
            # Check for low progress goals
            low_progress_goals = [g for g in goals if g.progress_percentage < 20 and g.months_remaining and g.months_remaining < 24]
            if low_progress_goals:
                recommendations.append(f"Increase contributions for {len(low_progress_goals)} urgent goals")
            
            # Check for missing emergency fund
            has_emergency_fund = any(g.goal_type == GoalType.EMERGENCY_FUND for g in goals)
            if not has_emergency_fund:
                recommendations.append("Consider creating an emergency fund goal")
            
            # Check for retirement planning
            has_retirement_goal = any(g.goal_type == GoalType.RETIREMENT for g in goals)
            if not has_retirement_goal:
                recommendations.append("Start planning for retirement with a dedicated goal")
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to get dashboard recommendations: {str(e)}")
            return []
    
    def _get_goal_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get goal-related alerts"""
        try:
            # This would typically query the GoalAlert table
            # For now, generate alerts based on goal status
            alerts = []
            goals = self.goal_service.get_user_goals(user_id, GoalStatus.ACTIVE)
            
            for goal in goals:
                # Check for urgent milestones
                milestones = self.goal_service.get_goal_milestones(goal.id, user_id)
                for milestone in milestones:
                    if not milestone.is_completed and milestone.target_date:
                        days_remaining = (milestone.target_date.date() - date.today()).days
                        if days_remaining <= 7:
                            alerts.append({
                                "type": "milestone_due",
                                "severity": "high",
                                "message": f"Milestone '{milestone.name}' for {goal.name} is due in {days_remaining} days",
                                "goal_id": goal.id,
                                "milestone_id": milestone.id
                            })
                
                # Check for goals significantly off track
                if not goal.is_on_track and goal.progress_percentage < 30:
                    alerts.append({
                        "type": "goal_off_track",
                        "severity": "medium",
                        "message": f"Goal '{goal.name}' is significantly behind schedule",
                        "goal_id": goal.id
                    })
            
            return alerts[:10]  # Limit to 10 alerts
            
        except Exception as e:
            logger.error(f"Failed to get goal alerts: {str(e)}")
            return []
