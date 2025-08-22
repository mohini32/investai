"""
Social Trading endpoints - Social trading and community features
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.social_service import SocialTradingService

router = APIRouter()


# Pydantic models
class UserProfileCreate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100, description="Display name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    investment_style: Optional[str] = Field("balanced", description="Investment style")
    is_public_profile: bool = Field(True, description="Public profile visibility")
    allow_portfolio_sharing: bool = Field(False, description="Allow portfolio sharing")
    allow_direct_messages: bool = Field(True, description="Allow direct messages")
    show_performance_stats: bool = Field(True, description="Show performance statistics")
    expertise_areas: List[str] = Field(default=[], description="Areas of expertise")


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100, description="Display name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    investment_style: Optional[str] = Field(None, description="Investment style")
    is_public_profile: Optional[bool] = Field(None, description="Public profile visibility")
    allow_portfolio_sharing: Optional[bool] = Field(None, description="Allow portfolio sharing")
    allow_direct_messages: Optional[bool] = Field(None, description="Allow direct messages")
    show_performance_stats: Optional[bool] = Field(None, description="Show performance statistics")
    expertise_areas: Optional[List[str]] = Field(None, description="Areas of expertise")


class SocialPostCreate(BaseModel):
    post_type: str = Field(..., description="Type of post")
    title: Optional[str] = Field(None, max_length=255, description="Post title")
    content: str = Field(..., max_length=5000, description="Post content")
    image_urls: List[str] = Field(default=[], description="Image URLs")
    video_url: Optional[str] = Field(None, description="Video URL")
    mentioned_stocks: List[str] = Field(default=[], description="Mentioned stock symbols")
    mentioned_portfolios: List[int] = Field(default=[], description="Mentioned portfolio IDs")
    investment_thesis: Optional[str] = Field(None, description="Investment thesis")
    target_price: Optional[float] = Field(None, ge=0, description="Target price")
    risk_level: Optional[str] = Field("medium", description="Risk level")
    visibility: str = Field("public", description="Post visibility")
    allow_comments: bool = Field(True, description="Allow comments")
    allow_reactions: bool = Field(True, description="Allow reactions")
    tags: List[str] = Field(default=[], description="Post tags")
    hashtags: List[str] = Field(default=[], description="Post hashtags")


class InvestmentIdeaCreate(BaseModel):
    stock_symbol: str = Field(..., max_length=50, description="Stock symbol")
    stock_name: str = Field(..., max_length=255, description="Stock name")
    recommendation: str = Field(..., description="Investment recommendation: buy, sell, hold")
    current_price: float = Field(..., gt=0, description="Current stock price")
    target_price: Optional[float] = Field(None, gt=0, description="Target price")
    stop_loss_price: Optional[float] = Field(None, gt=0, description="Stop loss price")
    investment_thesis: str = Field(..., max_length=2000, description="Investment thesis")
    key_catalysts: List[str] = Field(default=[], description="Key catalysts")
    risks: List[str] = Field(default=[], description="Key risks")
    time_horizon: str = Field("medium_term", description="Investment time horizon")
    suggested_allocation: float = Field(5.0, ge=0, le=100, description="Suggested portfolio allocation %")
    risk_level: str = Field("medium", description="Risk level")
    create_post: bool = Field(True, description="Create associated social post")


class CommunityGroupCreate(BaseModel):
    name: str = Field(..., max_length=255, description="Group name")
    description: Optional[str] = Field(None, max_length=1000, description="Group description")
    group_image_url: Optional[str] = Field(None, description="Group image URL")
    is_public: bool = Field(True, description="Public group visibility")
    requires_approval: bool = Field(False, description="Require approval to join")
    allow_member_posts: bool = Field(True, description="Allow member posts")
    category: str = Field("general", description="Group category")
    tags: List[str] = Field(default=[], description="Group tags")


# User Profile Endpoints
@router.post("/profile", response_model=Dict[str, Any])
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create social trading profile"""
    try:
        social_service = SocialTradingService(db)
        profile = social_service.create_user_profile(current_user.id, profile_data.dict())
        
        return {
            "status": "success",
            "data": {
                "id": profile.id,
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "bio": profile.bio,
                "investment_style": profile.investment_style,
                "is_public_profile": profile.is_public_profile,
                "followers_count": profile.followers_count,
                "following_count": profile.following_count,
                "posts_count": profile.posts_count,
                "created_at": profile.created_at.isoformat()
            },
            "message": "Social profile created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social profile: {str(e)}"
        )


