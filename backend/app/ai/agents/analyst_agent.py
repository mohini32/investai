"""
Fundamental Analyst Agent - Performs comprehensive stock and mutual fund analysis
"""

from crewai import Agent
from typing import Dict, List, Any
from datetime import datetime

from app.ai.tools.market_tools import MarketDataTool, StockAnalysisTool, MutualFundAnalysisTool
from app.ai.tools.analysis_tools import FundamentalAnalysisTool, TechnicalAnalysisTool, RiskAnalysisTool


class FundamentalAnalystAgent:
    """AI Agent specialized in fundamental analysis of stocks and mutual funds"""
    
    def __init__(self):
        self.tools = [
            MarketDataTool(),
            StockAnalysisTool(),
            MutualFundAnalysisTool(),
            FundamentalAnalysisTool(),
            TechnicalAnalysisTool(),
            RiskAnalysisTool()
        ]
        
        self.agent = Agent(
            role="Senior Fundamental Analyst",
            goal="Provide comprehensive fundamental analysis of stocks and mutual funds for Indian markets",
            backstory="""You are a seasoned fundamental analyst with over 15 years of experience in 
            Indian equity markets. You specialize in analyzing companies across various sectors including 
            Technology, Banking, Pharmaceuticals, FMCG, and Infrastructure. Your expertise includes 
            financial statement analysis, business model evaluation, competitive positioning, and 
            valuation assessment. You have a deep understanding of Indian market dynamics, regulatory 
            environment, and macroeconomic factors that impact investments.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    def analyze_stock(self, symbol: str, exchange: str = "NSE", analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Perform comprehensive stock analysis"""
        try:
            analysis_result = {
                "symbol": symbol,
                "exchange": exchange,
                "analysis_type": analysis_type,
                "analyst": "Fundamental Analyst Agent",
                "analysis_date": datetime.now().isoformat(),
                "analysis_components": {}
            }
            
            # Get market data
            market_tool = MarketDataTool()
            market_data = market_tool._run(symbol, exchange)
            analysis_result["market_data"] = market_data
            
            if "error" in market_data:
                return {"error": f"Failed to fetch market data: {market_data['error']}"}
            
            # Perform fundamental analysis
            if analysis_type in ["comprehensive", "fundamental"]:
                fundamental_tool = FundamentalAnalysisTool()
                fundamental_analysis = fundamental_tool._run(symbol, exchange)
                analysis_result["analysis_components"]["fundamental"] = fundamental_analysis
            
            # Perform technical analysis
            if analysis_type in ["comprehensive", "technical"]:
                technical_tool = TechnicalAnalysisTool()
                technical_analysis = technical_tool._run(symbol, exchange)
                analysis_result["analysis_components"]["technical"] = technical_analysis
            
            # Perform risk analysis
            if analysis_type in ["comprehensive", "risk"]:
                risk_tool = RiskAnalysisTool()
                risk_analysis = risk_tool._run(symbol, exchange)
                analysis_result["analysis_components"]["risk"] = risk_analysis
            
            # Generate comprehensive recommendation
            analysis_result["recommendation"] = self._generate_comprehensive_recommendation(analysis_result)
            analysis_result["investment_thesis"] = self._generate_investment_thesis(analysis_result)
            analysis_result["key_metrics"] = self._extract_key_metrics(analysis_result)
            analysis_result["risk_factors"] = self._identify_risk_factors(analysis_result)
            analysis_result["catalysts"] = self._identify_catalysts(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"Stock analysis failed: {str(e)}"}
    
    def analyze_mutual_fund(self, scheme_code: str) -> Dict[str, Any]:
        """Perform comprehensive mutual fund analysis"""
        try:
            analysis_result = {
                "scheme_code": scheme_code,
                "analysis_type": "mutual_fund",
                "analyst": "Fundamental Analyst Agent",
                "analysis_date": datetime.now().isoformat()
            }
            
            # Get mutual fund data and analysis
            mf_tool = MutualFundAnalysisTool()
            mf_analysis = mf_tool._run(scheme_code)
            analysis_result["fund_analysis"] = mf_analysis
            
            if "error" in mf_analysis:
                return {"error": f"Failed to analyze mutual fund: {mf_analysis['error']}"}
            
            # Generate detailed recommendations
            analysis_result["recommendation"] = self._generate_mf_recommendation(mf_analysis)
            analysis_result["suitability"] = self._assess_mf_suitability(mf_analysis)
            analysis_result["comparison"] = self._generate_peer_comparison(mf_analysis)
            analysis_result["investment_strategy"] = self._suggest_investment_strategy(mf_analysis)
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"Mutual fund analysis failed: {str(e)}"}
    
    def compare_investments(self, investments: List[Dict]) -> Dict[str, Any]:
        """Compare multiple investments (stocks/mutual funds)"""
        try:
            comparison_result = {
                "comparison_type": "multi_asset",
                "analyst": "Fundamental Analyst Agent",
                "analysis_date": datetime.now().isoformat(),
                "investments": [],
                "comparison_matrix": {},
                "ranking": []
            }
            
            # Analyze each investment
            for investment in investments:
                if investment.get("type") == "stock":
                    analysis = self.analyze_stock(
                        investment.get("symbol"), 
                        investment.get("exchange", "NSE"),
                        "comprehensive"
                    )
                elif investment.get("type") == "mutual_fund":
                    analysis = self.analyze_mutual_fund(investment.get("scheme_code"))
                else:
                    continue
                
                comparison_result["investments"].append(analysis)
            
            # Generate comparison matrix
            comparison_result["comparison_matrix"] = self._create_comparison_matrix(
                comparison_result["investments"]
            )
            
            # Rank investments
            comparison_result["ranking"] = self._rank_investments(
                comparison_result["investments"]
            )
            
            # Generate comparative insights
            comparison_result["insights"] = self._generate_comparative_insights(
                comparison_result["investments"]
            )
            
            return comparison_result
            
        except Exception as e:
            return {"error": f"Investment comparison failed: {str(e)}"}
    
    def sector_analysis(self, sector: str, top_stocks: int = 5) -> Dict[str, Any]:
        """Perform sector-wide analysis"""
        try:
            # This would typically fetch sector data from a database or API
            # For now, we'll create a mock sector analysis
            
            sector_result = {
                "sector": sector,
                "analysis_type": "sector_analysis",
                "analyst": "Fundamental Analyst Agent",
                "analysis_date": datetime.now().isoformat(),
                "sector_outlook": self._get_sector_outlook(sector),
                "key_trends": self._identify_sector_trends(sector),
                "top_picks": self._get_sector_top_picks(sector, top_stocks),
                "risks": self._identify_sector_risks(sector),
                "opportunities": self._identify_sector_opportunities(sector)
            }
            
            return sector_result
            
        except Exception as e:
            return {"error": f"Sector analysis failed: {str(e)}"}
    
    def _generate_comprehensive_recommendation(self, analysis: Dict) -> Dict[str, Any]:
        """Generate comprehensive investment recommendation"""
        fundamental = analysis.get("analysis_components", {}).get("fundamental", {})
        technical = analysis.get("analysis_components", {}).get("technical", {})
        risk = analysis.get("analysis_components", {}).get("risk", {})
        
        # Extract scores
        fundamental_score = fundamental.get("scores", {}).get("overall_score", 50)
        technical_score = technical.get("technical_score", 50)
        risk_score = risk.get("risk_score", 50)
        
        # Calculate weighted recommendation score
        # Fundamental analysis gets 50% weight, technical 30%, risk 20%
        overall_score = (fundamental_score * 0.5) + (technical_score * 0.3) + ((100 - risk_score) * 0.2)
        
        # Generate recommendation
        if overall_score >= 80:
            recommendation = "STRONG BUY"
            confidence = "High"
        elif overall_score >= 70:
            recommendation = "BUY"
            confidence = "High"
        elif overall_score >= 60:
            recommendation = "MODERATE BUY"
            confidence = "Medium"
        elif overall_score >= 50:
            recommendation = "HOLD"
            confidence = "Medium"
        elif overall_score >= 40:
            recommendation = "WEAK HOLD"
            confidence = "Low"
        else:
            recommendation = "SELL"
            confidence = "High"
        
        return {
            "recommendation": recommendation,
            "overall_score": overall_score,
            "confidence_level": confidence,
            "time_horizon": self._suggest_time_horizon(overall_score, risk_score),
            "target_price": self._calculate_target_price(analysis),
            "stop_loss": self._calculate_stop_loss(analysis),
            "rationale": self._generate_recommendation_rationale(analysis, overall_score)
        }
    
    def _generate_investment_thesis(self, analysis: Dict) -> str:
        """Generate investment thesis"""
        symbol = analysis.get("symbol", "Stock")
        fundamental = analysis.get("analysis_components", {}).get("fundamental", {})
        
        # Extract key information
        company_name = fundamental.get("business_moat", {}).get("sector", "Company")
        sector = fundamental.get("business_moat", {}).get("sector", "Unknown")
        recommendation = analysis.get("recommendation", {}).get("recommendation", "HOLD")
        
        thesis = f"""
        Investment Thesis for {symbol}:
        
        {company_name} operates in the {sector} sector and presents a {recommendation.lower()} opportunity 
        based on our comprehensive analysis. The company demonstrates strong fundamentals with 
        competitive positioning in its market segment.
        
        Key investment highlights include solid financial metrics, reasonable valuation, 
        and positive business outlook. However, investors should consider the associated 
        risks and market volatility before making investment decisions.
        
        This analysis is based on current market conditions and available financial data.
        """
        
        return thesis.strip()
    
    def _extract_key_metrics(self, analysis: Dict) -> Dict[str, Any]:
        """Extract key financial metrics"""
        market_data = analysis.get("market_data", {})
        fundamental = analysis.get("analysis_components", {}).get("fundamental", {})
        
        return {
            "current_price": market_data.get("current_price"),
            "market_cap": market_data.get("market_cap"),
            "pe_ratio": market_data.get("pe_ratio"),
            "pb_ratio": market_data.get("pb_ratio"),
            "dividend_yield": market_data.get("dividend_yield"),
            "roe": fundamental.get("profitability", {}).get("roe"),
            "debt_to_equity": fundamental.get("financial_health", {}).get("debt_to_equity"),
            "revenue_growth": fundamental.get("growth", {}).get("revenue_growth")
        }
    
    def _identify_risk_factors(self, analysis: Dict) -> List[str]:
        """Identify key risk factors"""
        risk_factors = []
        
        fundamental = analysis.get("analysis_components", {}).get("fundamental", {})
        risk = analysis.get("analysis_components", {}).get("risk", {})
        
        # Financial health risks
        health = fundamental.get("financial_health", {})
        if health.get("debt_to_equity", 0) > 1.0:
            risk_factors.append("High debt-to-equity ratio indicates financial leverage risk")
        
        # Valuation risks
        valuation = fundamental.get("valuation", {})
        if valuation.get("valuation_score", 100) < 40:
            risk_factors.append("Stock appears overvalued based on current metrics")
        
        # Market risks
        risk_score = risk.get("risk_score", 50)
        if risk_score > 70:
            risk_factors.append("High volatility and market risk")
        
        # Sector-specific risks
        sector = fundamental.get("business_moat", {}).get("sector", "")
        if sector in ["Banking", "Real Estate"]:
            risk_factors.append("Sector is sensitive to interest rate changes")
        
        return risk_factors
    
    def _identify_catalysts(self, analysis: Dict) -> List[str]:
        """Identify potential catalysts"""
        catalysts = []
        
        fundamental = analysis.get("analysis_components", {}).get("fundamental", {})
        
        # Growth catalysts
        growth = fundamental.get("growth", {})
        if growth.get("growth_score", 0) > 70:
            catalysts.append("Strong revenue and earnings growth trajectory")
        
        # Industry catalysts
        sector = fundamental.get("business_moat", {}).get("sector", "")
        if sector == "Technology":
            catalysts.append("Digital transformation and technology adoption trends")
        elif sector == "Pharmaceuticals":
            catalysts.append("New product launches and regulatory approvals")
        elif sector == "Infrastructure":
            catalysts.append("Government infrastructure spending and policy support")
        
        # Market catalysts
        catalysts.append("Potential inclusion in major indices")
        catalysts.append("Institutional investor interest and coverage")
        
        return catalysts
    
    def _generate_mf_recommendation(self, mf_analysis: Dict) -> Dict[str, Any]:
        """Generate mutual fund recommendation"""
        returns_1y = mf_analysis.get("returns_1y", 0)
        expense_ratio = mf_analysis.get("expense_ratio", 2.0)
        risk_score = mf_analysis.get("risk_score", 50)
        
        # Calculate recommendation score
        score = 50
        score += min(30, returns_1y * 1.5)  # Returns contribution
        score -= expense_ratio * 10  # Expense penalty
        score -= risk_score * 0.3  # Risk penalty
        
        if score >= 75:
            recommendation = "STRONG BUY"
        elif score >= 65:
            recommendation = "BUY"
        elif score >= 55:
            recommendation = "HOLD"
        else:
            recommendation = "AVOID"
        
        return {
            "recommendation": recommendation,
            "score": score,
            "rationale": f"Based on {returns_1y:.1f}% annual returns, {expense_ratio:.2f}% expense ratio, and risk assessment"
        }
    
    def _assess_mf_suitability(self, mf_analysis: Dict) -> Dict[str, str]:
        """Assess mutual fund suitability for different investor types"""
        category = mf_analysis.get("category", "")
        risk_score = mf_analysis.get("risk_score", 50)
        
        suitability = {}
        
        if "Equity" in category:
            if risk_score < 40:
                suitability["conservative"] = "Not Suitable"
                suitability["moderate"] = "Suitable"
                suitability["aggressive"] = "Highly Suitable"
            else:
                suitability["conservative"] = "Not Suitable"
                suitability["moderate"] = "Moderately Suitable"
                suitability["aggressive"] = "Suitable"
        else:
            suitability["conservative"] = "Suitable"
            suitability["moderate"] = "Suitable"
            suitability["aggressive"] = "Moderately Suitable"
        
        return suitability
    
    def _generate_peer_comparison(self, mf_analysis: Dict) -> Dict[str, Any]:
        """Generate peer comparison for mutual fund"""
        # This would typically compare with similar funds
        return {
            "peer_ranking": "Top Quartile",
            "vs_category_average": "+2.5%",
            "vs_benchmark": "+1.8%",
            "expense_ratio_ranking": "Below Average"
        }
    
    def _suggest_investment_strategy(self, mf_analysis: Dict) -> Dict[str, Any]:
        """Suggest investment strategy for mutual fund"""
        category = mf_analysis.get("category", "")
        
        if "Equity" in category:
            return {
                "investment_mode": "SIP",
                "recommended_tenure": "5+ years",
                "allocation": "Core holding for equity portfolio",
                "timing": "Any time for SIP, lump sum during market corrections"
            }
        else:
            return {
                "investment_mode": "Lump sum or SIP",
                "recommended_tenure": "1-3 years",
                "allocation": "Debt component of portfolio",
                "timing": "Any time"
            }
    
    # Helper methods for sector analysis
    def _get_sector_outlook(self, sector: str) -> str:
        """Get sector outlook"""
        outlooks = {
            "Technology": "Positive - Digital transformation driving growth",
            "Banking": "Cautious - Credit growth offset by asset quality concerns",
            "Pharmaceuticals": "Positive - Strong domestic and export demand",
            "FMCG": "Stable - Steady demand with margin pressures",
            "Automobile": "Recovery - Gradual improvement in demand"
        }
        return outlooks.get(sector, "Neutral outlook")
    
    def _identify_sector_trends(self, sector: str) -> List[str]:
        """Identify sector trends"""
        trends = {
            "Technology": ["Cloud adoption", "AI/ML integration", "Digital payments growth"],
            "Banking": ["Digital banking", "Credit growth recovery", "Asset quality improvement"],
            "Pharmaceuticals": ["Generic drug exports", "Biosimilar opportunities", "API manufacturing"],
            "FMCG": ["Rural demand recovery", "Premium product growth", "E-commerce expansion"],
            "Automobile": ["Electric vehicle adoption", "Semiconductor shortage recovery", "Export growth"]
        }
        return trends.get(sector, ["Industry consolidation", "Technology adoption", "Regulatory changes"])
    
    def _get_sector_top_picks(self, sector: str, count: int) -> List[str]:
        """Get sector top picks (mock data)"""
        picks = {
            "Technology": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
            "Banking": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK", "SBIN"],
            "Pharmaceuticals": ["SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "BIOCON"],
            "FMCG": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR"],
            "Automobile": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "HEROMOTOCO"]
        }
        return picks.get(sector, ["STOCK1", "STOCK2", "STOCK3"])[:count]
    
    def _identify_sector_risks(self, sector: str) -> List[str]:
        """Identify sector risks"""
        risks = {
            "Technology": ["Client concentration", "Visa restrictions", "Currency fluctuation"],
            "Banking": ["Asset quality", "Interest rate sensitivity", "Regulatory changes"],
            "Pharmaceuticals": ["Regulatory approvals", "Price controls", "Competition"],
            "FMCG": ["Raw material inflation", "Rural demand slowdown", "Competition"],
            "Automobile": ["Commodity price volatility", "Regulatory changes", "Economic slowdown"]
        }
        return risks.get(sector, ["Market volatility", "Regulatory changes", "Economic factors"])
    
    def _identify_sector_opportunities(self, sector: str) -> List[str]:
        """Identify sector opportunities"""
        opportunities = {
            "Technology": ["Digital transformation", "Cloud migration", "AI adoption"],
            "Banking": ["Financial inclusion", "Digital payments", "Credit growth"],
            "Pharmaceuticals": ["Export opportunities", "Biosimilars", "Contract manufacturing"],
            "FMCG": ["Rural penetration", "Premium products", "Health and wellness"],
            "Automobile": ["Electric vehicles", "Export markets", "Premiumization"]
        }
        return opportunities.get(sector, ["Market expansion", "Innovation", "Efficiency improvements"])
    
    # Additional helper methods
    def _create_comparison_matrix(self, investments: List[Dict]) -> Dict[str, Any]:
        """Create comparison matrix for investments"""
        # This would create a detailed comparison matrix
        return {"matrix": "Comparison matrix would be generated here"}
    
    def _rank_investments(self, investments: List[Dict]) -> List[Dict]:
        """Rank investments based on analysis"""
        # This would rank investments based on various criteria
        return [{"rank": 1, "symbol": "EXAMPLE", "score": 85}]
    
    def _generate_comparative_insights(self, investments: List[Dict]) -> List[str]:
        """Generate comparative insights"""
        return ["Comparative insights would be generated here"]
    
    def _suggest_time_horizon(self, overall_score: float, risk_score: float) -> str:
        """Suggest investment time horizon"""
        if risk_score > 70:
            return "Long-term (3+ years)"
        elif overall_score > 70:
            return "Medium to Long-term (2-5 years)"
        else:
            return "Short to Medium-term (1-3 years)"
    
    def _calculate_target_price(self, analysis: Dict) -> Optional[float]:
        """Calculate target price"""
        market_data = analysis.get("market_data", {})
        current_price = market_data.get("current_price")
        
        if current_price:
            # Simple target price calculation (10-20% upside)
            return current_price * 1.15
        return None
    
    def _calculate_stop_loss(self, analysis: Dict) -> Optional[float]:
        """Calculate stop loss"""
        market_data = analysis.get("market_data", {})
        current_price = market_data.get("current_price")
        
        if current_price:
            # Simple stop loss calculation (10% downside)
            return current_price * 0.90
        return None
    
    def _generate_recommendation_rationale(self, analysis: Dict, score: float) -> str:
        """Generate rationale for recommendation"""
        return f"Recommendation based on comprehensive analysis with overall score of {score:.1f}. " \
               f"Consider fundamental strengths, technical indicators, and risk factors before investing."
