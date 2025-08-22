"""
User model for InvestAI application
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class RiskProfile(str, enum.Enum):
    """User risk profile enumeration"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class InvestmentExperience(str, enum.Enum):
    """User investment experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    # Basic information
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    age = Column(Integer)
    phone_number = Column(String(15))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    
    # Financial profile
    annual_income = Column(Float)
    monthly_expenses = Column(Float)
    current_savings = Column(Float)
    investment_experience = Column(Enum(InvestmentExperience))
    risk_profile = Column(Enum(RiskProfile))
    
    # Investment preferences
    preferred_investment_amount = Column(Float)
    investment_horizon_years = Column(Integer)
    financial_goals = Column(Text)  # JSON string of goals
    
    # Tax information
    pan_number = Column(String(10))
    tax_bracket = Column(Float)  # Tax rate percentage
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Risk assessment
    risk_assessment_score = Column(Float)
    risk_assessment_date = Column(DateTime(timezone=True))
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("FinancialGoal", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def is_profile_complete(self) -> bool:
        """Check if user profile is complete"""
        required_fields = [
            self.age, self.annual_income, self.investment_experience,
            self.risk_profile, self.investment_horizon_years
        ]
        return all(field is not None for field in required_fields)
    
    @property
    def risk_score_category(self) -> str:
        """Get risk category based on assessment score"""
        if not self.risk_assessment_score:
            return "not_assessed"
        
        if self.risk_assessment_score <= 25:
            return "conservative"
        elif self.risk_assessment_score <= 50:
            return "moderate"
        elif self.risk_assessment_score <= 75:
            return "aggressive"
        else:
            return "very_aggressive"


class UserPreferences(Base):
    """User preferences and settings"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    
    # Dashboard preferences
    default_currency = Column(String(3), default="INR")
    dashboard_layout = Column(Text)  # JSON string
    preferred_charts = Column(Text)  # JSON string
    
    # Investment preferences
    auto_rebalance = Column(Boolean, default=False)
    rebalance_threshold = Column(Float, default=5.0)  # Percentage
    dividend_reinvestment = Column(Boolean, default=True)
    
    # Privacy settings
    profile_visibility = Column(String(20), default="private")
    share_portfolio_performance = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id})>"
