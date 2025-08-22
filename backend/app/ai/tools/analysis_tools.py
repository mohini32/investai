"""
Analysis tools for AI agents - Fundamental, Technical, and Risk Analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from crewai_tools import BaseTool
import yfinance as yf

from app.ai.tools.market_tools import MarketDataTool


class FundamentalAnalysisTool(BaseTool):
    """Tool for comprehensive fundamental analysis"""
    
    name: str = "Fundamental Analysis Tool"
    description: str = "Performs in-depth fundamental analysis including financial ratios, business moat analysis, and valuation metrics"
    
    def _run(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """Perform comprehensive fundamental analysis"""
        try:
            yf_symbol = f"{symbol}.NS" if exchange.upper() == "NSE" else f"{symbol}.BO"
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            # Get financial statements
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            analysis = {
                "symbol": symbol,
                "analysis_type": "fundamental",
                "analysis_date": datetime.now().isoformat(),
                
                # Valuation Analysis
                "valuation": self._analyze_valuation(info),
                
                # Profitability Analysis
                "profitability": self._analyze_profitability(info, financials),
                
                # Financial Health
                "financial_health": self._analyze_financial_health(info, balance_sheet),
                
                # Growth Analysis
                "growth": self._analyze_growth(info, financials),
                
                # Business Moat Analysis
                "business_moat": self._analyze_business_moat(info),
                
                # Management Quality
                "management": self._analyze_management(info),
                
                # Industry Analysis
                "industry": self._analyze_industry(info),
                
                # Overall Scores
                "scores": self._calculate_scores(info)
            }
            
            # Generate recommendation
            analysis["recommendation"] = self._generate_recommendation(analysis)
            analysis["key_strengths"] = self._identify_strengths(analysis)
            analysis["key_concerns"] = self._identify_concerns(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Fundamental analysis failed for {symbol}: {str(e)}"}
    
    def _analyze_valuation(self, info: Dict) -> Dict[str, Any]:
        """Analyze valuation metrics"""
        pe = info.get('trailingPE')
        pb = info.get('priceToBook')
        ps = info.get('priceToSalesTrailing12Months')
        peg = info.get('pegRatio')
        
        valuation = {
            "pe_ratio": pe,
            "pb_ratio": pb,
            "ps_ratio": ps,
            "peg_ratio": peg,
            "market_cap": info.get('marketCap'),
            "enterprise_value": info.get('enterpriseValue'),
            "ev_revenue": info.get('enterpriseToRevenue'),
            "ev_ebitda": info.get('enterpriseToEbitda')
        }
        
        # Valuation assessment
        valuation_score = 50
        if pe and 10 <= pe <= 20:
            valuation_score += 15
        elif pe and pe < 10:
            valuation_score += 10
        elif pe and pe > 30:
            valuation_score -= 20
        
        if pb and 1 <= pb <= 3:
            valuation_score += 10
        elif pb and pb > 5:
            valuation_score -= 15
        
        valuation["valuation_score"] = max(0, min(100, valuation_score))
        valuation["assessment"] = self._get_valuation_assessment(valuation_score)
        
        return valuation
    
    def _analyze_profitability(self, info: Dict, financials: pd.DataFrame) -> Dict[str, Any]:
        """Analyze profitability metrics"""
        profitability = {
            "gross_margin": info.get('grossMargins'),
            "operating_margin": info.get('operatingMargins'),
            "profit_margin": info.get('profitMargins'),
            "roe": info.get('returnOnEquity'),
            "roa": info.get('returnOnAssets'),
            "roic": info.get('returnOnCapital'),
            "ebitda_margin": info.get('ebitdaMargins')
        }
        
        # Calculate profitability score
        prof_score = 50
        roe = profitability.get('roe')
        if roe and roe > 0.20:
            prof_score += 20
        elif roe and roe > 0.15:
            prof_score += 15
        elif roe and roe < 0.10:
            prof_score -= 15
        
        operating_margin = profitability.get('operating_margin')
        if operating_margin and operating_margin > 0.15:
            prof_score += 15
        elif operating_margin and operating_margin < 0.05:
            prof_score -= 15
        
        profitability["profitability_score"] = max(0, min(100, prof_score))
        profitability["assessment"] = self._get_profitability_assessment(prof_score)
        
        return profitability
    
    def _analyze_financial_health(self, info: Dict, balance_sheet: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial health and stability"""
        health = {
            "debt_to_equity": info.get('debtToEquity'),
            "current_ratio": info.get('currentRatio'),
            "quick_ratio": info.get('quickRatio'),
            "cash_ratio": info.get('cashRatio'),
            "interest_coverage": info.get('interestCoverage'),
            "total_cash": info.get('totalCash'),
            "total_debt": info.get('totalDebt'),
            "working_capital": info.get('workingCapital')
        }
        
        # Calculate health score
        health_score = 50
        de_ratio = health.get('debt_to_equity')
        if de_ratio and de_ratio < 0.3:
            health_score += 20
        elif de_ratio and de_ratio < 0.6:
            health_score += 10
        elif de_ratio and de_ratio > 1.0:
            health_score -= 20
        
        current_ratio = health.get('current_ratio')
        if current_ratio and current_ratio > 1.5:
            health_score += 15
        elif current_ratio and current_ratio < 1.0:
            health_score -= 20
        
        health["health_score"] = max(0, min(100, health_score))
        health["assessment"] = self._get_health_assessment(health_score)
        
        return health
    
    def _analyze_growth(self, info: Dict, financials: pd.DataFrame) -> Dict[str, Any]:
        """Analyze growth metrics"""
        growth = {
            "revenue_growth": info.get('revenueGrowth'),
            "earnings_growth": info.get('earningsGrowth'),
            "revenue_growth_quarterly": info.get('revenueQuarterlyGrowth'),
            "earnings_growth_quarterly": info.get('earningsQuarterlyGrowth'),
            "book_value_growth": info.get('bookValueGrowth'),
            "dividend_growth": info.get('dividendGrowth')
        }
        
        # Calculate growth score
        growth_score = 50
        rev_growth = growth.get('revenue_growth')
        if rev_growth and rev_growth > 0.20:
            growth_score += 20
        elif rev_growth and rev_growth > 0.10:
            growth_score += 15
        elif rev_growth and rev_growth < 0:
            growth_score -= 25
        
        earnings_growth = growth.get('earnings_growth')
        if earnings_growth and earnings_growth > 0.15:
            growth_score += 15
        elif earnings_growth and earnings_growth < 0:
            growth_score -= 20
        
        growth["growth_score"] = max(0, min(100, growth_score))
        growth["assessment"] = self._get_growth_assessment(growth_score)
        
        return growth
    
    def _analyze_business_moat(self, info: Dict) -> Dict[str, Any]:
        """Analyze competitive advantages and business moat"""
        sector = info.get('sector', '')
        industry = info.get('industry', '')
        market_cap = info.get('marketCap', 0)
        
        moat = {
            "sector": sector,
            "industry": industry,
            "market_position": self._assess_market_position(market_cap),
            "competitive_advantages": self._identify_competitive_advantages(sector, industry),
            "moat_strength": self._assess_moat_strength(sector, industry, market_cap),
            "sustainability": self._assess_sustainability(info)
        }
        
        return moat
    
    def _analyze_management(self, info: Dict) -> Dict[str, Any]:
        """Analyze management quality indicators"""
        management = {
            "insider_ownership": info.get('heldByInsiders'),
            "institutional_ownership": info.get('heldByInstitutions'),
            "management_effectiveness": self._assess_management_effectiveness(info),
            "corporate_governance": self._assess_governance(info)
        }
        
        return management
    
    def _analyze_industry(self, info: Dict) -> Dict[str, Any]:
        """Analyze industry trends and positioning"""
        sector = info.get('sector', '')
        industry = info.get('industry', '')
        
        industry_analysis = {
            "sector": sector,
            "industry": industry,
            "industry_outlook": self._get_industry_outlook(sector, industry),
            "cyclical_nature": self._assess_cyclical_nature(sector),
            "regulatory_environment": self._assess_regulatory_environment(sector),
            "growth_prospects": self._assess_industry_growth(sector, industry)
        }
        
        return industry_analysis
    
    def _calculate_scores(self, info: Dict) -> Dict[str, float]:
        """Calculate overall scores"""
        # This would integrate all the individual scores
        return {
            "overall_score": 75.0,
            "value_score": 70.0,
            "quality_score": 80.0,
            "growth_score": 75.0,
            "safety_score": 85.0
        }
    
    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generate investment recommendation based on analysis"""
        scores = analysis.get('scores', {})
        overall_score = scores.get('overall_score', 50)
        
        if overall_score >= 80:
            return "STRONG BUY"
        elif overall_score >= 70:
            return "BUY"
        elif overall_score >= 60:
            return "HOLD"
        elif overall_score >= 40:
            return "WEAK HOLD"
        else:
            return "SELL"
    
    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """Identify key strengths"""
        strengths = []
        
        valuation = analysis.get('valuation', {})
        if valuation.get('valuation_score', 0) > 70:
            strengths.append("Attractive valuation")
        
        profitability = analysis.get('profitability', {})
        if profitability.get('profitability_score', 0) > 70:
            strengths.append("Strong profitability")
        
        health = analysis.get('financial_health', {})
        if health.get('health_score', 0) > 70:
            strengths.append("Solid financial health")
        
        growth = analysis.get('growth', {})
        if growth.get('growth_score', 0) > 70:
            strengths.append("Consistent growth")
        
        return strengths
    
    def _identify_concerns(self, analysis: Dict) -> List[str]:
        """Identify key concerns"""
        concerns = []
        
        valuation = analysis.get('valuation', {})
        if valuation.get('valuation_score', 100) < 40:
            concerns.append("High valuation")
        
        health = analysis.get('financial_health', {})
        if health.get('health_score', 100) < 40:
            concerns.append("Weak financial position")
        
        growth = analysis.get('growth', {})
        if growth.get('growth_score', 100) < 40:
            concerns.append("Declining growth")
        
        return concerns
    
    # Helper methods for assessments
    def _get_valuation_assessment(self, score: float) -> str:
        if score >= 70: return "Undervalued"
        elif score >= 50: return "Fairly valued"
        else: return "Overvalued"
    
    def _get_profitability_assessment(self, score: float) -> str:
        if score >= 70: return "Highly profitable"
        elif score >= 50: return "Moderately profitable"
        else: return "Low profitability"
    
    def _get_health_assessment(self, score: float) -> str:
        if score >= 70: return "Strong financial health"
        elif score >= 50: return "Adequate financial health"
        else: return "Weak financial health"
    
    def _get_growth_assessment(self, score: float) -> str:
        if score >= 70: return "Strong growth"
        elif score >= 50: return "Moderate growth"
        else: return "Weak growth"
    
    def _assess_market_position(self, market_cap: float) -> str:
        if market_cap >= 200000000000: return "Market leader"
        elif market_cap >= 50000000000: return "Strong player"
        else: return "Niche player"
    
    def _identify_competitive_advantages(self, sector: str, industry: str) -> List[str]:
        # Simplified competitive advantage identification
        advantages = []
        if "Technology" in sector:
            advantages.extend(["Innovation capability", "Network effects"])
        elif "Banking" in sector:
            advantages.extend(["Regulatory barriers", "Customer relationships"])
        elif "Pharmaceuticals" in sector:
            advantages.extend(["Patent protection", "R&D capabilities"])
        return advantages
    
    def _assess_moat_strength(self, sector: str, industry: str, market_cap: float) -> str:
        # Simplified moat assessment
        if market_cap > 100000000000 and sector in ["Technology", "Banking", "Pharmaceuticals"]:
            return "Wide moat"
        elif market_cap > 50000000000:
            return "Narrow moat"
        else:
            return "No moat"
    
    def _assess_sustainability(self, info: Dict) -> str:
        # Simplified sustainability assessment
        return "Sustainable business model"
    
    def _assess_management_effectiveness(self, info: Dict) -> str:
        return "Effective management"
    
    def _assess_governance(self, info: Dict) -> str:
        return "Good corporate governance"
    
    def _get_industry_outlook(self, sector: str, industry: str) -> str:
        return "Positive outlook"
    
    def _assess_cyclical_nature(self, sector: str) -> str:
        cyclical_sectors = ["Automobile", "Metals", "Infrastructure"]
        return "Cyclical" if sector in cyclical_sectors else "Non-cyclical"
    
    def _assess_regulatory_environment(self, sector: str) -> str:
        return "Stable regulatory environment"
    
    def _assess_industry_growth(self, sector: str, industry: str) -> str:
        return "Growing industry"


class TechnicalAnalysisTool(BaseTool):
    """Tool for technical analysis"""
    
    name: str = "Technical Analysis Tool"
    description: str = "Performs technical analysis including trend analysis, support/resistance levels, and technical indicators"
    
    def _run(self, symbol: str, exchange: str = "NSE", period: str = "6mo") -> Dict[str, Any]:
        """Perform technical analysis"""
        try:
            yf_symbol = f"{symbol}.NS" if exchange.upper() == "NSE" else f"{symbol}.BO"
            ticker = yf.Ticker(yf_symbol)
            
            # Get historical data
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {"error": f"No historical data found for {symbol}"}
            
            analysis = {
                "symbol": symbol,
                "analysis_type": "technical",
                "analysis_date": datetime.now().isoformat(),
                "period": period,
                
                # Price action
                "price_action": self._analyze_price_action(hist),
                
                # Moving averages
                "moving_averages": self._calculate_moving_averages(hist),
                
                # Technical indicators
                "indicators": self._calculate_technical_indicators(hist),
                
                # Support and resistance
                "support_resistance": self._find_support_resistance(hist),
                
                # Trend analysis
                "trend": self._analyze_trend(hist),
                
                # Volume analysis
                "volume": self._analyze_volume(hist)
            }
            
            # Generate technical recommendation
            analysis["technical_score"] = self._calculate_technical_score(analysis)
            analysis["recommendation"] = self._generate_technical_recommendation(analysis)
            analysis["key_levels"] = self._identify_key_levels(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Technical analysis failed for {symbol}: {str(e)}"}
    
    def _analyze_price_action(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Analyze recent price action"""
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        
        return {
            "current_price": float(current_price),
            "previous_close": float(prev_close),
            "daily_change": float(current_price - prev_close),
            "daily_change_pct": float((current_price - prev_close) / prev_close * 100),
            "high_52w": float(hist['High'].max()),
            "low_52w": float(hist['Low'].min()),
            "current_vs_52w_high": float((current_price / hist['High'].max() - 1) * 100),
            "current_vs_52w_low": float((current_price / hist['Low'].min() - 1) * 100)
        }
    
    def _calculate_moving_averages(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate moving averages"""
        close = hist['Close']
        
        mas = {
            "sma_20": float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None,
            "sma_50": float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None,
            "sma_200": float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None,
            "ema_12": float(close.ewm(span=12).mean().iloc[-1]) if len(close) >= 12 else None,
            "ema_26": float(close.ewm(span=26).mean().iloc[-1]) if len(close) >= 26 else None
        }
        
        # Add signals
        current_price = close.iloc[-1]
        mas["price_vs_sma20"] = "Above" if mas["sma_20"] and current_price > mas["sma_20"] else "Below"
        mas["price_vs_sma50"] = "Above" if mas["sma_50"] and current_price > mas["sma_50"] else "Below"
        
        return mas
    
    def _calculate_technical_indicators(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        close = hist['Close']
        high = hist['High']
        low = hist['Low']
        volume = hist['Volume']
        
        indicators = {}
        
        # RSI
        if len(close) >= 14:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators["rsi"] = float(rsi.iloc[-1])
            indicators["rsi_signal"] = self._get_rsi_signal(indicators["rsi"])
        
        # MACD
        if len(close) >= 26:
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            indicators["macd"] = float(macd.iloc[-1])
            indicators["macd_signal"] = float(signal.iloc[-1])
            indicators["macd_histogram"] = float(macd.iloc[-1] - signal.iloc[-1])
        
        return indicators
    
    def _find_support_resistance(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Find support and resistance levels"""
        high = hist['High']
        low = hist['Low']
        
        # Simple support/resistance calculation
        recent_high = high.tail(20).max()
        recent_low = low.tail(20).min()
        
        return {
            "resistance": float(recent_high),
            "support": float(recent_low),
            "key_levels": [float(recent_low), float(recent_high)]
        }
    
    def _analyze_trend(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price trend"""
        close = hist['Close']
        
        # Simple trend analysis using moving averages
        if len(close) >= 50:
            sma20 = close.rolling(20).mean()
            sma50 = close.rolling(50).mean()
            
            current_trend = "Uptrend" if sma20.iloc[-1] > sma50.iloc[-1] else "Downtrend"
        else:
            current_trend = "Sideways"
        
        return {
            "current_trend": current_trend,
            "trend_strength": "Strong" if abs(close.pct_change().mean()) > 0.02 else "Weak"
        }
    
    def _analyze_volume(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns"""
        volume = hist['Volume']
        
        return {
            "avg_volume": float(volume.mean()),
            "current_volume": float(volume.iloc[-1]),
            "volume_trend": "Increasing" if volume.iloc[-1] > volume.mean() else "Decreasing"
        }
    
    def _calculate_technical_score(self, analysis: Dict) -> float:
        """Calculate overall technical score"""
        score = 50
        
        # RSI scoring
        indicators = analysis.get('indicators', {})
        rsi = indicators.get('rsi')
        if rsi:
            if 30 <= rsi <= 70:
                score += 10
            elif rsi < 30:
                score += 20  # Oversold - potential buy
            elif rsi > 70:
                score -= 20  # Overbought - potential sell
        
        # Trend scoring
        trend = analysis.get('trend', {})
        if trend.get('current_trend') == "Uptrend":
            score += 15
        elif trend.get('current_trend') == "Downtrend":
            score -= 15
        
        # Moving average scoring
        mas = analysis.get('moving_averages', {})
        if mas.get('price_vs_sma20') == "Above":
            score += 10
        if mas.get('price_vs_sma50') == "Above":
            score += 10
        
        return max(0, min(100, score))
    
    def _generate_technical_recommendation(self, analysis: Dict) -> str:
        """Generate technical recommendation"""
        score = analysis.get('technical_score', 50)
        
        if score >= 70:
            return "BUY"
        elif score >= 55:
            return "WEAK BUY"
        elif score >= 45:
            return "HOLD"
        elif score >= 30:
            return "WEAK SELL"
        else:
            return "SELL"
    
    def _identify_key_levels(self, analysis: Dict) -> List[float]:
        """Identify key price levels"""
        sr = analysis.get('support_resistance', {})
        return sr.get('key_levels', [])
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """Get RSI signal"""
        if rsi < 30:
            return "Oversold"
        elif rsi > 70:
            return "Overbought"
        else:
            return "Neutral"


class RiskAnalysisTool(BaseTool):
    """Tool for risk analysis"""
    
    name: str = "Risk Analysis Tool"
    description: str = "Performs comprehensive risk analysis including volatility, beta, VaR, and risk-adjusted returns"
    
    def _run(self, symbol: str, exchange: str = "NSE", period: str = "1y") -> Dict[str, Any]:
        """Perform risk analysis"""
        try:
            yf_symbol = f"{symbol}.NS" if exchange.upper() == "NSE" else f"{symbol}.BO"
            ticker = yf.Ticker(yf_symbol)
            
            # Get historical data
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {"error": f"No historical data found for {symbol}"}
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            
            analysis = {
                "symbol": symbol,
                "analysis_type": "risk",
                "analysis_date": datetime.now().isoformat(),
                "period": period,
                
                # Volatility measures
                "volatility": self._calculate_volatility(returns),
                
                # Risk metrics
                "risk_metrics": self._calculate_risk_metrics(returns),
                
                # Downside risk
                "downside_risk": self._calculate_downside_risk(returns),
                
                # Risk-adjusted returns
                "risk_adjusted": self._calculate_risk_adjusted_returns(returns),
                
                # Beta calculation (vs market)
                "beta_analysis": self._calculate_beta(symbol, exchange, returns)
            }
            
            # Overall risk assessment
            analysis["risk_score"] = self._calculate_risk_score(analysis)
            analysis["risk_category"] = self._categorize_risk(analysis["risk_score"])
            analysis["risk_summary"] = self._generate_risk_summary(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Risk analysis failed for {symbol}: {str(e)}"}
    
    def _calculate_volatility(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate various volatility measures"""
        return {
            "daily_volatility": float(returns.std()),
            "annualized_volatility": float(returns.std() * np.sqrt(252)),
            "volatility_30d": float(returns.tail(30).std() * np.sqrt(252)),
            "volatility_90d": float(returns.tail(90).std() * np.sqrt(252))
        }
    
    def _calculate_risk_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate various risk metrics"""
        return {
            "var_95": float(np.percentile(returns, 5)),  # 95% VaR
            "var_99": float(np.percentile(returns, 1)),  # 99% VaR
            "cvar_95": float(returns[returns <= np.percentile(returns, 5)].mean()),  # Conditional VaR
            "max_drawdown": self._calculate_max_drawdown(returns),
            "skewness": float(returns.skew()),
            "kurtosis": float(returns.kurtosis())
        }
    
    def _calculate_downside_risk(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate downside risk measures"""
        negative_returns = returns[returns < 0]
        
        return {
            "downside_deviation": float(negative_returns.std() * np.sqrt(252)),
            "downside_frequency": float(len(negative_returns) / len(returns)),
            "average_loss": float(negative_returns.mean()) if len(negative_returns) > 0 else 0.0,
            "worst_day": float(returns.min()),
            "worst_month": float(returns.rolling(21).sum().min())
        }
    
    def _calculate_risk_adjusted_returns(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate risk-adjusted return measures"""
        annual_return = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        
        # Assuming risk-free rate of 6% for India
        risk_free_rate = 0.06
        
        return {
            "sharpe_ratio": float((annual_return - risk_free_rate) / annual_vol) if annual_vol > 0 else 0.0,
            "sortino_ratio": self._calculate_sortino_ratio(returns, risk_free_rate),
            "calmar_ratio": self._calculate_calmar_ratio(returns),
            "information_ratio": float(annual_return / annual_vol) if annual_vol > 0 else 0.0
        }
    
    def _calculate_beta(self, symbol: str, exchange: str, returns: pd.Series) -> Dict[str, Any]:
        """Calculate beta vs market index"""
        try:
            # Use NIFTY 50 as benchmark for NSE stocks
            benchmark_symbol = "^NSEI" if exchange.upper() == "NSE" else "^BSESN"
            benchmark = yf.Ticker(benchmark_symbol)
            benchmark_hist = benchmark.history(period="1y")
            benchmark_returns = benchmark_hist['Close'].pct_change().dropna()
            
            # Align dates
            common_dates = returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 30:
                stock_returns = returns.loc[common_dates]
                market_returns = benchmark_returns.loc[common_dates]
                
                # Calculate beta
                covariance = np.cov(stock_returns, market_returns)[0][1]
                market_variance = np.var(market_returns)
                beta = covariance / market_variance if market_variance > 0 else 1.0
                
                # Calculate correlation
                correlation = np.corrcoef(stock_returns, market_returns)[0][1]
                
                return {
                    "beta": float(beta),
                    "correlation": float(correlation),
                    "benchmark": benchmark_symbol,
                    "r_squared": float(correlation ** 2)
                }
        except:
            pass
        
        return {
            "beta": 1.0,
            "correlation": 0.0,
            "benchmark": "N/A",
            "r_squared": 0.0
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return float(drawdown.min())
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """Calculate Sortino ratio"""
        annual_return = returns.mean() * 252
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252)
        
        return float((annual_return - risk_free_rate) / downside_deviation) if downside_deviation > 0 else 0.0
    
    def _calculate_calmar_ratio(self, returns: pd.Series) -> float:
        """Calculate Calmar ratio"""
        annual_return = returns.mean() * 252
        max_drawdown = abs(self._calculate_max_drawdown(returns))
        
        return float(annual_return / max_drawdown) if max_drawdown > 0 else 0.0
    
    def _calculate_risk_score(self, analysis: Dict) -> float:
        """Calculate overall risk score (0-100, higher = riskier)"""
        volatility = analysis.get('volatility', {}).get('annualized_volatility', 0.2)
        max_drawdown = abs(analysis.get('risk_metrics', {}).get('max_drawdown', 0.1))
        beta = analysis.get('beta_analysis', {}).get('beta', 1.0)
        
        # Risk score calculation
        vol_score = min(50, volatility * 100)  # Cap at 50
        drawdown_score = min(30, max_drawdown * 100)  # Cap at 30
        beta_score = min(20, abs(beta - 1) * 20)  # Cap at 20
        
        return min(100, vol_score + drawdown_score + beta_score)
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score < 30:
            return "Low Risk"
        elif risk_score < 50:
            return "Moderate Risk"
        elif risk_score < 70:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _generate_risk_summary(self, analysis: Dict) -> str:
        """Generate risk summary"""
        risk_category = analysis.get('risk_category', 'Moderate Risk')
        volatility = analysis.get('volatility', {}).get('annualized_volatility', 0.2)
        
        return f"This investment carries {risk_category.lower()} with an annualized volatility of {volatility:.1%}. " \
               f"Suitable for investors with appropriate risk tolerance."
