"""
Tax Planning Models - Comprehensive tax optimization for Indian investors
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class TaxRegime(enum.Enum):
    """Tax regime options in India"""
    OLD_REGIME = "old_regime"
    NEW_REGIME = "new_regime"


class InvestmentType(enum.Enum):
    """Investment types for tax purposes"""
    EQUITY = "equity"
    DEBT = "debt"
    HYBRID = "hybrid"
    ELSS = "elss"
    PPF = "ppf"
    EPF = "epf"
    NSC = "nsc"
    TAX_SAVER_FD = "tax_saver_fd"
    LIFE_INSURANCE = "life_insurance"
    HEALTH_INSURANCE = "health_insurance"
    HOME_LOAN = "home_loan"
    EDUCATION_LOAN = "education_loan"


class TaxSection(enum.Enum):
    """Tax sections for deductions"""
    SECTION_80C = "80c"
    SECTION_80CCC = "80ccc"
    SECTION_80CCD_1 = "80ccd_1"
    SECTION_80CCD_1B = "80ccd_1b"
    SECTION_80CCD_2 = "80ccd_2"
    SECTION_80D = "80d"
    SECTION_80E = "80e"
    SECTION_80EE = "80ee"
    SECTION_80EEA = "80eea"
    SECTION_80G = "80g"
    SECTION_80TTA = "80tta"
    SECTION_80TTB = "80ttb"
    SECTION_24B = "24b"


class CapitalGainType(enum.Enum):
    """Capital gains types"""
    SHORT_TERM_EQUITY = "stcg_equity"
    LONG_TERM_EQUITY = "ltcg_equity"
    SHORT_TERM_DEBT = "stcg_debt"
    LONG_TERM_DEBT = "ltcg_debt"
    SHORT_TERM_OTHER = "stcg_other"
    LONG_TERM_OTHER = "ltcg_other"


class TaxProfile(Base):
    """User tax profile and preferences"""
    __tablename__ = "tax_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Basic tax information
    tax_regime = Column(Enum(TaxRegime), nullable=False, default=TaxRegime.OLD_REGIME)
    annual_income = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    
    # Personal details affecting tax
    is_senior_citizen = Column(Boolean, default=False)
    is_super_senior_citizen = Column(Boolean, default=False)
    has_disability = Column(Boolean, default=False)
    
    # Employment details
    employer_pf_contribution = Column(Float, default=0)
    employer_nps_contribution = Column(Float, default=0)
    professional_tax = Column(Float, default=0)
    
    # Current deductions
    section_80c_investments = Column(Float, default=0)
    section_80d_premium = Column(Float, default=0)
    home_loan_interest = Column(Float, default=0)
    home_loan_principal = Column(Float, default=0)
    education_loan_interest = Column(Float, default=0)
    
    # Tax preferences
    risk_appetite_for_tax_saving = Column(String(20), default="moderate")  # conservative, moderate, aggressive
    preferred_lock_in_period = Column(Integer, default=3)  # years
    
    # Assessment year
    assessment_year = Column(String(10), nullable=False)  # e.g., "2024-25"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    tax_calculations = relationship("TaxCalculation", back_populates="tax_profile", cascade="all, delete-orphan")
    tax_savings = relationship("TaxSavingInvestment", back_populates="tax_profile", cascade="all, delete-orphan")
    capital_gains = relationship("CapitalGain", back_populates="tax_profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TaxProfile(id={self.id}, user_id={self.user_id}, regime='{self.tax_regime}')>"


class TaxCalculation(Base):
    """Tax calculation results"""
    __tablename__ = "tax_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    tax_profile_id = Column(Integer, ForeignKey("tax_profiles.id"), nullable=False, index=True)
    
    # Income details
    gross_income = Column(Float, nullable=False)
    standard_deduction = Column(Float, default=50000)  # Standard deduction for FY 2023-24
    
    # Deductions under Chapter VI-A
    total_80c_deduction = Column(Float, default=0)
    total_80d_deduction = Column(Float, default=0)
    total_80ccd_1b_deduction = Column(Float, default=0)
    total_other_deductions = Column(Float, default=0)
    
    # Taxable income
    taxable_income = Column(Float, nullable=False)
    
    # Tax calculations
    income_tax = Column(Float, nullable=False)
    surcharge = Column(Float, default=0)
    health_education_cess = Column(Float, nullable=False)
    total_tax = Column(Float, nullable=False)
    
    # Tax regime comparison
    old_regime_tax = Column(Float)
    new_regime_tax = Column(Float)
    tax_savings_amount = Column(Float)
    recommended_regime = Column(Enum(TaxRegime))
    
    # Calculation metadata
    calculation_date = Column(DateTime(timezone=True), nullable=False)
    assessment_year = Column(String(10), nullable=False)
    
    # Additional details (JSON)
    calculation_details = Column(Text)  # JSON with detailed breakdown
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tax_profile = relationship("TaxProfile", back_populates="tax_calculations")
    
    def __repr__(self):
        return f"<TaxCalculation(id={self.id}, taxable_income={self.taxable_income}, total_tax={self.total_tax})>"


class TaxSavingInvestment(Base):
    """Tax saving investment recommendations and tracking"""
    __tablename__ = "tax_saving_investments"
    
    id = Column(Integer, primary_key=True, index=True)
    tax_profile_id = Column(Integer, ForeignKey("tax_profiles.id"), nullable=False, index=True)
    
    # Investment details
    investment_type = Column(Enum(InvestmentType), nullable=False)
    tax_section = Column(Enum(TaxSection), nullable=False)
    
    # Investment specifics
    investment_name = Column(String(255), nullable=False)
    investment_amount = Column(Float, nullable=False)
    annual_limit = Column(Float, nullable=False)
    
    # Tax benefits
    deduction_amount = Column(Float, nullable=False)
    tax_saved = Column(Float, nullable=False)
    effective_cost = Column(Float, nullable=False)  # Investment amount - tax saved
    
    # Investment characteristics
    lock_in_period_years = Column(Integer, default=0)
    expected_return_rate = Column(Float)
    risk_level = Column(String(20))  # low, moderate, high
    
    # Status
    is_recommended = Column(Boolean, default=False)
    is_invested = Column(Boolean, default=False)
    investment_date = Column(DateTime(timezone=True))
    
    # Additional details
    investment_details = Column(Text)  # JSON with additional details
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tax_profile = relationship("TaxProfile", back_populates="tax_savings")
    
    def __repr__(self):
        return f"<TaxSavingInvestment(id={self.id}, type='{self.investment_type}', amount={self.investment_amount})>"


class CapitalGain(Base):
    """Capital gains tracking and tax calculation"""
    __tablename__ = "capital_gains"
    
    id = Column(Integer, primary_key=True, index=True)
    tax_profile_id = Column(Integer, ForeignKey("tax_profiles.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    
    # Transaction details
    security_symbol = Column(String(50), nullable=False)
    security_name = Column(String(255), nullable=False)
    
    # Buy details
    buy_date = Column(DateTime(timezone=True), nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_quantity = Column(Float, nullable=False)
    buy_amount = Column(Float, nullable=False)
    
    # Sell details
    sell_date = Column(DateTime(timezone=True), nullable=False)
    sell_price = Column(Float, nullable=False)
    sell_quantity = Column(Float, nullable=False)
    sell_amount = Column(Float, nullable=False)
    
    # Gain/Loss calculation
    capital_gain_loss = Column(Float, nullable=False)  # Positive for gain, negative for loss
    gain_type = Column(Enum(CapitalGainType), nullable=False)
    holding_period_days = Column(Integer, nullable=False)
    
    # Tax calculation
    applicable_tax_rate = Column(Float, nullable=False)
    tax_on_gain = Column(Float, nullable=False)
    
    # Indexation (for debt instruments)
    cost_inflation_index_buy = Column(Float)
    cost_inflation_index_sell = Column(Float)
    indexed_cost = Column(Float)
    
    # STT and other charges
    stt_paid = Column(Float, default=0)
    brokerage_buy = Column(Float, default=0)
    brokerage_sell = Column(Float, default=0)
    other_charges = Column(Float, default=0)
    
    # Assessment year
    assessment_year = Column(String(10), nullable=False)
    
    # Status
    is_realized = Column(Boolean, default=True)
    is_reported = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tax_profile = relationship("TaxProfile", back_populates="capital_gains")
    portfolio = relationship("Portfolio")
    
    def __repr__(self):
        return f"<CapitalGain(id={self.id}, symbol='{self.security_symbol}', gain={self.capital_gain_loss})>"


class TaxOptimizationSuggestion(Base):
    """AI-generated tax optimization suggestions"""
    __tablename__ = "tax_optimization_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    tax_profile_id = Column(Integer, ForeignKey("tax_profiles.id"), nullable=False, index=True)
    
    # Suggestion details
    suggestion_type = Column(String(50), nullable=False)  # investment, regime_change, timing, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Financial impact
    potential_tax_savings = Column(Float, nullable=False)
    investment_required = Column(Float, default=0)
    net_benefit = Column(Float, nullable=False)
    
    # Implementation details
    implementation_steps = Column(Text)  # JSON with steps
    timeline = Column(String(50))  # immediate, this_month, this_quarter, this_year
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Risk and considerations
    risk_level = Column(String(20), default="low")
    considerations = Column(Text)  # JSON with considerations
    
    # Status
    is_active = Column(Boolean, default=True)
    is_implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime(timezone=True))
    
    # AI metadata
    confidence_score = Column(Float, default=0.8)  # AI confidence in suggestion
    generated_by = Column(String(50), default="tax_agent")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tax_profile = relationship("TaxProfile")
    
    def __repr__(self):
        return f"<TaxOptimizationSuggestion(id={self.id}, type='{self.suggestion_type}', savings={self.potential_tax_savings})>"


class TaxDocument(Base):
    """Tax-related documents and certificates"""
    __tablename__ = "tax_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tax_profile_id = Column(Integer, ForeignKey("tax_profiles.id"), nullable=False, index=True)
    
    # Document details
    document_type = Column(String(50), nullable=False)  # form16, investment_proof, etc.
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    
    # Document metadata
    assessment_year = Column(String(10), nullable=False)
    document_date = Column(DateTime(timezone=True))
    
    # Status
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tax_profile = relationship("TaxProfile")
    
    def __repr__(self):
        return f"<TaxDocument(id={self.id}, type='{self.document_type}', name='{self.document_name}')>"
