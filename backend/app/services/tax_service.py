"""
Tax Planning Service - Comprehensive tax optimization for Indian investors
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging
import math

from app.models.tax import (
    TaxProfile, TaxCalculation, TaxSavingInvestment, CapitalGain, 
    TaxOptimizationSuggestion, TaxRegime, InvestmentType, TaxSection, CapitalGainType
)
from app.models.portfolio import Portfolio, Transaction
from app.models.user import User

logger = logging.getLogger(__name__)


class TaxPlanningService:
    """Service for comprehensive tax planning and optimization"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Tax slabs for FY 2023-24 (AY 2024-25)
        self.old_regime_slabs = [
            (250000, 0.0),      # Up to 2.5L - 0%
            (500000, 0.05),     # 2.5L to 5L - 5%
            (1000000, 0.20),    # 5L to 10L - 20%
            (float('inf'), 0.30) # Above 10L - 30%
        ]
        
        self.new_regime_slabs = [
            (300000, 0.0),      # Up to 3L - 0%
            (600000, 0.05),     # 3L to 6L - 5%
            (900000, 0.10),     # 6L to 9L - 10%
            (1200000, 0.15),    # 9L to 12L - 15%
            (1500000, 0.20),    # 12L to 15L - 20%
            (float('inf'), 0.30) # Above 15L - 30%
        ]
        
        # Deduction limits for FY 2023-24
        self.deduction_limits = {
            TaxSection.SECTION_80C: 150000,
            TaxSection.SECTION_80CCC: 150000,  # Combined with 80C
            TaxSection.SECTION_80CCD_1: 150000,  # Combined with 80C
            TaxSection.SECTION_80CCD_1B: 50000,
            TaxSection.SECTION_80D: 25000,  # Regular, 50000 for senior citizens
            TaxSection.SECTION_80E: float('inf'),  # No limit
            TaxSection.SECTION_80EE: 200000,
            TaxSection.SECTION_80EEA: 150000,
            TaxSection.SECTION_80TTA: 10000,
            TaxSection.SECTION_80TTB: 50000,
        }
    
    # Tax Profile Management
    def create_tax_profile(self, user_id: int, profile_data: Dict[str, Any]) -> TaxProfile:
        """Create tax profile for user"""
        try:
            # Check if profile already exists
            existing_profile = self.db.query(TaxProfile).filter(
                TaxProfile.user_id == user_id
            ).first()
            
            if existing_profile:
                raise ValueError("Tax profile already exists for user")
            
            # Create new tax profile
            tax_profile = TaxProfile(
                user_id=user_id,
                tax_regime=TaxRegime(profile_data.get("tax_regime", "old_regime")),
                annual_income=profile_data["annual_income"],
                age=profile_data["age"],
                is_senior_citizen=profile_data.get("is_senior_citizen", False),
                is_super_senior_citizen=profile_data.get("is_super_senior_citizen", False),
                has_disability=profile_data.get("has_disability", False),
                employer_pf_contribution=profile_data.get("employer_pf_contribution", 0),
                employer_nps_contribution=profile_data.get("employer_nps_contribution", 0),
                professional_tax=profile_data.get("professional_tax", 0),
                section_80c_investments=profile_data.get("section_80c_investments", 0),
                section_80d_premium=profile_data.get("section_80d_premium", 0),
                home_loan_interest=profile_data.get("home_loan_interest", 0),
                home_loan_principal=profile_data.get("home_loan_principal", 0),
                education_loan_interest=profile_data.get("education_loan_interest", 0),
                risk_appetite_for_tax_saving=profile_data.get("risk_appetite_for_tax_saving", "moderate"),
                preferred_lock_in_period=profile_data.get("preferred_lock_in_period", 3),
                assessment_year=profile_data.get("assessment_year", "2024-25")
            )
            
            self.db.add(tax_profile)
            self.db.commit()
            self.db.refresh(tax_profile)
            
            # Generate initial tax calculation
            self.calculate_tax(tax_profile.id)
            
            # Generate tax optimization suggestions
            self.generate_tax_optimization_suggestions(tax_profile.id)
            
            logger.info(f"Created tax profile {tax_profile.id} for user {user_id}")
            return tax_profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create tax profile: {str(e)}")
            raise
    
    def get_tax_profile(self, user_id: int) -> Optional[TaxProfile]:
        """Get tax profile for user"""
        return self.db.query(TaxProfile).filter(TaxProfile.user_id == user_id).first()
    
    def update_tax_profile(self, user_id: int, profile_data: Dict[str, Any]) -> TaxProfile:
        """Update tax profile"""
        try:
            tax_profile = self.get_tax_profile(user_id)
            if not tax_profile:
                raise ValueError("Tax profile not found")
            
            # Update fields
            for field, value in profile_data.items():
                if hasattr(tax_profile, field):
                    if field == "tax_regime" and isinstance(value, str):
                        setattr(tax_profile, field, TaxRegime(value))
                    else:
                        setattr(tax_profile, field, value)
            
            self.db.commit()
            self.db.refresh(tax_profile)
            
            # Recalculate tax
            self.calculate_tax(tax_profile.id)
            
            # Regenerate suggestions
            self.generate_tax_optimization_suggestions(tax_profile.id)
            
            logger.info(f"Updated tax profile {tax_profile.id}")
            return tax_profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update tax profile: {str(e)}")
            raise
    
    # Tax Calculations
    def calculate_tax(self, tax_profile_id: int) -> TaxCalculation:
        """Calculate comprehensive tax for user"""
        try:
            tax_profile = self.db.query(TaxProfile).filter(
                TaxProfile.id == tax_profile_id
            ).first()
            
            if not tax_profile:
                raise ValueError("Tax profile not found")
            
            # Calculate tax under both regimes
            old_regime_tax = self._calculate_tax_old_regime(tax_profile)
            new_regime_tax = self._calculate_tax_new_regime(tax_profile)
            
            # Determine recommended regime
            recommended_regime = TaxRegime.OLD_REGIME if old_regime_tax["total_tax"] < new_regime_tax["total_tax"] else TaxRegime.NEW_REGIME
            tax_savings = abs(old_regime_tax["total_tax"] - new_regime_tax["total_tax"])
            
            # Use current regime for main calculation
            current_calculation = old_regime_tax if tax_profile.tax_regime == TaxRegime.OLD_REGIME else new_regime_tax
            
            # Create tax calculation record
            tax_calculation = TaxCalculation(
                tax_profile_id=tax_profile_id,
                gross_income=tax_profile.annual_income,
                standard_deduction=current_calculation["standard_deduction"],
                total_80c_deduction=current_calculation["total_80c_deduction"],
                total_80d_deduction=current_calculation["total_80d_deduction"],
                total_80ccd_1b_deduction=current_calculation["total_80ccd_1b_deduction"],
                total_other_deductions=current_calculation["total_other_deductions"],
                taxable_income=current_calculation["taxable_income"],
                income_tax=current_calculation["income_tax"],
                surcharge=current_calculation["surcharge"],
                health_education_cess=current_calculation["health_education_cess"],
                total_tax=current_calculation["total_tax"],
                old_regime_tax=old_regime_tax["total_tax"],
                new_regime_tax=new_regime_tax["total_tax"],
                tax_savings_amount=tax_savings,
                recommended_regime=recommended_regime,
                calculation_date=datetime.now(),
                assessment_year=tax_profile.assessment_year,
                calculation_details=json.dumps({
                    "old_regime": old_regime_tax,
                    "new_regime": new_regime_tax,
                    "comparison": {
                        "savings_amount": tax_savings,
                        "savings_percentage": (tax_savings / max(old_regime_tax["total_tax"], new_regime_tax["total_tax"])) * 100,
                        "recommended_regime": recommended_regime.value
                    }
                })
            )
            
            self.db.add(tax_calculation)
            self.db.commit()
            self.db.refresh(tax_calculation)
            
            logger.info(f"Calculated tax for profile {tax_profile_id}")
            return tax_calculation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to calculate tax: {str(e)}")
            raise
    
    def _calculate_tax_old_regime(self, tax_profile: TaxProfile) -> Dict[str, float]:
        """Calculate tax under old regime"""
        try:
            gross_income = tax_profile.annual_income
            
            # Standard deduction
            standard_deduction = 50000
            
            # Calculate deductions
            total_80c_deduction = min(
                tax_profile.section_80c_investments + 
                tax_profile.employer_pf_contribution + 
                tax_profile.home_loan_principal,
                self.deduction_limits[TaxSection.SECTION_80C]
            )
            
            total_80d_deduction = min(
                tax_profile.section_80d_premium,
                self.deduction_limits[TaxSection.SECTION_80D] * (2 if tax_profile.is_senior_citizen else 1)
            )
            
            total_80ccd_1b_deduction = min(
                tax_profile.employer_nps_contribution,
                self.deduction_limits[TaxSection.SECTION_80CCD_1B]
            )
            
            # Other deductions (simplified)
            total_other_deductions = tax_profile.education_loan_interest + tax_profile.home_loan_interest
            
            # Calculate taxable income
            total_deductions = (standard_deduction + total_80c_deduction + 
                              total_80d_deduction + total_80ccd_1b_deduction + 
                              total_other_deductions)
            
            taxable_income = max(0, gross_income - total_deductions)
            
            # Calculate income tax
            income_tax = self._calculate_income_tax(taxable_income, self.old_regime_slabs, tax_profile)
            
            # Calculate surcharge
            surcharge = self._calculate_surcharge(taxable_income, income_tax)
            
            # Calculate health and education cess (4%)
            health_education_cess = (income_tax + surcharge) * 0.04
            
            # Total tax
            total_tax = income_tax + surcharge + health_education_cess
            
            return {
                "gross_income": gross_income,
                "standard_deduction": standard_deduction,
                "total_80c_deduction": total_80c_deduction,
                "total_80d_deduction": total_80d_deduction,
                "total_80ccd_1b_deduction": total_80ccd_1b_deduction,
                "total_other_deductions": total_other_deductions,
                "total_deductions": total_deductions,
                "taxable_income": taxable_income,
                "income_tax": income_tax,
                "surcharge": surcharge,
                "health_education_cess": health_education_cess,
                "total_tax": total_tax
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate old regime tax: {str(e)}")
            raise
    
    def _calculate_tax_new_regime(self, tax_profile: TaxProfile) -> Dict[str, float]:
        """Calculate tax under new regime"""
        try:
            gross_income = tax_profile.annual_income
            
            # Standard deduction (same as old regime)
            standard_deduction = 50000
            
            # Limited deductions in new regime
            total_80c_deduction = 0  # No 80C deductions
            total_80d_deduction = 0  # No 80D deductions
            total_80ccd_1b_deduction = min(
                tax_profile.employer_nps_contribution,
                self.deduction_limits[TaxSection.SECTION_80CCD_1B]
            )  # Only employer NPS contribution allowed
            
            # Other deductions (very limited)
            total_other_deductions = tax_profile.education_loan_interest  # Only education loan interest
            
            # Calculate taxable income
            total_deductions = (standard_deduction + total_80ccd_1b_deduction + 
                              total_other_deductions)
            
            taxable_income = max(0, gross_income - total_deductions)
            
            # Calculate income tax
            income_tax = self._calculate_income_tax(taxable_income, self.new_regime_slabs, tax_profile)
            
            # Calculate surcharge
            surcharge = self._calculate_surcharge(taxable_income, income_tax)
            
            # Calculate health and education cess (4%)
            health_education_cess = (income_tax + surcharge) * 0.04
            
            # Total tax
            total_tax = income_tax + surcharge + health_education_cess
            
            return {
                "gross_income": gross_income,
                "standard_deduction": standard_deduction,
                "total_80c_deduction": total_80c_deduction,
                "total_80d_deduction": total_80d_deduction,
                "total_80ccd_1b_deduction": total_80ccd_1b_deduction,
                "total_other_deductions": total_other_deductions,
                "total_deductions": total_deductions,
                "taxable_income": taxable_income,
                "income_tax": income_tax,
                "surcharge": surcharge,
                "health_education_cess": health_education_cess,
                "total_tax": total_tax
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate new regime tax: {str(e)}")
            raise
    
    def _calculate_income_tax(self, taxable_income: float, tax_slabs: List[Tuple[float, float]], 
                            tax_profile: TaxProfile) -> float:
        """Calculate income tax based on slabs"""
        try:
            if taxable_income <= 0:
                return 0
            
            # Senior citizen exemption limit adjustment
            if tax_profile.is_super_senior_citizen and taxable_income <= 500000:
                return 0
            elif tax_profile.is_senior_citizen and taxable_income <= 300000:
                return 0
            
            income_tax = 0
            remaining_income = taxable_income
            previous_limit = 0
            
            for limit, rate in tax_slabs:
                if remaining_income <= 0:
                    break
                
                taxable_in_slab = min(remaining_income, limit - previous_limit)
                income_tax += taxable_in_slab * rate
                remaining_income -= taxable_in_slab
                previous_limit = limit
                
                if limit == float('inf'):
                    break
            
            return income_tax
            
        except Exception as e:
            logger.error(f"Failed to calculate income tax: {str(e)}")
            return 0
    
    def _calculate_surcharge(self, taxable_income: float, income_tax: float) -> float:
        """Calculate surcharge based on income"""
        try:
            if taxable_income <= 5000000:
                return 0
            elif taxable_income <= 10000000:
                return income_tax * 0.10  # 10% surcharge
            elif taxable_income <= 20000000:
                return income_tax * 0.15  # 15% surcharge
            elif taxable_income <= 50000000:
                return income_tax * 0.25  # 25% surcharge
            else:
                return income_tax * 0.37  # 37% surcharge
                
        except Exception as e:
            logger.error(f"Failed to calculate surcharge: {str(e)}")
            return 0

    # Capital Gains Calculations
    def calculate_capital_gains(self, user_id: int, portfolio_id: Optional[int] = None) -> List[CapitalGain]:
        """Calculate capital gains from portfolio transactions"""
        try:
            tax_profile = self.get_tax_profile(user_id)
            if not tax_profile:
                raise ValueError("Tax profile not found")

            # Get transactions
            query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
            if portfolio_id:
                query = query.filter(Transaction.portfolio_id == portfolio_id)

            transactions = query.filter(Transaction.transaction_type == "sell").all()

            capital_gains = []

            for sell_transaction in transactions:
                # Find corresponding buy transaction(s)
                buy_transactions = self.db.query(Transaction).filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.symbol == sell_transaction.symbol,
                        Transaction.transaction_type == "buy",
                        Transaction.transaction_date < sell_transaction.transaction_date
                    )
                ).order_by(Transaction.transaction_date).all()

                if not buy_transactions:
                    continue

                # Calculate capital gain using FIFO method
                remaining_sell_quantity = sell_transaction.quantity

                for buy_transaction in buy_transactions:
                    if remaining_sell_quantity <= 0:
                        break

                    # Calculate quantity for this pair
                    quantity = min(remaining_sell_quantity, buy_transaction.quantity)

                    # Calculate holding period
                    holding_period = (sell_transaction.transaction_date - buy_transaction.transaction_date).days

                    # Determine gain type
                    gain_type = self._determine_capital_gain_type(
                        sell_transaction.symbol, holding_period
                    )

                    # Calculate amounts
                    buy_amount = quantity * buy_transaction.price
                    sell_amount = quantity * sell_transaction.price

                    # Calculate capital gain/loss
                    capital_gain_loss = sell_amount - buy_amount

                    # Calculate tax
                    tax_rate = self._get_capital_gains_tax_rate(gain_type, tax_profile)
                    tax_on_gain = max(0, capital_gain_loss * tax_rate)

                    # Create capital gain record
                    capital_gain = CapitalGain(
                        tax_profile_id=tax_profile.id,
                        portfolio_id=sell_transaction.portfolio_id,
                        security_symbol=sell_transaction.symbol,
                        security_name=sell_transaction.symbol,  # Would be fetched from market data
                        buy_date=buy_transaction.transaction_date,
                        buy_price=buy_transaction.price,
                        buy_quantity=quantity,
                        buy_amount=buy_amount,
                        sell_date=sell_transaction.transaction_date,
                        sell_price=sell_transaction.price,
                        sell_quantity=quantity,
                        sell_amount=sell_amount,
                        capital_gain_loss=capital_gain_loss,
                        gain_type=gain_type,
                        holding_period_days=holding_period,
                        applicable_tax_rate=tax_rate,
                        tax_on_gain=tax_on_gain,
                        assessment_year=tax_profile.assessment_year
                    )

                    self.db.add(capital_gain)
                    capital_gains.append(capital_gain)

                    remaining_sell_quantity -= quantity

            self.db.commit()
            logger.info(f"Calculated {len(capital_gains)} capital gains for user {user_id}")
            return capital_gains

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to calculate capital gains: {str(e)}")
            raise

    def _determine_capital_gain_type(self, symbol: str, holding_period_days: int) -> CapitalGainType:
        """Determine capital gain type based on asset and holding period"""
        try:
            # Simplified logic - would be enhanced with actual asset classification
            is_equity = True  # Assume equity for now

            if is_equity:
                if holding_period_days > 365:
                    return CapitalGainType.LONG_TERM_EQUITY
                else:
                    return CapitalGainType.SHORT_TERM_EQUITY
            else:
                if holding_period_days > 1095:  # 3 years for debt
                    return CapitalGainType.LONG_TERM_DEBT
                else:
                    return CapitalGainType.SHORT_TERM_DEBT

        except Exception as e:
            logger.error(f"Failed to determine capital gain type: {str(e)}")
            return CapitalGainType.SHORT_TERM_EQUITY

    def _get_capital_gains_tax_rate(self, gain_type: CapitalGainType, tax_profile: TaxProfile) -> float:
        """Get applicable tax rate for capital gains"""
        try:
            tax_rates = {
                CapitalGainType.SHORT_TERM_EQUITY: 0.15,  # 15% + cess
                CapitalGainType.LONG_TERM_EQUITY: 0.10,   # 10% above 1L exemption + cess
                CapitalGainType.SHORT_TERM_DEBT: self._get_marginal_tax_rate(tax_profile),
                CapitalGainType.LONG_TERM_DEBT: 0.20,     # 20% with indexation + cess
                CapitalGainType.SHORT_TERM_OTHER: self._get_marginal_tax_rate(tax_profile),
                CapitalGainType.LONG_TERM_OTHER: 0.20
            }

            base_rate = tax_rates.get(gain_type, 0.15)

            # Add health and education cess (4%)
            return base_rate * 1.04

        except Exception as e:
            logger.error(f"Failed to get capital gains tax rate: {str(e)}")
            return 0.15

    def _get_marginal_tax_rate(self, tax_profile: TaxProfile) -> float:
        """Get marginal tax rate for user"""
        try:
            taxable_income = tax_profile.annual_income  # Simplified

            if tax_profile.tax_regime == TaxRegime.OLD_REGIME:
                slabs = self.old_regime_slabs
            else:
                slabs = self.new_regime_slabs

            for limit, rate in slabs:
                if taxable_income <= limit:
                    return rate

            return 0.30  # Highest slab

        except Exception as e:
            logger.error(f"Failed to get marginal tax rate: {str(e)}")
            return 0.30

    # Tax Optimization Suggestions
    def generate_tax_optimization_suggestions(self, tax_profile_id: int) -> List[TaxOptimizationSuggestion]:
        """Generate AI-powered tax optimization suggestions"""
        try:
            tax_profile = self.db.query(TaxProfile).filter(
                TaxProfile.id == tax_profile_id
            ).first()

            if not tax_profile:
                raise ValueError("Tax profile not found")

            # Clear existing suggestions
            self.db.query(TaxOptimizationSuggestion).filter(
                TaxOptimizationSuggestion.tax_profile_id == tax_profile_id
            ).delete()

            suggestions = []

            # Section 80C optimization
            suggestions.extend(self._generate_80c_suggestions(tax_profile))

            # Section 80D optimization
            suggestions.extend(self._generate_80d_suggestions(tax_profile))

            # Tax regime optimization
            suggestions.extend(self._generate_regime_suggestions(tax_profile))

            # Capital gains optimization
            suggestions.extend(self._generate_capital_gains_suggestions(tax_profile))

            # Investment timing suggestions
            suggestions.extend(self._generate_timing_suggestions(tax_profile))

            # Add suggestions to database
            for suggestion in suggestions:
                self.db.add(suggestion)

            self.db.commit()
            logger.info(f"Generated {len(suggestions)} tax optimization suggestions")
            return suggestions

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to generate tax optimization suggestions: {str(e)}")
            raise

    def _generate_80c_suggestions(self, tax_profile: TaxProfile) -> List[TaxOptimizationSuggestion]:
        """Generate Section 80C optimization suggestions"""
        suggestions = []

        try:
            current_80c = tax_profile.section_80c_investments + tax_profile.employer_pf_contribution + tax_profile.home_loan_principal
            max_80c = self.deduction_limits[TaxSection.SECTION_80C]
            remaining_80c = max_80c - current_80c

            if remaining_80c > 0 and tax_profile.tax_regime == TaxRegime.OLD_REGIME:
                marginal_rate = self._get_marginal_tax_rate(tax_profile)
                potential_savings = remaining_80c * marginal_rate * 1.04  # Including cess

                # ELSS suggestion
                if tax_profile.risk_appetite_for_tax_saving in ["moderate", "aggressive"]:
                    suggestions.append(TaxOptimizationSuggestion(
                        tax_profile_id=tax_profile.id,
                        suggestion_type="80c_investment",
                        title=f"Invest ₹{remaining_80c:,.0f} in ELSS for tax savings",
                        description=f"Invest the remaining ₹{remaining_80c:,.0f} in Equity Linked Savings Scheme (ELSS) to save ₹{potential_savings:,.0f} in taxes while building wealth.",
                        potential_tax_savings=potential_savings,
                        investment_required=remaining_80c,
                        net_benefit=potential_savings,
                        timeline="this_month",
                        priority="high",
                        risk_level="moderate"
                    ))

                # PPF suggestion
                if tax_profile.preferred_lock_in_period >= 15:
                    suggestions.append(TaxOptimizationSuggestion(
                        tax_profile_id=tax_profile.id,
                        suggestion_type="80c_investment",
                        title=f"Invest ₹{min(remaining_80c, 150000):,.0f} in PPF",
                        description=f"Public Provident Fund offers tax-free returns with 15-year lock-in. Current rate: ~7.1% annually.",
                        potential_tax_savings=min(remaining_80c, 150000) * marginal_rate * 1.04,
                        investment_required=min(remaining_80c, 150000),
                        net_benefit=min(remaining_80c, 150000) * marginal_rate * 1.04,
                        timeline="this_month",
                        priority="medium",
                        risk_level="low"
                    ))

            return suggestions

        except Exception as e:
            logger.error(f"Failed to generate 80C suggestions: {str(e)}")
            return []

    def _generate_80d_suggestions(self, tax_profile: TaxProfile) -> List[TaxOptimizationSuggestion]:
        """Generate Section 80D optimization suggestions"""
        suggestions = []

        try:
            if tax_profile.tax_regime == TaxRegime.NEW_REGIME:
                return suggestions  # No 80D in new regime

            max_80d = self.deduction_limits[TaxSection.SECTION_80D] * (2 if tax_profile.is_senior_citizen else 1)
            remaining_80d = max_80d - tax_profile.section_80d_premium

            if remaining_80d > 0:
                marginal_rate = self._get_marginal_tax_rate(tax_profile)
                potential_savings = remaining_80d * marginal_rate * 1.04

                suggestions.append(TaxOptimizationSuggestion(
                    tax_profile_id=tax_profile.id,
                    suggestion_type="80d_investment",
                    title=f"Increase health insurance premium by ₹{remaining_80d:,.0f}",
                    description=f"Enhance your health coverage while saving ₹{potential_savings:,.0f} in taxes under Section 80D.",
                    potential_tax_savings=potential_savings,
                    investment_required=remaining_80d,
                    net_benefit=potential_savings,
                    timeline="this_quarter",
                    priority="medium",
                    risk_level="low"
                ))

            return suggestions

        except Exception as e:
            logger.error(f"Failed to generate 80D suggestions: {str(e)}")
            return []

    def _generate_regime_suggestions(self, tax_profile: TaxProfile) -> List[TaxOptimizationSuggestion]:
        """Generate tax regime optimization suggestions"""
        suggestions = []

        try:
            # Get latest tax calculation
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()

            if not latest_calculation:
                return suggestions

            if latest_calculation.recommended_regime != tax_profile.tax_regime:
                suggestions.append(TaxOptimizationSuggestion(
                    tax_profile_id=tax_profile.id,
                    suggestion_type="regime_change",
                    title=f"Switch to {latest_calculation.recommended_regime.value.replace('_', ' ').title()} Tax Regime",
                    description=f"Switching to {latest_calculation.recommended_regime.value.replace('_', ' ')} regime can save you ₹{latest_calculation.tax_savings_amount:,.0f} annually.",
                    potential_tax_savings=latest_calculation.tax_savings_amount,
                    investment_required=0,
                    net_benefit=latest_calculation.tax_savings_amount,
                    timeline="this_year",
                    priority="high",
                    risk_level="low"
                ))

            return suggestions

        except Exception as e:
            logger.error(f"Failed to generate regime suggestions: {str(e)}")
            return []

    def _generate_capital_gains_suggestions(self, tax_profile: TaxProfile) -> List[TaxOptimizationSuggestion]:
        """Generate capital gains optimization suggestions"""
        suggestions = []

        try:
            # This would analyze portfolio holdings for tax-loss harvesting opportunities
            # For now, provide general suggestions

            suggestions.append(TaxOptimizationSuggestion(
                tax_profile_id=tax_profile.id,
                suggestion_type="capital_gains_optimization",
                title="Consider tax-loss harvesting",
                description="Review your portfolio for opportunities to book losses to offset capital gains and reduce tax liability.",
                potential_tax_savings=10000,  # Estimated
                investment_required=0,
                net_benefit=10000,
                timeline="this_quarter",
                priority="medium",
                risk_level="low"
            ))

            return suggestions

        except Exception as e:
            logger.error(f"Failed to generate capital gains suggestions: {str(e)}")
            return []

    def _generate_timing_suggestions(self, tax_profile: TaxProfile) -> List[TaxOptimizationSuggestion]:
        """Generate investment timing suggestions"""
        suggestions = []

        try:
            current_month = datetime.now().month

            # Year-end tax planning
            if current_month >= 10:  # October onwards
                suggestions.append(TaxOptimizationSuggestion(
                    tax_profile_id=tax_profile.id,
                    suggestion_type="timing_optimization",
                    title="Complete tax-saving investments before March 31st",
                    description="Ensure all tax-saving investments are completed before the financial year ends to claim deductions.",
                    potential_tax_savings=0,
                    investment_required=0,
                    net_benefit=0,
                    timeline="this_quarter",
                    priority="high",
                    risk_level="low"
                ))

            return suggestions

        except Exception as e:
            logger.error(f"Failed to generate timing suggestions: {str(e)}")
            return []

    # Tax Saving Investment Management
    def get_tax_saving_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get personalized tax-saving investment recommendations"""
        try:
            tax_profile = self.get_tax_profile(user_id)
            if not tax_profile:
                raise ValueError("Tax profile not found")

            recommendations = []

            # Calculate remaining limits
            current_80c = (tax_profile.section_80c_investments +
                          tax_profile.employer_pf_contribution +
                          tax_profile.home_loan_principal)
            remaining_80c = max(0, self.deduction_limits[TaxSection.SECTION_80C] - current_80c)

            marginal_rate = self._get_marginal_tax_rate(tax_profile)

            if remaining_80c > 0 and tax_profile.tax_regime == TaxRegime.OLD_REGIME:
                # ELSS Mutual Funds
                if tax_profile.risk_appetite_for_tax_saving in ["moderate", "aggressive"]:
                    recommendations.append({
                        "investment_type": "ELSS",
                        "name": "Equity Linked Savings Scheme",
                        "recommended_amount": min(remaining_80c, 50000),
                        "tax_section": "80C",
                        "tax_savings": min(remaining_80c, 50000) * marginal_rate * 1.04,
                        "lock_in_period": 3,
                        "expected_return": 12.0,
                        "risk_level": "moderate",
                        "description": "Market-linked tax-saving mutual fund with 3-year lock-in"
                    })

                # PPF
                if tax_profile.preferred_lock_in_period >= 15:
                    recommendations.append({
                        "investment_type": "PPF",
                        "name": "Public Provident Fund",
                        "recommended_amount": min(remaining_80c, 150000),
                        "tax_section": "80C",
                        "tax_savings": min(remaining_80c, 150000) * marginal_rate * 1.04,
                        "lock_in_period": 15,
                        "expected_return": 7.1,
                        "risk_level": "low",
                        "description": "Government-backed tax-free returns with 15-year maturity"
                    })

                # NSC
                if tax_profile.risk_appetite_for_tax_saving == "conservative":
                    recommendations.append({
                        "investment_type": "NSC",
                        "name": "National Savings Certificate",
                        "recommended_amount": min(remaining_80c, 30000),
                        "tax_section": "80C",
                        "tax_savings": min(remaining_80c, 30000) * marginal_rate * 1.04,
                        "lock_in_period": 5,
                        "expected_return": 6.8,
                        "risk_level": "low",
                        "description": "Government-backed fixed return investment"
                    })

                # Tax Saver FD
                recommendations.append({
                    "investment_type": "Tax Saver FD",
                    "name": "Tax Saving Fixed Deposit",
                    "recommended_amount": min(remaining_80c, 25000),
                    "tax_section": "80C",
                    "tax_savings": min(remaining_80c, 25000) * marginal_rate * 1.04,
                    "lock_in_period": 5,
                    "expected_return": 6.5,
                    "risk_level": "very_low",
                    "description": "Bank fixed deposit with tax benefits"
                })

            # Section 80D recommendations
            max_80d = self.deduction_limits[TaxSection.SECTION_80D] * (2 if tax_profile.is_senior_citizen else 1)
            remaining_80d = max(0, max_80d - tax_profile.section_80d_premium)

            if remaining_80d > 0 and tax_profile.tax_regime == TaxRegime.OLD_REGIME:
                recommendations.append({
                    "investment_type": "Health Insurance",
                    "name": "Health Insurance Premium",
                    "recommended_amount": remaining_80d,
                    "tax_section": "80D",
                    "tax_savings": remaining_80d * marginal_rate * 1.04,
                    "lock_in_period": 1,
                    "expected_return": 0,  # Insurance, not investment
                    "risk_level": "low",
                    "description": "Health insurance coverage with tax benefits"
                })

            # NPS recommendations
            if tax_profile.employer_nps_contribution < self.deduction_limits[TaxSection.SECTION_80CCD_1B]:
                remaining_nps = self.deduction_limits[TaxSection.SECTION_80CCD_1B] - tax_profile.employer_nps_contribution
                recommendations.append({
                    "investment_type": "NPS",
                    "name": "National Pension System",
                    "recommended_amount": remaining_nps,
                    "tax_section": "80CCD(1B)",
                    "tax_savings": remaining_nps * marginal_rate * 1.04,
                    "lock_in_period": 60,  # Until retirement
                    "expected_return": 10.0,
                    "risk_level": "moderate",
                    "description": "Retirement-focused investment with additional tax benefits"
                })

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get tax saving recommendations: {str(e)}")
            raise

    def calculate_section_80c_optimization(self, user_id: int) -> Dict[str, Any]:
        """Calculate optimal Section 80C allocation"""
        try:
            tax_profile = self.get_tax_profile(user_id)
            if not tax_profile:
                raise ValueError("Tax profile not found")

            current_80c = (tax_profile.section_80c_investments +
                          tax_profile.employer_pf_contribution +
                          tax_profile.home_loan_principal)

            max_limit = self.deduction_limits[TaxSection.SECTION_80C]
            remaining_limit = max(0, max_limit - current_80c)

            marginal_rate = self._get_marginal_tax_rate(tax_profile)
            potential_savings = remaining_limit * marginal_rate * 1.04

            # Optimal allocation based on risk profile
            optimal_allocation = {}

            if tax_profile.risk_appetite_for_tax_saving == "aggressive":
                optimal_allocation = {
                    "ELSS": min(remaining_limit, 100000),
                    "PPF": min(remaining_limit - 100000, 50000) if remaining_limit > 100000 else 0
                }
            elif tax_profile.risk_appetite_for_tax_saving == "moderate":
                optimal_allocation = {
                    "ELSS": min(remaining_limit, 75000),
                    "PPF": min(remaining_limit - 75000, 75000) if remaining_limit > 75000 else 0
                }
            else:  # conservative
                optimal_allocation = {
                    "PPF": min(remaining_limit, 100000),
                    "NSC": min(remaining_limit - 100000, 50000) if remaining_limit > 100000 else 0
                }

            return {
                "current_investment": current_80c,
                "maximum_limit": max_limit,
                "remaining_limit": remaining_limit,
                "potential_tax_savings": potential_savings,
                "optimal_allocation": optimal_allocation,
                "marginal_tax_rate": marginal_rate
            }

        except Exception as e:
            logger.error(f"Failed to calculate 80C optimization: {str(e)}")
            raise

    # Utility Methods
    def get_tax_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive tax summary for user"""
        try:
            tax_profile = self.get_tax_profile(user_id)
            if not tax_profile:
                return {"error": "Tax profile not found"}

            # Get latest tax calculation
            latest_calculation = self.db.query(TaxCalculation).filter(
                TaxCalculation.tax_profile_id == tax_profile.id
            ).order_by(desc(TaxCalculation.created_at)).first()

            # Get active suggestions
            active_suggestions = self.db.query(TaxOptimizationSuggestion).filter(
                and_(
                    TaxOptimizationSuggestion.tax_profile_id == tax_profile.id,
                    TaxOptimizationSuggestion.is_active == True,
                    TaxOptimizationSuggestion.is_implemented == False
                )
            ).all()

            # Get capital gains
            capital_gains = self.db.query(CapitalGain).filter(
                CapitalGain.tax_profile_id == tax_profile.id
            ).all()

            # Calculate totals
            total_capital_gains = sum(cg.capital_gain_loss for cg in capital_gains if cg.capital_gain_loss > 0)
            total_capital_losses = sum(abs(cg.capital_gain_loss) for cg in capital_gains if cg.capital_gain_loss < 0)
            total_tax_on_gains = sum(cg.tax_on_gain for cg in capital_gains)

            return {
                "tax_profile": {
                    "regime": tax_profile.tax_regime.value,
                    "annual_income": tax_profile.annual_income,
                    "age": tax_profile.age,
                    "is_senior_citizen": tax_profile.is_senior_citizen
                },
                "tax_calculation": {
                    "taxable_income": latest_calculation.taxable_income if latest_calculation else 0,
                    "total_tax": latest_calculation.total_tax if latest_calculation else 0,
                    "old_regime_tax": latest_calculation.old_regime_tax if latest_calculation else 0,
                    "new_regime_tax": latest_calculation.new_regime_tax if latest_calculation else 0,
                    "recommended_regime": latest_calculation.recommended_regime.value if latest_calculation else None,
                    "tax_savings_amount": latest_calculation.tax_savings_amount if latest_calculation else 0
                },
                "deductions": {
                    "section_80c": tax_profile.section_80c_investments,
                    "section_80d": tax_profile.section_80d_premium,
                    "home_loan_interest": tax_profile.home_loan_interest,
                    "education_loan_interest": tax_profile.education_loan_interest
                },
                "capital_gains": {
                    "total_gains": total_capital_gains,
                    "total_losses": total_capital_losses,
                    "net_gains": total_capital_gains - total_capital_losses,
                    "tax_on_gains": total_tax_on_gains,
                    "transactions_count": len(capital_gains)
                },
                "optimization": {
                    "active_suggestions": len(active_suggestions),
                    "potential_savings": sum(s.potential_tax_savings for s in active_suggestions),
                    "high_priority_suggestions": len([s for s in active_suggestions if s.priority == "high"])
                }
            }

        except Exception as e:
            logger.error(f"Failed to get tax summary: {str(e)}")
            raise

    def get_tax_calendar(self, user_id: int) -> List[Dict[str, Any]]:
        """Get tax calendar with important dates and deadlines"""
        try:
            current_year = datetime.now().year

            tax_calendar = [
                {
                    "date": f"{current_year}-03-31",
                    "event": "Financial Year End",
                    "description": "Last date to make tax-saving investments",
                    "priority": "critical",
                    "action_required": True
                },
                {
                    "date": f"{current_year}-07-31",
                    "event": "ITR Filing Deadline",
                    "description": "Last date to file Income Tax Return",
                    "priority": "critical",
                    "action_required": True
                },
                {
                    "date": f"{current_year}-12-31",
                    "event": "Tax Planning Review",
                    "description": "Review and plan tax-saving investments for next year",
                    "priority": "high",
                    "action_required": True
                },
                {
                    "date": f"{current_year}-01-31",
                    "event": "Form 16 Receipt",
                    "description": "Collect Form 16 from employer",
                    "priority": "medium",
                    "action_required": False
                },
                {
                    "date": f"{current_year}-06-30",
                    "event": "Advance Tax Payment",
                    "description": "Pay advance tax if applicable",
                    "priority": "medium",
                    "action_required": False
                }
            ]

            return sorted(tax_calendar, key=lambda x: x["date"])

        except Exception as e:
            logger.error(f"Failed to get tax calendar: {str(e)}")
            return []

    def compare_tax_regimes(self, user_id: int) -> Dict[str, Any]:
        """Compare old vs new tax regime for user"""
        try:
            tax_profile = self.get_tax_profile(user_id)
            if not tax_profile:
                raise ValueError("Tax profile not found")

            # Calculate tax under both regimes
            old_regime_calc = self._calculate_tax_old_regime(tax_profile)
            new_regime_calc = self._calculate_tax_new_regime(tax_profile)

            # Determine better regime
            savings = abs(old_regime_calc["total_tax"] - new_regime_calc["total_tax"])
            better_regime = "old_regime" if old_regime_calc["total_tax"] < new_regime_calc["total_tax"] else "new_regime"

            return {
                "old_regime": {
                    "taxable_income": old_regime_calc["taxable_income"],
                    "total_deductions": old_regime_calc["total_deductions"],
                    "income_tax": old_regime_calc["income_tax"],
                    "total_tax": old_regime_calc["total_tax"],
                    "effective_tax_rate": (old_regime_calc["total_tax"] / tax_profile.annual_income) * 100
                },
                "new_regime": {
                    "taxable_income": new_regime_calc["taxable_income"],
                    "total_deductions": new_regime_calc["total_deductions"],
                    "income_tax": new_regime_calc["income_tax"],
                    "total_tax": new_regime_calc["total_tax"],
                    "effective_tax_rate": (new_regime_calc["total_tax"] / tax_profile.annual_income) * 100
                },
                "comparison": {
                    "better_regime": better_regime,
                    "tax_savings": savings,
                    "savings_percentage": (savings / max(old_regime_calc["total_tax"], new_regime_calc["total_tax"])) * 100,
                    "current_regime": tax_profile.tax_regime.value,
                    "recommendation": "switch" if better_regime != tax_profile.tax_regime.value else "stay"
                }
            }

        except Exception as e:
            logger.error(f"Failed to compare tax regimes: {str(e)}")
            raise
