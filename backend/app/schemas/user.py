"""
User schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
from app.models.user import RiskProfile, InvestmentExperience


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: str
    phone_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    age: Optional[int] = None
    annual_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    current_savings: Optional[float] = None
    investment_experience: Optional[InvestmentExperience] = None
    risk_profile: Optional[RiskProfile] = None
    preferred_investment_amount: Optional[float] = None
    investment_horizon_years: Optional[int] = None
    financial_goals: Optional[str] = None
    pan_number: Optional[str] = None
    tax_bracket: Optional[float] = None
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 18 or v > 100):
            raise ValueError('Age must be between 18 and 100')
        return v
    
    @validator('annual_income', 'monthly_expenses', 'current_savings', 'preferred_investment_amount')
    def validate_positive_amounts(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount must be positive')
        return v
    
    @validator('investment_horizon_years')
    def validate_investment_horizon(cls, v):
        if v is not None and (v < 1 or v > 50):
            raise ValueError('Investment horizon must be between 1 and 50 years')
        return v
    
    @validator('tax_bracket')
    def validate_tax_bracket(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError('Tax bracket must be between 0 and 50 percent')
        return v
    
    @validator('pan_number')
    def validate_pan(cls, v):
        if v and len(v) != 10:
            raise ValueError('PAN number must be 10 characters long')
        return v


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    username: str
    full_name: str
    phone_number: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    age: Optional[int]
    annual_income: Optional[float]
    monthly_expenses: Optional[float]
    current_savings: Optional[float]
    investment_experience: Optional[InvestmentExperience]
    risk_profile: Optional[RiskProfile]
    preferred_investment_amount: Optional[float]
    investment_horizon_years: Optional[int]
    financial_goals: Optional[str]
    pan_number: Optional[str]
    tax_bracket: Optional[float]
    is_active: bool
    is_verified: bool
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    risk_assessment_score: Optional[float]
    risk_assessment_date: Optional[datetime]
    
    class Config:
        from_attributes = True


class RiskAssessment(BaseModel):
    """Schema for risk assessment questionnaire"""
    age: int
    annual_income: float
    investment_experience: InvestmentExperience
    investment_horizon_years: int
    risk_tolerance_score: int  # 1-10 scale
    financial_goals_priority: List[str]
    emergency_fund_months: int
    debt_to_income_ratio: float
    investment_knowledge_score: int  # 1-10 scale
    market_volatility_comfort: int  # 1-10 scale
    
    @validator('risk_tolerance_score', 'investment_knowledge_score', 'market_volatility_comfort')
    def validate_score_range(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Score must be between 1 and 10')
        return v
    
    @validator('emergency_fund_months')
    def validate_emergency_fund(cls, v):
        if v < 0 or v > 24:
            raise ValueError('Emergency fund must be between 0 and 24 months')
        return v
    
    @validator('debt_to_income_ratio')
    def validate_debt_ratio(cls, v):
        if v < 0 or v > 10:
            raise ValueError('Debt to income ratio must be between 0 and 10')
        return v


class RiskAssessmentResult(BaseModel):
    """Schema for risk assessment result"""
    risk_score: float
    risk_profile: RiskProfile
    recommended_allocation: dict
    assessment_summary: str
    recommendations: List[str]


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    default_currency: Optional[str] = None
    dashboard_layout: Optional[str] = None
    preferred_charts: Optional[str] = None
    auto_rebalance: Optional[bool] = None
    rebalance_threshold: Optional[float] = None
    dividend_reinvestment: Optional[bool] = None
    profile_visibility: Optional[str] = None
    share_portfolio_performance: Optional[bool] = None
    
    @validator('default_currency')
    def validate_currency(cls, v):
        if v and v not in ['INR', 'USD', 'EUR']:
            raise ValueError('Currency must be INR, USD, or EUR')
        return v
    
    @validator('rebalance_threshold')
    def validate_rebalance_threshold(cls, v):
        if v is not None and (v < 1 or v > 20):
            raise ValueError('Rebalance threshold must be between 1 and 20 percent')
        return v
    
    @validator('profile_visibility')
    def validate_visibility(cls, v):
        if v and v not in ['private', 'friends', 'public']:
            raise ValueError('Profile visibility must be private, friends, or public')
        return v
