#!/usr/bin/env python3
"""
Test script for InvestAI AI system
This script tests the AI agents and their functionality
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.ai.crew import InvestAICrew
from app.ai.agents.analyst_agent import FundamentalAnalystAgent
from app.ai.agents.advisor_agent import InvestmentAdvisorAgent
from app.ai.agents.risk_agent import RiskAssessmentAgent
from app.ai.agents.tax_agent import TaxPlanningAgent


def test_fundamental_analyst():
    """Test the Fundamental Analyst Agent"""
    print("🔍 Testing Fundamental Analyst Agent...")
    
    try:
        analyst = FundamentalAnalystAgent()
        
        # Test stock analysis
        print("  📊 Testing stock analysis for RELIANCE...")
        result = analyst.analyze_stock("RELIANCE", "NSE", "comprehensive")
        
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
            return False
        
        print(f"  ✅ Analysis completed for {result.get('symbol', 'RELIANCE')}")
        print(f"  📈 Recommendation: {result.get('recommendation', {}).get('recommendation', 'N/A')}")
        
        # Test mutual fund analysis
        print("  📊 Testing mutual fund analysis...")
        mf_result = analyst.analyze_mutual_fund("12345")
        
        if "error" not in mf_result:
            print(f"  ✅ MF Analysis completed")
            print(f"  📈 MF Recommendation: {mf_result.get('recommendation', {}).get('recommendation', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Fundamental Analyst test failed: {str(e)}")
        return False


def test_investment_advisor():
    """Test the Investment Advisor Agent"""
    print("💼 Testing Investment Advisor Agent...")
    
    try:
        advisor = InvestmentAdvisorAgent()
        
        # Sample user profile
        user_profile = {
            "id": 1,
            "age": 30,
            "annual_income": 1200000,
            "monthly_expenses": 50000,
            "risk_profile": "moderate",
            "investment_experience": "intermediate",
            "investment_horizon_years": 10,
            "current_savings": 500000
        }
        
        # Sample goals
        goals = [
            {
                "name": "Retirement",
                "goal_type": "retirement",
                "target_amount": 10000000,
                "years_to_goal": 30,
                "retirement_age": 60
            }
        ]
        
        # Test investment plan creation
        print("  📋 Testing investment plan creation...")
        plan_result = advisor.create_investment_plan(user_profile, goals)
        
        if "error" in plan_result:
            print(f"  ❌ Error: {plan_result['error']}")
            return False
        
        print(f"  ✅ Investment plan created successfully")
        print(f"  🎯 Plan type: {plan_result.get('plan_type', 'N/A')}")
        
        # Test investment recommendations
        print("  💡 Testing investment recommendations...")
        rec_result = advisor.recommend_investments(user_profile, 100000, "medium_term")
        
        if "error" not in rec_result:
            print(f"  ✅ Investment recommendations generated")
            print(f"  💰 Investment amount: ₹{rec_result.get('investment_amount', 0):,.0f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Investment Advisor test failed: {str(e)}")
        return False


def test_risk_agent():
    """Test the Risk Assessment Agent"""
    print("⚠️  Testing Risk Assessment Agent...")
    
    try:
        risk_agent = RiskAssessmentAgent()
        
        # Sample user profile
        user_profile = {
            "id": 1,
            "age": 35,
            "annual_income": 1000000,
            "monthly_expenses": 40000,
            "current_savings": 300000,
            "investment_experience": "intermediate",
            "investment_horizon_years": 15
        }
        
        # Sample questionnaire responses
        responses = {
            "market_volatility_comfort": 6,
            "loss_tolerance": 5,
            "investment_knowledge_score": 7,
            "risk_return_preference": 6,
            "market_risk_perception": 5,
            "inflation_risk_perception": 6,
            "liquidity_risk_perception": 4,
            "loss_aversion_scenario1": "guaranteed",
            "loss_reaction": "hold"
        }
        
        # Test risk profiling
        print("  📊 Testing risk profiling...")
        profiling_result = risk_agent.conduct_risk_profiling(responses, user_profile)
        
        if "error" in profiling_result:
            print(f"  ❌ Error: {profiling_result['error']}")
            return False
        
        print(f"  ✅ Risk profiling completed")
        overall_profile = profiling_result.get('overall_risk_profile', {})
        print(f"  📈 Risk Profile: {overall_profile.get('overall_risk_profile', 'N/A')}")
        print(f"  📊 Risk Score: {overall_profile.get('risk_score', 0):.1f}")
        
        # Test investment risk analysis
        print("  📊 Testing investment risk analysis...")
        investment_risk = risk_agent.analyze_investment_risk("RELIANCE", "NSE", 100000)
        
        if "error" not in investment_risk:
            print(f"  ✅ Investment risk analysis completed")
            risk_analysis = investment_risk.get('risk_analysis', {})
            print(f"  ⚠️  Risk Category: {risk_analysis.get('risk_category', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Risk Assessment test failed: {str(e)}")
        return False


def test_tax_agent():
    """Test the Tax Planning Agent"""
    print("💰 Testing Tax Planning Agent...")
    
    try:
        tax_agent = TaxPlanningAgent()
        
        # Sample user profile
        user_profile = {
            "id": 1,
            "annual_income": 1500000,
            "tax_bracket": 30,
            "pan_number": "ABCDE1234F",
            "age": 35
        }
        
        # Sample transactions
        transactions = [
            {
                "symbol": "RELIANCE",
                "transaction_type": "buy",
                "quantity": 100,
                "price": 2500,
                "total_amount": 250000,
                "transaction_date": "2024-01-15"
            },
            {
                "symbol": "RELIANCE", 
                "transaction_type": "sell",
                "quantity": 50,
                "price": 2700,
                "total_amount": 135000,
                "transaction_date": "2024-06-15"
            }
        ]
        
        # Test comprehensive tax plan
        print("  📋 Testing comprehensive tax planning...")
        tax_plan = tax_agent.create_comprehensive_tax_plan(user_profile, transactions, "2024-25")
        
        if "error" in tax_plan:
            print(f"  ❌ Error: {tax_plan['error']}")
            return False
        
        print(f"  ✅ Tax plan created for FY {tax_plan.get('financial_year', '2024-25')}")
        
        current_position = tax_plan.get('current_tax_position', {})
        capital_gains = current_position.get('capital_gains', {})
        print(f"  💹 STCG: ₹{capital_gains.get('stcg_total', 0):,.0f}")
        print(f"  💹 LTCG: ₹{capital_gains.get('ltcg_total', 0):,.0f}")
        
        # Test Section 80C planning
        print("  📊 Testing Section 80C planning...")
        section_80c = tax_agent.plan_section_80c_investments(user_profile, {}, "2024-25")
        
        if "error" not in section_80c:
            print(f"  ✅ Section 80C planning completed")
            utilization = section_80c.get('current_utilization', {})
            print(f"  💰 Remaining 80C limit: ₹{utilization.get('remaining_limit', 0):,.0f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Tax Planning test failed: {str(e)}")
        return False


def test_ai_crew():
    """Test the complete AI Crew system"""
    print("🤖 Testing InvestAI Crew System...")
    
    try:
        crew = InvestAICrew()
        
        # Test agent status
        print("  📊 Testing agent status...")
        status = crew.get_agent_status()
        print(f"  ✅ Agent Status: {status}")
        
        # Test available analyses
        analyses = crew.get_available_analyses()
        print(f"  📋 Available Analyses: {len(analyses)} types")
        
        # Sample comprehensive analysis request
        user_profile = {
            "id": 1,
            "age": 32,
            "annual_income": 1200000,
            "risk_profile": "moderate",
            "investment_experience": "intermediate",
            "investment_horizon_years": 10
        }
        
        analysis_request = {
            "request_id": "test_analysis_001",
            "symbol": "TCS",
            "exchange": "NSE",
            "investment_amount": 150000,
            "user_profile": user_profile
        }
        
        # Test comprehensive investment analysis
        print("  🔍 Testing comprehensive investment analysis...")
        analysis_result = crew.comprehensive_investment_analysis(analysis_request)
        
        if "error" in analysis_result:
            print(f"  ❌ Error: {analysis_result['error']}")
            return False
        
        print(f"  ✅ Comprehensive analysis completed for {analysis_result.get('request_details', {}).get('symbol', 'TCS')}")
        
        integrated_rec = analysis_result.get('integrated_recommendations', {})
        print(f"  📈 Overall Recommendation: {integrated_rec.get('overall_recommendation', 'N/A')}")
        print(f"  🎯 Confidence Level: {integrated_rec.get('confidence_level', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI Crew test failed: {str(e)}")
        return False


def main():
    """Run all AI system tests"""
    print("🚀 Starting InvestAI AI System Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run individual agent tests
    test_results.append(("Fundamental Analyst", test_fundamental_analyst()))
    test_results.append(("Investment Advisor", test_investment_advisor()))
    test_results.append(("Risk Assessment", test_risk_agent()))
    test_results.append(("Tax Planning", test_tax_agent()))
    test_results.append(("AI Crew System", test_ai_crew()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI system tests passed successfully!")
        print("🤖 InvestAI AI system is ready for deployment!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