@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's social profile"""
    try:
        social_service = SocialTradingService(db)
        profile = social_service.get_user_profile(current_user.id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social profile not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": profile.id,
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "bio": profile.bio,
                "profile_image_url": profile.profile_image_url,
                "cover_image_url": profile.cover_image_url,
                "investment_style": profile.investment_style,
                "is_public_profile": profile.is_public_profile,
                "allow_portfolio_sharing": profile.allow_portfolio_sharing,
                "allow_direct_messages": profile.allow_direct_messages,
                "show_performance_stats": profile.show_performance_stats,
                "followers_count": profile.followers_count,
                "following_count": profile.following_count,
                "posts_count": profile.posts_count,
                "total_portfolio_value": profile.total_portfolio_value,
                "total_returns": profile.total_returns,
                "total_returns_percentage": profile.total_returns_percentage,
                "best_performing_stock": profile.best_performing_stock,
                "is_verified": profile.is_verified,
                "reputation_score": profile.reputation_score,
                "expertise_areas": profile.expertise_areas,
                "last_active_at": profile.last_active_at.isoformat() if profile.last_active_at else None,
                "joined_at": profile.joined_at.isoformat(),
                "created_at": profile.created_at.isoformat()
            },
            "message": "Social profile retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get social profile: {str(e)}"
        )


@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user's social profile"""
    try:
        social_service = SocialTradingService(db)
        
        # Filter out None values
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        
        profile = social_service.update_user_profile(current_user.id, update_data)
        
        return {
            "status": "success",
            "data": {
                "id": profile.id,
                "display_name": profile.display_name,
                "bio": profile.bio,
                "investment_style": profile.investment_style,
                "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
            },
            "message": "Social profile updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update social profile: {str(e)}"
        )


