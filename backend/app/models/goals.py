"""
Financial goals model for InvestAI application
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
import enum

from app.core.database import Base


class GoalType(str, enum.Enum):
    """Financial goal types"""
    RETIREMENT = "retirement"
    EDUCATION = "education"
    HOME_PURCHASE = "home_purchase"
    EMERGENCY_FUND = "emergency_fund"
    VACATION = "vacation"
    WEDDING = "wedding"
    VEHICLE = "vehicle"
    BUSINESS = "business"
    DEBT_PAYOFF = "debt_payoff"
    OTHER = "other"


class GoalStatus(str, enum.Enum):
    """Goal status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class GoalPriority(str, enum.Enum):
    """Goal priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FinancialGoal(Base):
    """Financial goal model"""
    __tablename__ = "financial_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Goal details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    goal_type = Column(Enum(GoalType), nullable=False)
    priority = Column(Enum(GoalPriority), default=GoalPriority.MEDIUM)
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    
    # Financial details
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    monthly_contribution = Column(Float, default=0.0)
    
    # Timeline
    target_date = Column(DateTime(timezone=True), nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Calculated fields
    months_remaining = Column(Integer)
    required_monthly_amount = Column(Float)
    completion_percentage = Column(Float, default=0.0)
    
    # Investment strategy
    risk_level = Column(String(20))  # conservative, moderate, aggressive
    recommended_allocation = Column(Text)  # JSON string of asset allocation
    
    # Inflation and growth assumptions
    inflation_rate = Column(Float, default=6.0)  # Default Indian inflation rate
    expected_return_rate = Column(Float, default=12.0)  # Expected annual return
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="goals")
    milestones = relationship("GoalMilestone", back_populates="goal", cascade="all, delete-orphan")
    contributions = relationship("GoalContribution", back_populates="goal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FinancialGoal(id={self.id}, name='{self.name}', target_amount={self.target_amount})>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate goal completion percentage"""
        if self.target_amount <= 0:
            return 0.0
        return min((self.current_amount / self.target_amount) * 100, 100.0)
    
    @property
    def is_on_track(self) -> bool:
        """Check if goal is on track based on timeline and current progress"""
        if not self.target_date:
            return False
        
        total_months = (self.target_date.date() - self.start_date.date()).days / 30.44
        elapsed_months = (date.today() - self.start_date.date()).days / 30.44
        
        if total_months <= 0:
            return self.current_amount >= self.target_amount
        
        expected_progress = (elapsed_months / total_months) * 100
        actual_progress = self.progress_percentage
        
        # Allow 10% deviation
        return actual_progress >= (expected_progress - 10)
    
    def calculate_required_monthly_amount(self) -> float:
        """Calculate required monthly contribution to meet goal"""
        if not self.target_date:
            return 0.0
        
        remaining_amount = max(0, self.target_amount - self.current_amount)
        months_left = max(1, (self.target_date.date() - date.today()).days / 30.44)
        
        # Simple calculation without considering returns
        return remaining_amount / months_left
    
    def calculate_sip_amount(self) -> float:
        """Calculate SIP amount considering expected returns"""
        if not self.target_date or self.expected_return_rate <= 0:
            return self.calculate_required_monthly_amount()
        
        remaining_amount = max(0, self.target_amount - self.current_amount)
        months_left = max(1, (self.target_date.date() - date.today()).days / 30.44)
        monthly_rate = self.expected_return_rate / 100 / 12
        
        # SIP formula: FV = PMT * [((1 + r)^n - 1) / r]
        # PMT = FV * r / ((1 + r)^n - 1)
        if monthly_rate > 0:
            factor = ((1 + monthly_rate) ** months_left - 1) / monthly_rate
            return remaining_amount / factor if factor > 0 else remaining_amount / months_left
        else:
            return remaining_amount / months_left


class GoalMilestone(Base):
    """Goal milestone model for tracking progress"""
    __tablename__ = "goal_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("financial_goals.id"), nullable=False, index=True)
    
    # Milestone details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_amount = Column(Float, nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    goal = relationship("FinancialGoal", back_populates="milestones")
    
    def __repr__(self):
        return f"<GoalMilestone(id={self.id}, name='{self.name}', target_amount={self.target_amount})>"


class GoalContribution(Base):
    """Goal contribution tracking"""
    __tablename__ = "goal_contributions"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("financial_goals.id"), nullable=False, index=True)
    
    # Contribution details
    amount = Column(Float, nullable=False)
    contribution_date = Column(DateTime(timezone=True), nullable=False)
    contribution_type = Column(String(50), default="manual")  # manual, automatic, bonus
    
    # Source information
    source_account = Column(String(100))
    transaction_reference = Column(String(100))
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    goal = relationship("FinancialGoal", back_populates="contributions")
    
    def __repr__(self):
        return f"<GoalContribution(id={self.id}, amount={self.amount}, date={self.contribution_date})>"


class GoalTemplate(Base):
    """Pre-defined goal templates for common financial goals"""
    __tablename__ = "goal_templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    goal_type = Column(Enum(GoalType), nullable=False)

    # Default parameters
    default_timeline_years = Column(Integer)
    default_inflation_rate = Column(Float, default=6.0)
    default_expected_return = Column(Float, default=12.0)
    recommended_risk_level = Column(String(20))

    # Template configuration (JSON)
    template_config = Column(Text)  # JSON with additional parameters

    # Usage tracking
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<GoalTemplate(id={self.id}, name='{self.name}', type='{self.goal_type}')>"


class GoalRecommendation(Base):
    """AI-generated goal recommendations"""
    __tablename__ = "goal_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    goal_id = Column(Integer, ForeignKey("financial_goals.id"), index=True)

    # Recommendation details
    recommendation_type = Column(String(50), nullable=False)  # increase_contribution, adjust_timeline, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Recommendation data (JSON)
    recommendation_data = Column(Text)  # JSON with specific recommendations

    # Impact analysis
    potential_impact = Column(Text)  # Expected impact description
    confidence_score = Column(Float)  # AI confidence in recommendation (0-100)

    # Status
    is_accepted = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    accepted_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    goal = relationship("FinancialGoal")

    def __repr__(self):
        return f"<GoalRecommendation(id={self.id}, type='{self.recommendation_type}', user_id={self.user_id})>"


class GoalAlert(Base):
    """Goal-related alerts and notifications"""
    __tablename__ = "goal_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    goal_id = Column(Integer, ForeignKey("financial_goals.id"), nullable=False, index=True)

    # Alert details
    alert_type = Column(String(50), nullable=False)  # milestone_reached, off_track, contribution_due, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # info, warning, critical

    # Alert data (JSON)
    alert_data = Column(Text)  # JSON with additional alert information

    # Status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User")
    goal = relationship("FinancialGoal")

    def __repr__(self):
        return f"<GoalAlert(id={self.id}, type='{self.alert_type}', goal_id={self.goal_id})>"
