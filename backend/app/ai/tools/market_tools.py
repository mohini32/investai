"""
Market data tools for AI agents
"""

import yfinance as yf
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from crewai_tools import BaseTool
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.market_data import Security, PriceData, MutualFundData
from app.core.config import settings


class MarketDataTool(BaseTool):
    """Tool for fetching real-time market data"""
    
    name: str = "Market Data Fetcher"
    description: str = "Fetches real-time market data for stocks and mutual funds from various sources including NSE, BSE, and Yahoo Finance"
    
    def _run(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """Fetch market data for a given symbol"""
        try:
            # Try Yahoo Finance first (works for Indian stocks with .NS/.BO suffix)
            yf_symbol = self._get_yahoo_symbol(symbol, exchange)
            ticker = yf.Ticker(yf_symbol)
            
            # Get current data
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', hist['Close'].iloc[-1])
            
            market_data = {
                "symbol": symbol,
                "exchange": exchange,
                "current_price": float(current_price),
                "previous_close": float(previous_close),
                "open_price": float(hist['Open'].iloc[-1]),
                "high_price": float(hist['High'].iloc[-1]),
                "low_price": float(hist['Low'].iloc[-1]),
                "volume": int(hist['Volume'].iloc[-1]),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "pb_ratio": info.get('priceToBook'),
                "dividend_yield": info.get('dividendYield'),
                "week_52_high": info.get('fiftyTwoWeekHigh'),
                "week_52_low": info.get('fiftyTwoWeekLow'),
                "last_updated": datetime.now().isoformat()
            }
            
            # Calculate price change
            if previous_close and previous_close > 0:
                price_change = current_price - previous_close
                price_change_percentage = (price_change / previous_close) * 100
                market_data.update({
                    "price_change": float(price_change),
                    "price_change_percentage": float(price_change_percentage)
                })
            
            return market_data
            
        except Exception as e:
            return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}
    
    def _get_yahoo_symbol(self, symbol: str, exchange: str) -> str:
        """Convert Indian stock symbol to Yahoo Finance format"""
        if exchange.upper() == "NSE":
            return f"{symbol}.NS"
        elif exchange.upper() == "BSE":
            return f"{symbol}.BO"
        else:
            return symbol


