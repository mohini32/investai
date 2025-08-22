"""
Social Analytics endpoints - Analytics and insights for social trading community
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.social_analytics_service import SocialAnalyticsService

router = APIRouter()


@router.get("/community", response_model=Dict[str, Any])
async def get_community_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get overall community analytics"""
    try:
        analytics_service = SocialAnalyticsService(db)
        analytics = analytics_service.get_community_analytics()
        
        return {
            "status": "success",
            "data": {
                "community_analytics": analytics,
                "analytics_type": "community_overview",
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": "Community analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get community analytics: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_user_analytics(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed analytics for a specific user"""
    try:
        analytics_service = SocialAnalyticsService(db)
        analytics = analytics_service.get_user_analytics(user_id)
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User analytics not found"
            )
        
        return {
            "status": "success",
            "data": {
                "user_analytics": analytics,
                "analytics_type": "user_detailed",
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": "User analytics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics: {str(e)}"
        )


@router.get("/user/my", response_model=Dict[str, Any])
async def get_my_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's detailed analytics"""
    try:
        analytics_service = SocialAnalyticsService(db)
        analytics = analytics_service.get_user_analytics(current_user.id)
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User analytics not found. Please create a social profile first."
            )
        
        return {
            "status": "success",
            "data": {
                "user_analytics": analytics,
                "analytics_type": "personal_analytics",
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": "Personal analytics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get personal analytics: {str(e)}"
        )


@router.get("/trending", response_model=Dict[str, Any])
async def get_trending_analysis(
    days: int = Query(7, ge=1, le=30, description="Number of days for trending analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get trending analysis for specified period"""
    try:
        analytics_service = SocialAnalyticsService(db)
        trending = analytics_service.get_trending_analysis(days)
        
        return {
            "status": "success",
            "data": {
                "trending_analysis": trending,
                "analytics_type": "trending_content",
                "analysis_period_days": days,
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": f"Trending analysis for {days} days retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending analysis: {str(e)}"
        )


@router.get("/sentiment", response_model=Dict[str, Any])
async def get_investment_sentiment(
    symbol: Optional[str] = Query(None, description="Stock symbol for sentiment analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get investment sentiment analysis"""
    try:
        analytics_service = SocialAnalyticsService(db)
        sentiment = analytics_service.get_investment_sentiment(symbol)
        
        return {
            "status": "success",
            "data": {
                "sentiment_analysis": sentiment,
                "analytics_type": "investment_sentiment",
                "symbol_filter": symbol,
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": f"Investment sentiment analysis retrieved successfully{' for ' + symbol if symbol else ''}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get investment sentiment: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_community_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-powered community insights"""
    try:
        analytics_service = SocialAnalyticsService(db)
        insights = analytics_service.get_community_insights()
        
        return {
            "status": "success",
            "data": {
                "community_insights": insights,
                "analytics_type": "ai_insights",
                "generated_at": insights.get("generated_at", analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat())
            },
            "message": "Community insights retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get community insights: {str(e)}"
        )


@router.get("/engagement/overview", response_model=Dict[str, Any])
async def get_engagement_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get engagement overview across the community"""
    try:
        analytics_service = SocialAnalyticsService(db)
        community_analytics = analytics_service.get_community_analytics()
        
        engagement_data = community_analytics.get("engagement_metrics", {})
        content_data = community_analytics.get("content_analytics", {})
        
        # Calculate additional engagement metrics
        total_posts = community_analytics.get("community_overview", {}).get("total_posts", 0)
        avg_engagement = engagement_data.get("average_engagement_per_post", 0)
        
        # Engagement quality assessment
        if avg_engagement > 15:
            engagement_quality = "excellent"
        elif avg_engagement > 8:
            engagement_quality = "good"
        elif avg_engagement > 3:
            engagement_quality = "fair"
        else:
            engagement_quality = "needs_improvement"
        
        return {
            "status": "success",
            "data": {
                "engagement_overview": {
                    "total_engagement": engagement_data.get("total_likes", 0) + engagement_data.get("total_comments", 0) + engagement_data.get("total_shares", 0),
                    "average_engagement_per_post": avg_engagement,
                    "engagement_quality": engagement_quality,
                    "total_views": engagement_data.get("total_views", 0),
                    "engagement_breakdown": {
                        "likes": engagement_data.get("total_likes", 0),
                        "comments": engagement_data.get("total_comments", 0),
                        "shares": engagement_data.get("total_shares", 0)
                    },
                    "content_distribution": content_data.get("post_type_distribution", {}),
                    "top_content": content_data.get("top_performing_posts", [])
                },
                "analytics_type": "engagement_overview",
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": "Engagement overview retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get engagement overview: {str(e)}"
        )


@router.get("/performance/leaderboard", response_model=Dict[str, Any])
async def get_performance_leaderboard(
    metric: str = Query("reputation", description="Leaderboard metric: reputation, followers, posts, engagement"),
    limit: int = Query(20, ge=5, le=50, description="Number of top performers"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get performance leaderboard"""
    try:
        analytics_service = SocialAnalyticsService(db)
        
        # This would be implemented with more sophisticated ranking in production
        # For now, return mock leaderboard data
        leaderboard_data = {
            "metric": metric,
            "top_performers": [
                {
                    "rank": 1,
                    "user_id": 1,
                    "display_name": "InvestmentGuru",
                    "metric_value": 95.5,
                    "followers_count": 1250,
                    "posts_count": 89,
                    "is_verified": True
                },
                {
                    "rank": 2,
                    "user_id": 2,
                    "display_name": "StockAnalyst",
                    "metric_value": 92.3,
                    "followers_count": 980,
                    "posts_count": 67,
                    "is_verified": True
                },
                {
                    "rank": 3,
                    "user_id": 3,
                    "display_name": "MarketExpert",
                    "metric_value": 89.7,
                    "followers_count": 756,
                    "posts_count": 45,
                    "is_verified": False
                }
            ],
            "user_rank": None,  # Would calculate current user's rank
            "total_participants": 1500
        }
        
        return {
            "status": "success",
            "data": {
                "leaderboard": leaderboard_data,
                "analytics_type": "performance_leaderboard",
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": f"Performance leaderboard by {metric} retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance leaderboard: {str(e)}"
        )


@router.get("/growth/metrics", response_model=Dict[str, Any])
async def get_growth_metrics(
    period: str = Query("30d", description="Growth period: 7d, 30d, 90d"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get community growth metrics"""
    try:
        analytics_service = SocialAnalyticsService(db)
        
        # Mock growth metrics - would calculate actual growth in production
        growth_metrics = {
            "period": period,
            "user_growth": {
                "new_users": 145,
                "growth_rate": 12.5,
                "retention_rate": 78.3
            },
            "content_growth": {
                "new_posts": 892,
                "growth_rate": 18.7,
                "quality_score": 8.2
            },
            "engagement_growth": {
                "total_interactions": 5420,
                "growth_rate": 22.1,
                "average_per_user": 3.7
            },
            "investment_ideas_growth": {
                "new_ideas": 67,
                "growth_rate": 15.3,
                "success_rate": 64.2
            }
        }
        
        return {
            "status": "success",
            "data": {
                "growth_metrics": growth_metrics,
                "analytics_type": "community_growth",
                "generated_at": analytics_service.db.query(analytics_service.db.func.now()).scalar().isoformat()
            },
            "message": f"Growth metrics for {period} retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get growth metrics: {str(e)}"
        )
