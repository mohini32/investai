"""
Social Analytics Service - Analytics and insights for social trading community
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timedelta
import json
import logging

from app.models.social import (
    UserProfile, UserFollow, SocialPost, PostComment, PostReaction, PostShare,
    InvestmentIdea, IdeaFollower, CommunityGroup, GroupMember,
    PostType, ReactionType
)
from app.models.user import User

logger = logging.getLogger(__name__)


class SocialAnalyticsService:
    """Service for social trading analytics and insights"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_community_analytics(self) -> Dict[str, Any]:
        """Get overall community analytics"""
        try:
            # Basic community stats
            total_users = self.db.query(UserProfile).count()
            total_posts = self.db.query(SocialPost).count()
            total_ideas = self.db.query(InvestmentIdea).count()
            total_groups = self.db.query(CommunityGroup).count()
            
            # Active users (posted in last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_users = self.db.query(UserProfile).join(SocialPost).filter(
                SocialPost.published_at >= thirty_days_ago
            ).distinct().count()
            
            # Engagement metrics
            total_likes = self.db.query(func.sum(SocialPost.likes_count)).scalar() or 0
            total_comments = self.db.query(func.sum(SocialPost.comments_count)).scalar() or 0
            total_shares = self.db.query(func.sum(SocialPost.shares_count)).scalar() or 0
            total_views = self.db.query(func.sum(SocialPost.views_count)).scalar() or 0
            
            # Post type distribution
            post_type_stats = self.db.query(
                SocialPost.post_type,
                func.count(SocialPost.id).label('count')
            ).group_by(SocialPost.post_type).all()
            
            post_type_distribution = {pt.value: count for pt, count in post_type_stats}
            
            # Top performing content
            top_posts = self.db.query(SocialPost).order_by(
                desc(SocialPost.likes_count + SocialPost.comments_count + SocialPost.shares_count)
            ).limit(5).all()
            
            top_posts_data = []
            for post in top_posts:
                engagement = post.likes_count + post.comments_count + post.shares_count
                top_posts_data.append({
                    "id": post.id,
                    "title": post.title,
                    "post_type": post.post_type.value,
                    "engagement_score": engagement,
                    "author": post.author.display_name
                })
            
            # Investment ideas performance
            ideas_stats = self.db.query(
                InvestmentIdea.recommendation,
                func.count(InvestmentIdea.id).label('count'),
                func.avg(InvestmentIdea.idea_performance).label('avg_performance')
            ).group_by(InvestmentIdea.recommendation).all()
            
            ideas_performance = {}
            for rec, count, avg_perf in ideas_stats:
                ideas_performance[rec] = {
                    "count": count,
                    "average_performance": float(avg_perf) if avg_perf else 0
                }
            
            return {
                "community_overview": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_posts": total_posts,
                    "total_investment_ideas": total_ideas,
                    "total_groups": total_groups,
                    "activity_rate": (active_users / total_users * 100) if total_users > 0 else 0
                },
                "engagement_metrics": {
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "total_shares": total_shares,
                    "total_views": total_views,
                    "average_engagement_per_post": (total_likes + total_comments + total_shares) / total_posts if total_posts > 0 else 0
                },
                "content_analytics": {
                    "post_type_distribution": post_type_distribution,
                    "top_performing_posts": top_posts_data
                },
                "investment_analytics": {
                    "ideas_by_recommendation": ideas_performance,
                    "total_idea_followers": self.db.query(IdeaFollower).count()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get community analytics: {str(e)}")
            return {}
    
    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed analytics for a specific user"""
        try:
            profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if not profile:
                return {}
            
            # Post analytics
            posts = self.db.query(SocialPost).filter(SocialPost.author_id == profile.id).all()
            
            if posts:
                total_engagement = sum(p.likes_count + p.comments_count + p.shares_count for p in posts)
                avg_engagement = total_engagement / len(posts)
                
                # Post performance over time
                post_performance = []
                for post in posts[-10:]:  # Last 10 posts
                    engagement = post.likes_count + post.comments_count + post.shares_count
                    post_performance.append({
                        "id": post.id,
                        "title": post.title,
                        "post_type": post.post_type.value,
                        "engagement": engagement,
                        "published_at": post.published_at.isoformat()
                    })
                
                # Best performing post
                best_post = max(posts, key=lambda p: p.likes_count + p.comments_count + p.shares_count)
                best_post_data = {
                    "id": best_post.id,
                    "title": best_post.title,
                    "engagement": best_post.likes_count + best_post.comments_count + best_post.shares_count,
                    "published_at": best_post.published_at.isoformat()
                }
            else:
                total_engagement = 0
                avg_engagement = 0
                post_performance = []
                best_post_data = None
            
            # Investment ideas analytics
            ideas = self.db.query(InvestmentIdea).filter(InvestmentIdea.author_id == profile.id).all()
            
            ideas_analytics = {
                "total_ideas": len(ideas),
                "total_followers": sum(idea.followers_count for idea in ideas),
                "average_performance": sum(idea.idea_performance for idea in ideas) / len(ideas) if ideas else 0,
                "ideas_by_recommendation": {}
            }
            
            # Group ideas by recommendation
            for idea in ideas:
                rec = idea.recommendation
                if rec not in ideas_analytics["ideas_by_recommendation"]:
                    ideas_analytics["ideas_by_recommendation"][rec] = {
                        "count": 0,
                        "total_followers": 0,
                        "avg_performance": 0
                    }
                
                ideas_analytics["ideas_by_recommendation"][rec]["count"] += 1
                ideas_analytics["ideas_by_recommendation"][rec]["total_followers"] += idea.followers_count
                ideas_analytics["ideas_by_recommendation"][rec]["avg_performance"] += idea.idea_performance
            
            # Calculate averages
            for rec_data in ideas_analytics["ideas_by_recommendation"].values():
                if rec_data["count"] > 0:
                    rec_data["avg_performance"] /= rec_data["count"]
            
            # Follower growth (simplified - would need historical data in production)
            follower_growth = self._calculate_follower_growth(profile.id)
            
            # Engagement trends
            engagement_trends = self._calculate_engagement_trends(profile.id)
            
            return {
                "user_id": user_id,
                "profile_id": profile.id,
                "basic_stats": {
                    "followers_count": profile.followers_count,
                    "following_count": profile.following_count,
                    "posts_count": profile.posts_count,
                    "reputation_score": profile.reputation_score
                },
                "content_analytics": {
                    "total_posts": len(posts),
                    "total_engagement": total_engagement,
                    "average_engagement_per_post": avg_engagement,
                    "best_performing_post": best_post_data,
                    "recent_post_performance": post_performance
                },
                "investment_analytics": ideas_analytics,
                "growth_metrics": {
                    "follower_growth": follower_growth,
                    "engagement_trends": engagement_trends
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {str(e)}")
            return {}
    
    def get_trending_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Get trending analysis for specified period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Trending posts
            trending_posts = self.db.query(SocialPost).filter(
                SocialPost.published_at >= cutoff_date
            ).order_by(
                desc(SocialPost.likes_count + SocialPost.comments_count + SocialPost.shares_count)
            ).limit(10).all()
            
            trending_posts_data = []
            for post in trending_posts:
                engagement = post.likes_count + post.comments_count + post.shares_count
                trending_posts_data.append({
                    "id": post.id,
                    "title": post.title,
                    "post_type": post.post_type.value,
                    "engagement_score": engagement,
                    "growth_rate": self._calculate_post_growth_rate(post.id, days),
                    "author": {
                        "display_name": post.author.display_name,
                        "is_verified": post.author.is_verified
                    }
                })
            
            # Trending stocks (mentioned in posts)
            trending_stocks = self._get_trending_stocks(days)
            
            # Trending users (by follower growth)
            trending_users = self._get_trending_users(days)
            
            # Trending investment ideas
            trending_ideas = self.db.query(InvestmentIdea).filter(
                InvestmentIdea.created_at >= cutoff_date
            ).order_by(desc(InvestmentIdea.followers_count)).limit(10).all()
            
            trending_ideas_data = []
            for idea in trending_ideas:
                trending_ideas_data.append({
                    "id": idea.id,
                    "stock_symbol": idea.stock_symbol,
                    "recommendation": idea.recommendation,
                    "followers_count": idea.followers_count,
                    "performance": idea.idea_performance,
                    "author": idea.author.display_name
                })
            
            return {
                "analysis_period": f"{days} days",
                "trending_posts": trending_posts_data,
                "trending_stocks": trending_stocks,
                "trending_users": trending_users,
                "trending_ideas": trending_ideas_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get trending analysis: {str(e)}")
            return {}
    
    def get_investment_sentiment(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get investment sentiment analysis"""
        try:
            # Base query for investment ideas
            query = self.db.query(InvestmentIdea)
            
            if symbol:
                query = query.filter(InvestmentIdea.stock_symbol == symbol.upper())
            
            ideas = query.all()
            
            if not ideas:
                return {"symbol": symbol, "sentiment": "neutral", "total_ideas": 0}
            
            # Calculate sentiment
            buy_count = len([i for i in ideas if i.recommendation == "buy"])
            sell_count = len([i for i in ideas if i.recommendation == "sell"])
            hold_count = len([i for i in ideas if i.recommendation == "hold"])
            
            total_ideas = len(ideas)
            
            # Determine overall sentiment
            if buy_count > sell_count and buy_count > hold_count:
                sentiment = "bullish"
            elif sell_count > buy_count and sell_count > hold_count:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            # Calculate sentiment score (-1 to 1)
            sentiment_score = (buy_count - sell_count) / total_ideas
            
            # Get recent sentiment trend
            recent_ideas = [i for i in ideas if i.created_at >= datetime.now() - timedelta(days=30)]
            recent_sentiment = self._calculate_recent_sentiment(recent_ideas)
            
            return {
                "symbol": symbol,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "total_ideas": total_ideas,
                "recommendation_breakdown": {
                    "buy": buy_count,
                    "sell": sell_count,
                    "hold": hold_count
                },
                "recent_trend": recent_sentiment,
                "top_contributors": self._get_top_sentiment_contributors(ideas)
            }
            
        except Exception as e:
            logger.error(f"Failed to get investment sentiment: {str(e)}")
            return {}
    
    def get_community_insights(self) -> Dict[str, Any]:
        """Get AI-powered community insights"""
        try:
            insights = []
            
            # Analyze posting patterns
            post_patterns = self._analyze_posting_patterns()
            if post_patterns:
                insights.extend(post_patterns)
            
            # Analyze user engagement
            engagement_insights = self._analyze_engagement_patterns()
            if engagement_insights:
                insights.extend(engagement_insights)
            
            # Analyze investment trends
            investment_insights = self._analyze_investment_trends()
            if investment_insights:
                insights.extend(investment_insights)
            
            # Community health metrics
            health_metrics = self._calculate_community_health()
            
            return {
                "insights": insights,
                "community_health": health_metrics,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get community insights: {str(e)}")
            return {}
    
    # Helper methods
    def _calculate_follower_growth(self, profile_id: int) -> Dict[str, float]:
        """Calculate follower growth metrics"""
        # Simplified calculation - in production would use historical data
        profile = self.db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            return {"growth_rate": 0, "growth_trend": "stable"}
        
        # Mock growth calculation
        return {
            "growth_rate": 5.2,  # 5.2% growth
            "growth_trend": "increasing"
        }
    
    def _calculate_engagement_trends(self, profile_id: int) -> Dict[str, Any]:
        """Calculate engagement trends"""
        posts = self.db.query(SocialPost).filter(
            SocialPost.author_id == profile_id
        ).order_by(desc(SocialPost.published_at)).limit(10).all()
        
        if len(posts) < 2:
            return {"trend": "insufficient_data"}
        
        recent_engagement = sum(p.likes_count + p.comments_count for p in posts[:5])
        older_engagement = sum(p.likes_count + p.comments_count for p in posts[5:])
        
        if older_engagement == 0:
            trend = "increasing" if recent_engagement > 0 else "stable"
        else:
            change = (recent_engagement - older_engagement) / older_engagement
            if change > 0.1:
                trend = "increasing"
            elif change < -0.1:
                trend = "decreasing"
            else:
                trend = "stable"
        
        return {
            "trend": trend,
            "recent_avg_engagement": recent_engagement / 5 if len(posts) >= 5 else 0,
            "change_percentage": change * 100 if 'change' in locals() else 0
        }
    
    def _calculate_post_growth_rate(self, post_id: int, days: int) -> float:
        """Calculate post growth rate"""
        # Simplified calculation - would use time-series data in production
        return 15.5  # Mock 15.5% growth rate
    
    def _get_trending_stocks(self, days: int) -> List[Dict[str, Any]]:
        """Get trending stocks mentioned in posts"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # This would be more sophisticated in production
        # For now, return mock trending stocks
        return [
            {"symbol": "RELIANCE", "mentions": 45, "sentiment": "bullish"},
            {"symbol": "TCS", "mentions": 38, "sentiment": "bullish"},
            {"symbol": "HDFCBANK", "mentions": 32, "sentiment": "neutral"},
            {"symbol": "INFY", "mentions": 28, "sentiment": "bullish"},
            {"symbol": "ITC", "mentions": 22, "sentiment": "bearish"}
        ]
    
    def _get_trending_users(self, days: int) -> List[Dict[str, Any]]:
        """Get trending users by growth"""
        # Mock trending users - would calculate actual growth in production
        trending_users = self.db.query(UserProfile).filter(
            UserProfile.is_public_profile == True
        ).order_by(desc(UserProfile.reputation_score)).limit(5).all()
        
        trending_data = []
        for user in trending_users:
            trending_data.append({
                "id": user.id,
                "display_name": user.display_name,
                "followers_count": user.followers_count,
                "growth_rate": 12.5,  # Mock growth rate
                "is_verified": user.is_verified
            })
        
        return trending_data
    
    def _calculate_recent_sentiment(self, recent_ideas: List[InvestmentIdea]) -> str:
        """Calculate recent sentiment trend"""
        if not recent_ideas:
            return "neutral"
        
        buy_count = len([i for i in recent_ideas if i.recommendation == "buy"])
        sell_count = len([i for i in recent_ideas if i.recommendation == "sell"])
        
        if buy_count > sell_count:
            return "increasingly_bullish"
        elif sell_count > buy_count:
            return "increasingly_bearish"
        else:
            return "stable"
    
    def _get_top_sentiment_contributors(self, ideas: List[InvestmentIdea]) -> List[Dict[str, Any]]:
        """Get top contributors to sentiment"""
        contributors = {}
        
        for idea in ideas:
            author_id = idea.author_id
            if author_id not in contributors:
                contributors[author_id] = {
                    "author": idea.author.display_name,
                    "ideas_count": 0,
                    "followers_impact": 0
                }
            
            contributors[author_id]["ideas_count"] += 1
            contributors[author_id]["followers_impact"] += idea.followers_count
        
        # Sort by impact
        sorted_contributors = sorted(
            contributors.values(),
            key=lambda x: x["followers_impact"],
            reverse=True
        )
        
        return sorted_contributors[:5]
    
    def _analyze_posting_patterns(self) -> List[str]:
        """Analyze community posting patterns"""
        insights = []
        
        # Analyze post frequency
        recent_posts = self.db.query(SocialPost).filter(
            SocialPost.published_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        if recent_posts > 100:
            insights.append("High community activity with 100+ posts this week")
        elif recent_posts < 20:
            insights.append("Lower posting activity - consider engagement initiatives")
        
        return insights
    
    def _analyze_engagement_patterns(self) -> List[str]:
        """Analyze engagement patterns"""
        insights = []
        
        # Calculate average engagement
        avg_engagement = self.db.query(
            func.avg(SocialPost.likes_count + SocialPost.comments_count)
        ).scalar() or 0
        
        if avg_engagement > 10:
            insights.append(f"Strong community engagement with {avg_engagement:.1f} average interactions per post")
        elif avg_engagement < 3:
            insights.append("Low engagement levels - focus on content quality and community building")
        
        return insights
    
    def _analyze_investment_trends(self) -> List[str]:
        """Analyze investment trends"""
        insights = []
        
        # Analyze recent investment ideas
        recent_ideas = self.db.query(InvestmentIdea).filter(
            InvestmentIdea.created_at >= datetime.now() - timedelta(days=30)
        ).all()
        
        if recent_ideas:
            buy_ratio = len([i for i in recent_ideas if i.recommendation == "buy"]) / len(recent_ideas)
            
            if buy_ratio > 0.6:
                insights.append("Community sentiment is predominantly bullish with 60%+ buy recommendations")
            elif buy_ratio < 0.3:
                insights.append("Community showing caution with fewer buy recommendations")
        
        return insights
    
    def _calculate_community_health(self) -> Dict[str, Any]:
        """Calculate community health metrics"""
        total_users = self.db.query(UserProfile).count()
        active_users = self.db.query(UserProfile).filter(
            UserProfile.last_active_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        activity_rate = (active_users / total_users * 100) if total_users > 0 else 0
        
        # Health score calculation
        health_score = min(100, activity_rate * 2)  # Simplified calculation
        
        if health_score >= 80:
            health_status = "excellent"
        elif health_score >= 60:
            health_status = "good"
        elif health_score >= 40:
            health_status = "fair"
        else:
            health_status = "needs_attention"
        
        return {
            "health_score": health_score,
            "health_status": health_status,
            "activity_rate": activity_rate,
            "total_users": total_users,
            "active_users": active_users
        }