@router.get("/profile/{user_id}", response_model=Dict[str, Any])
async def get_public_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get another user's public profile"""
    try:
        social_service = SocialTradingService(db)
        profile = social_service.get_user_profile(user_id)
        
        if not profile or not profile.is_public_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Public profile not found"
            )
        
        # Check if current user is following this profile
        is_following = social_service.is_following(current_user.id, user_id)
        
        return {
            "status": "success",
            "data": {
                "id": profile.id,
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "bio": profile.bio,
                "profile_image_url": profile.profile_image_url,
                "cover_image_url": profile.cover_image_url,
                "investment_style": profile.investment_style,
                "followers_count": profile.followers_count,
                "following_count": profile.following_count,
                "posts_count": profile.posts_count,
                "total_portfolio_value": profile.total_portfolio_value if profile.show_performance_stats else None,
                "total_returns": profile.total_returns if profile.show_performance_stats else None,
                "total_returns_percentage": profile.total_returns_percentage if profile.show_performance_stats else None,
                "best_performing_stock": profile.best_performing_stock if profile.show_performance_stats else None,
                "is_verified": profile.is_verified,
                "reputation_score": profile.reputation_score,
                "expertise_areas": profile.expertise_areas,
                "joined_at": profile.joined_at.isoformat(),
                "is_following": is_following
            },
            "message": "Public profile retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public profile: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_user_social_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's social statistics"""
    try:
        social_service = SocialTradingService(db)
        stats = social_service.get_user_social_stats(current_user.id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social profile not found"
            )
        
        return {
            "status": "success",
            "data": stats,
            "message": "Social statistics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get social statistics: {str(e)}"
        )


# Follow System Endpoints
@router.post("/follow/{user_id}", response_model=Dict[str, Any])
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Follow another user"""
    try:
        social_service = SocialTradingService(db)
        follow = social_service.follow_user(current_user.id, user_id)

        return {
            "status": "success",
            "data": {
                "id": follow.id,
                "follower_id": follow.follower_id,
                "following_id": follow.following_id,
                "status": follow.status.value,
                "follow_date": follow.follow_date.isoformat()
            },
            "message": "User followed successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to follow user: {str(e)}"
        )


@router.delete("/follow/{user_id}", response_model=Dict[str, Any])
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Unfollow a user"""
    try:
        social_service = SocialTradingService(db)
        success = social_service.unfollow_user(current_user.id, user_id)

        return {
            "status": "success",
            "data": {"unfollowed": success},
            "message": "User unfollowed successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unfollow user: {str(e)}"
        )


@router.get("/followers", response_model=Dict[str, Any])
async def get_followers(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of followers"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's followers"""
    try:
        social_service = SocialTradingService(db)
        followers = social_service.get_followers(current_user.id, limit)

        followers_data = []
        for follower in followers:
            followers_data.append({
                "id": follower.id,
                "user_id": follower.user_id,
                "display_name": follower.display_name,
                "profile_image_url": follower.profile_image_url,
                "bio": follower.bio,
                "investment_style": follower.investment_style,
                "followers_count": follower.followers_count,
                "is_verified": follower.is_verified,
                "reputation_score": follower.reputation_score
            })

        return {
            "status": "success",
            "data": {
                "followers": followers_data,
                "followers_count": len(followers_data)
            },
            "message": f"Retrieved {len(followers_data)} followers"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get followers: {str(e)}"
        )


@router.get("/following", response_model=Dict[str, Any])
async def get_following(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of following"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get users that current user is following"""
    try:
        social_service = SocialTradingService(db)
        following = social_service.get_following(current_user.id, limit)

        following_data = []
        for user in following:
            following_data.append({
                "id": user.id,
                "user_id": user.user_id,
                "display_name": user.display_name,
                "profile_image_url": user.profile_image_url,
                "bio": user.bio,
                "investment_style": user.investment_style,
                "followers_count": user.followers_count,
                "is_verified": user.is_verified,
                "reputation_score": user.reputation_score
            })

        return {
            "status": "success",
            "data": {
                "following": following_data,
                "following_count": len(following_data)
            },
            "message": f"Retrieved {len(following_data)} following"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get following: {str(e)}"
        )


# Social Posts Endpoints
@router.post("/posts", response_model=Dict[str, Any])
async def create_post(
    post_data: SocialPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a social post"""
    try:
        social_service = SocialTradingService(db)
        post = social_service.create_post(current_user.id, post_data.dict())

        return {
            "status": "success",
            "data": {
                "id": post.id,
                "post_type": post.post_type.value,
                "title": post.title,
                "content": post.content,
                "visibility": post.visibility.value,
                "mentioned_stocks": post.mentioned_stocks,
                "target_price": post.target_price,
                "risk_level": post.risk_level,
                "views_count": post.views_count,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "published_at": post.published_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "display_name": post.author.display_name,
                    "profile_image_url": post.author.profile_image_url,
                    "is_verified": post.author.is_verified
                }
            },
            "message": "Post created successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@router.get("/posts/{post_id}", response_model=Dict[str, Any])
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific post"""
    try:
        social_service = SocialTradingService(db)
        post = social_service.get_post(post_id, current_user.id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or not accessible"
            )

        return {
            "status": "success",
            "data": {
                "id": post.id,
                "post_type": post.post_type.value,
                "title": post.title,
                "content": post.content,
                "image_urls": post.image_urls,
                "video_url": post.video_url,
                "mentioned_stocks": post.mentioned_stocks,
                "mentioned_portfolios": post.mentioned_portfolios,
                "investment_thesis": post.investment_thesis,
                "target_price": post.target_price,
                "risk_level": post.risk_level,
                "visibility": post.visibility.value,
                "allow_comments": post.allow_comments,
                "allow_reactions": post.allow_reactions,
                "views_count": post.views_count,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count,
                "tags": post.tags,
                "hashtags": post.hashtags,
                "published_at": post.published_at.isoformat(),
                "edited_at": post.edited_at.isoformat() if post.edited_at else None,
                "author": {
                    "id": post.author.id,
                    "user_id": post.author.user_id,
                    "display_name": post.author.display_name,
                    "profile_image_url": post.author.profile_image_url,
                    "is_verified": post.author.is_verified,
                    "reputation_score": post.author.reputation_score
                }
            },
            "message": "Post retrieved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get post: {str(e)}"
        )


@router.get("/posts/user/{user_id}", response_model=Dict[str, Any])
async def get_user_posts(
    user_id: int,
    limit: int = Query(20, ge=1, le=50, description="Maximum number of posts"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get posts by a specific user"""
    try:
        social_service = SocialTradingService(db)
        posts = social_service.get_user_posts(user_id, current_user.id, limit, offset)

        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "post_type": post.post_type.value,
                "title": post.title,
                "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                "mentioned_stocks": post.mentioned_stocks,
                "target_price": post.target_price,
                "risk_level": post.risk_level,
                "views_count": post.views_count,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "published_at": post.published_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "display_name": post.author.display_name,
                    "profile_image_url": post.author.profile_image_url,
                    "is_verified": post.author.is_verified
                }
            })

        return {
            "status": "success",
            "data": {
                "posts": posts_data,
                "posts_count": len(posts_data),
                "has_more": len(posts_data) == limit
            },
            "message": f"Retrieved {len(posts_data)} posts"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user posts: {str(e)}"
        )


@router.get("/feed", response_model=Dict[str, Any])
async def get_feed(
    limit: int = Query(20, ge=1, le=50, description="Maximum number of posts"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get personalized feed for user"""
    try:
        social_service = SocialTradingService(db)
        posts = social_service.get_feed(current_user.id, limit, offset)

        feed_data = []
        for post in posts:
            feed_data.append({
                "id": post.id,
                "post_type": post.post_type.value,
                "title": post.title,
                "content": post.content[:300] + "..." if len(post.content) > 300 else post.content,
                "image_urls": post.image_urls,
                "mentioned_stocks": post.mentioned_stocks,
                "investment_thesis": post.investment_thesis[:200] + "..." if post.investment_thesis and len(post.investment_thesis) > 200 else post.investment_thesis,
                "target_price": post.target_price,
                "risk_level": post.risk_level,
                "views_count": post.views_count,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count,
                "published_at": post.published_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "user_id": post.author.user_id,
                    "display_name": post.author.display_name,
                    "profile_image_url": post.author.profile_image_url,
                    "is_verified": post.author.is_verified,
                    "reputation_score": post.author.reputation_score
                }
            })

        return {
            "status": "success",
            "data": {
                "feed": feed_data,
                "posts_count": len(feed_data),
                "has_more": len(feed_data) == limit
            },
            "message": f"Retrieved {len(feed_data)} posts in feed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feed: {str(e)}"
        )


@router.post("/posts/{post_id}/react", response_model=Dict[str, Any])
async def react_to_post(
    post_id: int,
    reaction_type: str = Query(..., description="Reaction type: like, love, insightful, disagree, bullish, bearish"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """React to a post"""
    try:
        social_service = SocialTradingService(db)
        reaction = social_service.react_to_post(current_user.id, post_id, reaction_type)

        return {
            "status": "success",
            "data": {
                "id": reaction.id,
                "post_id": reaction.post_id,
                "reaction_type": reaction.reaction_type.value,
                "created_at": reaction.created_at.isoformat()
            },
            "message": "Reaction added successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to react to post: {str(e)}"
        )


@router.post("/posts/{post_id}/comment", response_model=Dict[str, Any])
async def comment_on_post(
    post_id: int,
    content: str = Query(..., max_length=1000, description="Comment content"),
    parent_comment_id: Optional[int] = Query(None, description="Parent comment ID for replies"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Comment on a post"""
    try:
        social_service = SocialTradingService(db)
        comment = social_service.comment_on_post(current_user.id, post_id, content, parent_comment_id)

        return {
            "status": "success",
            "data": {
                "id": comment.id,
                "post_id": comment.post_id,
                "content": comment.content,
                "parent_comment_id": comment.parent_comment_id,
                "likes_count": comment.likes_count,
                "replies_count": comment.replies_count,
                "created_at": comment.created_at.isoformat(),
                "author": {
                    "id": comment.author.id,
                    "display_name": comment.author.display_name,
                    "profile_image_url": comment.author.profile_image_url,
                    "is_verified": comment.author.is_verified
                }
            },
            "message": "Comment added successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to comment on post: {str(e)}"
        )


# Investment Ideas Endpoints
@router.post("/ideas", response_model=Dict[str, Any])
async def create_investment_idea(
    idea_data: InvestmentIdeaCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create an investment idea"""
    try:
        social_service = SocialTradingService(db)
        idea = social_service.create_investment_idea(current_user.id, idea_data.dict())

        return {
            "status": "success",
            "data": {
                "id": idea.id,
                "stock_symbol": idea.stock_symbol,
                "stock_name": idea.stock_name,
                "recommendation": idea.recommendation,
                "current_price": idea.current_price,
                "target_price": idea.target_price,
                "stop_loss_price": idea.stop_loss_price,
                "investment_thesis": idea.investment_thesis,
                "key_catalysts": idea.key_catalysts,
                "risks": idea.risks,
                "time_horizon": idea.time_horizon,
                "suggested_allocation": idea.suggested_allocation,
                "followers_count": idea.followers_count,
                "idea_performance": idea.idea_performance,
                "post_id": idea.post_id,
                "created_at": idea.created_at.isoformat(),
                "author": {
                    "id": idea.author.id,
                    "display_name": idea.author.display_name,
                    "profile_image_url": idea.author.profile_image_url,
                    "is_verified": idea.author.is_verified
                }
            },
            "message": "Investment idea created successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create investment idea: {str(e)}"
        )


@router.get("/ideas", response_model=Dict[str, Any])
async def get_investment_ideas(
    symbol: Optional[str] = Query(None, description="Filter by stock symbol"),
    recommendation: Optional[str] = Query(None, description="Filter by recommendation: buy, sell, hold"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of ideas"),
    offset: int = Query(0, ge=0, description="Number of ideas to skip"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get investment ideas with filters"""
    try:
        social_service = SocialTradingService(db)
        ideas = social_service.get_investment_ideas(symbol, recommendation, author_id, limit, offset)

        ideas_data = []
        for idea in ideas:
            ideas_data.append({
                "id": idea.id,
                "stock_symbol": idea.stock_symbol,
                "stock_name": idea.stock_name,
                "recommendation": idea.recommendation,
                "current_price": idea.current_price,
                "target_price": idea.target_price,
                "stop_loss_price": idea.stop_loss_price,
                "investment_thesis": idea.investment_thesis[:200] + "..." if len(idea.investment_thesis) > 200 else idea.investment_thesis,
                "time_horizon": idea.time_horizon,
                "suggested_allocation": idea.suggested_allocation,
                "followers_count": idea.followers_count,
                "idea_performance": idea.idea_performance,
                "success_rate": idea.success_rate,
                "created_at": idea.created_at.isoformat(),
                "author": {
                    "id": idea.author.id,
                    "display_name": idea.author.display_name,
                    "profile_image_url": idea.author.profile_image_url,
                    "is_verified": idea.author.is_verified,
                    "reputation_score": idea.author.reputation_score
                }
            })

        return {
            "status": "success",
            "data": {
                "ideas": ideas_data,
                "ideas_count": len(ideas_data),
                "has_more": len(ideas_data) == limit
            },
            "message": f"Retrieved {len(ideas_data)} investment ideas"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get investment ideas: {str(e)}"
        )


@router.post("/ideas/{idea_id}/follow", response_model=Dict[str, Any])
async def follow_investment_idea(
    idea_id: int,
    investment_amount: Optional[float] = Query(None, ge=0, description="Investment amount"),
    entry_price: Optional[float] = Query(None, gt=0, description="Entry price"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Follow an investment idea"""
    try:
        social_service = SocialTradingService(db)
        idea_follow = social_service.follow_investment_idea(
            current_user.id, idea_id, investment_amount, entry_price
        )

        return {
            "status": "success",
            "data": {
                "id": idea_follow.id,
                "idea_id": idea_follow.idea_id,
                "investment_amount": idea_follow.investment_amount,
                "entry_price": idea_follow.entry_price,
                "follow_date": idea_follow.follow_date.isoformat(),
                "is_active": idea_follow.is_active
            },
            "message": "Investment idea followed successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to follow investment idea: {str(e)}"
        )


# Community Groups Endpoints
@router.post("/groups", response_model=Dict[str, Any])
async def create_community_group(
    group_data: CommunityGroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a community group"""
    try:
        social_service = SocialTradingService(db)
        group = social_service.create_community_group(current_user.id, group_data.dict())

        return {
            "status": "success",
            "data": {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "group_image_url": group.group_image_url,
                "is_public": group.is_public,
                "requires_approval": group.requires_approval,
                "allow_member_posts": group.allow_member_posts,
                "category": group.category,
                "tags": group.tags,
                "members_count": group.members_count,
                "posts_count": group.posts_count,
                "created_at": group.created_at.isoformat(),
                "creator": {
                    "id": group.creator.id,
                    "display_name": group.creator.display_name,
                    "profile_image_url": group.creator.profile_image_url,
                    "is_verified": group.creator.is_verified
                }
            },
            "message": "Community group created successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create community group: {str(e)}"
        )


@router.get("/groups", response_model=Dict[str, Any])
async def get_community_groups(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_public: bool = Query(True, description="Filter by public/private groups"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of groups"),
    offset: int = Query(0, ge=0, description="Number of groups to skip"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get community groups"""
    try:
        social_service = SocialTradingService(db)
        groups = social_service.get_community_groups(category, is_public, limit, offset)

        groups_data = []
        for group in groups:
            groups_data.append({
                "id": group.id,
                "name": group.name,
                "description": group.description[:200] + "..." if group.description and len(group.description) > 200 else group.description,
                "group_image_url": group.group_image_url,
                "is_public": group.is_public,
                "category": group.category,
                "tags": group.tags,
                "members_count": group.members_count,
                "posts_count": group.posts_count,
                "created_at": group.created_at.isoformat(),
                "creator": {
                    "id": group.creator.id,
                    "display_name": group.creator.display_name,
                    "profile_image_url": group.creator.profile_image_url,
                    "is_verified": group.creator.is_verified
                }
            })

        return {
            "status": "success",
            "data": {
                "groups": groups_data,
                "groups_count": len(groups_data),
                "has_more": len(groups_data) == limit
            },
            "message": f"Retrieved {len(groups_data)} community groups"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get community groups: {str(e)}"
        )


@router.post("/groups/{group_id}/join", response_model=Dict[str, Any])
async def join_community_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Join a community group"""
    try:
        social_service = SocialTradingService(db)
        membership = social_service.join_community_group(current_user.id, group_id)

        return {
            "status": "success",
            "data": {
                "id": membership.id,
                "group_id": membership.group_id,
                "role": membership.role,
                "join_date": membership.join_date.isoformat(),
                "is_active": membership.is_active
            },
            "message": "Joined community group successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join community group: {str(e)}"
        )


@router.get("/groups/my", response_model=Dict[str, Any])
async def get_my_groups(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get groups that user is a member of"""
    try:
        social_service = SocialTradingService(db)
        groups = social_service.get_user_groups(current_user.id)

        groups_data = []
        for group in groups:
            groups_data.append({
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "group_image_url": group.group_image_url,
                "category": group.category,
                "members_count": group.members_count,
                "posts_count": group.posts_count,
                "created_at": group.created_at.isoformat()
            })

        return {
            "status": "success",
            "data": {
                "groups": groups_data,
                "groups_count": len(groups_data)
            },
            "message": f"Retrieved {len(groups_data)} user groups"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user groups: {str(e)}"
        )


# Discovery and Search Endpoints
@router.get("/search/users", response_model=Dict[str, Any])
async def search_users(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of users"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Search for users"""
    try:
        social_service = SocialTradingService(db)
        users = social_service.search_users(query, limit)

        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "user_id": user.user_id,
                "display_name": user.display_name,
                "bio": user.bio,
                "profile_image_url": user.profile_image_url,
                "investment_style": user.investment_style,
                "followers_count": user.followers_count,
                "posts_count": user.posts_count,
                "is_verified": user.is_verified,
                "reputation_score": user.reputation_score,
                "is_following": social_service.is_following(current_user.id, user.user_id)
            })

        return {
            "status": "success",
            "data": {
                "users": users_data,
                "users_count": len(users_data)
            },
            "message": f"Found {len(users_data)} users matching '{query}'"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )


@router.get("/search/posts", response_model=Dict[str, Any])
async def search_posts(
    query: str = Query(..., min_length=2, description="Search query"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of posts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Search for posts"""
    try:
        social_service = SocialTradingService(db)
        posts = social_service.search_posts(query, post_type, limit)

        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "post_type": post.post_type.value,
                "title": post.title,
                "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                "mentioned_stocks": post.mentioned_stocks,
                "target_price": post.target_price,
                "views_count": post.views_count,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "published_at": post.published_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "display_name": post.author.display_name,
                    "profile_image_url": post.author.profile_image_url,
                    "is_verified": post.author.is_verified
                }
            })

        return {
            "status": "success",
            "data": {
                "posts": posts_data,
                "posts_count": len(posts_data)
            },
            "message": f"Found {len(posts_data)} posts matching '{query}'"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search posts: {str(e)}"
        )


@router.get("/trending", response_model=Dict[str, Any])
async def get_trending_posts(
    limit: int = Query(20, ge=1, le=50, description="Maximum number of posts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get trending posts"""
    try:
        social_service = SocialTradingService(db)
        posts = social_service.get_trending_posts(limit)

        trending_data = []
        for post in posts:
            engagement_score = post.likes_count + post.comments_count + post.shares_count
            trending_data.append({
                "id": post.id,
                "post_type": post.post_type.value,
                "title": post.title,
                "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                "mentioned_stocks": post.mentioned_stocks,
                "target_price": post.target_price,
                "views_count": post.views_count,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count,
                "engagement_score": engagement_score,
                "published_at": post.published_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "display_name": post.author.display_name,
                    "profile_image_url": post.author.profile_image_url,
                    "is_verified": post.author.is_verified,
                    "reputation_score": post.author.reputation_score
                }
            })

        return {
            "status": "success",
            "data": {
                "trending_posts": trending_data,
                "posts_count": len(trending_data)
            },
            "message": f"Retrieved {len(trending_data)} trending posts"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending posts: {str(e)}"
        )


@router.get("/top-investors", response_model=Dict[str, Any])
async def get_top_investors(
    limit: int = Query(20, ge=1, le=50, description="Maximum number of investors"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get top performing investors"""
    try:
        social_service = SocialTradingService(db)
        investors = social_service.get_top_investors(limit)

        investors_data = []
        for investor in investors:
            investors_data.append({
                "id": investor.id,
                "user_id": investor.user_id,
                "display_name": investor.display_name,
                "bio": investor.bio,
                "profile_image_url": investor.profile_image_url,
                "investment_style": investor.investment_style,
                "followers_count": investor.followers_count,
                "posts_count": investor.posts_count,
                "total_portfolio_value": investor.total_portfolio_value,
                "total_returns": investor.total_returns,
                "total_returns_percentage": investor.total_returns_percentage,
                "best_performing_stock": investor.best_performing_stock,
                "is_verified": investor.is_verified,
                "reputation_score": investor.reputation_score,
                "is_following": social_service.is_following(current_user.id, investor.user_id)
            })

        return {
            "status": "success",
            "data": {
                "top_investors": investors_data,
                "investors_count": len(investors_data)
            },
            "message": f"Retrieved {len(investors_data)} top investors"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top investors: {str(e)}"
        )