class StockAnalysisTool(BaseTool):
    """Tool for comprehensive stock analysis"""
    
    name: str = "Stock Analysis Tool"
    description: str = "Performs comprehensive fundamental and technical analysis of stocks including financial ratios, business analysis, and recommendations"
    
    def _run(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """Perform comprehensive stock analysis"""
        try:
            # Get market data first
            market_tool = MarketDataTool()
            market_data = market_tool._run(symbol, exchange)
            
            if "error" in market_data:
                return market_data
            
            # Get detailed stock information
            yf_symbol = f"{symbol}.NS" if exchange.upper() == "NSE" else f"{symbol}.BO"
            ticker = yf.Ticker(yf_symbol)
            
            # Get financial data
            info = ticker.info
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            # Calculate key financial ratios
            analysis = {
                "symbol": symbol,
                "company_name": info.get('longName', symbol),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "market_cap_category": self._get_market_cap_category(info.get('marketCap', 0)),
                
                # Valuation ratios
                "pe_ratio": info.get('trailingPE'),
                "forward_pe": info.get('forwardPE'),
                "pb_ratio": info.get('priceToBook'),
                "ps_ratio": info.get('priceToSalesTrailing12Months'),
                "peg_ratio": info.get('pegRatio'),
                
                # Profitability ratios
                "roe": info.get('returnOnEquity'),
                "roa": info.get('returnOnAssets'),
                "profit_margin": info.get('profitMargins'),
                "operating_margin": info.get('operatingMargins'),
                
                # Financial health
                "debt_to_equity": info.get('debtToEquity'),
                "current_ratio": info.get('currentRatio'),
                "quick_ratio": info.get('quickRatio'),
                
                # Growth metrics
                "revenue_growth": info.get('revenueGrowth'),
                "earnings_growth": info.get('earningsGrowth'),
                
                # Dividend information
                "dividend_yield": info.get('dividendYield'),
                "payout_ratio": info.get('payoutRatio'),
                
                # Risk metrics
                "beta": info.get('beta'),
                "volatility": self._calculate_volatility(ticker),
                
                # Analyst recommendations
                "recommendation": info.get('recommendationKey'),
                "target_price": info.get('targetMeanPrice'),
                
                "analysis_date": datetime.now().isoformat()
            }
            
            # Add fundamental score
            analysis["fundamental_score"] = self._calculate_fundamental_score(analysis)
            
            # Add business analysis
            analysis["business_analysis"] = self._analyze_business(info)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze {symbol}: {str(e)}"}
    
    def _get_market_cap_category(self, market_cap: float) -> str:
        """Categorize stock by market cap (in INR)"""
        if market_cap >= 200000000000:  # 20,000 crores
            return "large_cap"
        elif market_cap >= 50000000000:  # 5,000 crores
            return "mid_cap"
        else:
            return "small_cap"
    
    def _calculate_volatility(self, ticker) -> Optional[float]:
        """Calculate 30-day volatility"""
        try:
            hist = ticker.history(period="1mo")
            if len(hist) > 1:
                returns = hist['Close'].pct_change().dropna()
                return float(returns.std() * (252 ** 0.5))  # Annualized volatility
        except:
            pass
        return None
    
    def _calculate_fundamental_score(self, analysis: Dict) -> float:
        """Calculate fundamental score (0-100)"""
        score = 50  # Base score
        
        # PE ratio scoring
        pe = analysis.get('pe_ratio')
        if pe and 10 <= pe <= 25:
            score += 10
        elif pe and pe < 10:
            score += 5
        elif pe and pe > 30:
            score -= 10
        
        # ROE scoring
        roe = analysis.get('roe')
        if roe and roe > 0.15:
            score += 15
        elif roe and roe > 0.10:
            score += 10
        elif roe and roe < 0.05:
            score -= 10
        
        # Debt to equity scoring
        de = analysis.get('debt_to_equity')
        if de and de < 0.5:
            score += 10
        elif de and de > 1.0:
            score -= 10
        
        # Revenue growth scoring
        growth = analysis.get('revenue_growth')
        if growth and growth > 0.15:
            score += 10
        elif growth and growth < 0:
            score -= 15
        
        return max(0, min(100, score))
    
    def _analyze_business(self, info: Dict) -> str:
        """Generate business analysis summary"""
        company = info.get('longName', 'Company')
        sector = info.get('sector', 'Unknown sector')
        business = info.get('longBusinessSummary', 'No business summary available')
        
        return f"{company} operates in the {sector} sector. {business[:200]}..."


class MutualFundAnalysisTool(BaseTool):
    """Tool for mutual fund analysis"""
    
    name: str = "Mutual Fund Analysis Tool"
    description: str = "Analyzes mutual funds including NAV, returns, expense ratios, portfolio composition, and risk metrics"
    
    def _run(self, scheme_code: str) -> Dict[str, Any]:
        """Analyze mutual fund by scheme code"""
        try:
            # This would typically connect to AMFI API or other MF data sources
            # For now, we'll create a mock analysis structure
            
            analysis = {
                "scheme_code": scheme_code,
                "scheme_name": f"Sample Mutual Fund {scheme_code}",
                "amc_name": "Sample AMC",
                "category": "Equity",
                "sub_category": "Large Cap",
                "fund_type": "Open",
                
                # NAV information
                "current_nav": 150.25,
                "previous_nav": 149.80,
                "nav_change": 0.45,
                "nav_change_percentage": 0.30,
                
                # Returns
                "returns_1d": 0.30,
                "returns_1w": 1.25,
                "returns_1m": 3.45,
                "returns_3m": 8.20,
                "returns_6m": 12.50,
                "returns_1y": 18.75,
                "returns_3y": 15.20,
                "returns_5y": 12.80,
                
                # Fund metrics
                "aum": 5000000000,  # 5000 crores
                "expense_ratio": 1.25,
                "exit_load": 1.0,
                "minimum_investment": 5000,
                "minimum_sip": 1000,
                
                # Risk metrics
                "standard_deviation": 15.25,
                "sharpe_ratio": 1.15,
                "alpha": 2.5,
                "beta": 0.95,
                
                # Ratings
                "crisil_rating": "4 Star",
                "morningstar_rating": 4,
                
                "analysis_date": datetime.now().isoformat()
            }
            
            # Add AI recommendation
            analysis["ai_recommendation"] = self._generate_mf_recommendation(analysis)
            analysis["risk_score"] = self._calculate_risk_score(analysis)
            analysis["suitability_score"] = self._calculate_suitability_score(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze mutual fund {scheme_code}: {str(e)}"}
    
    def _generate_mf_recommendation(self, analysis: Dict) -> str:
        """Generate AI recommendation for mutual fund"""
        returns_1y = analysis.get('returns_1y', 0)
        expense_ratio = analysis.get('expense_ratio', 2.0)
        
        if returns_1y > 15 and expense_ratio < 1.5:
            return "BUY"
        elif returns_1y > 10:
            return "HOLD"
        else:
            return "AVOID"
    
    def _calculate_risk_score(self, analysis: Dict) -> float:
        """Calculate risk score (0-100, higher = riskier)"""
        std_dev = analysis.get('standard_deviation', 15)
        beta = analysis.get('beta', 1.0)
        
        # Simple risk calculation
        risk_score = (std_dev * 2) + (abs(beta - 1) * 20)
        return min(100, max(0, risk_score))
    
    def _calculate_suitability_score(self, analysis: Dict) -> float:
        """Calculate suitability score (0-100)"""
        returns_3y = analysis.get('returns_3y', 10)
        expense_ratio = analysis.get('expense_ratio', 2.0)
        sharpe_ratio = analysis.get('sharpe_ratio', 1.0)
        
        score = 50
        score += min(30, returns_3y * 2)  # Returns contribution
        score -= expense_ratio * 10  # Expense penalty
        score += sharpe_ratio * 15  # Risk-adjusted returns
        
        return max(0, min(100, score))
