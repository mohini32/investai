"""
Social Trading & Community Models - Social features for collaborative investment management
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class FollowStatus(enum.Enum):
    """Follow relationship status"""
    ACTIVE = "active"
    PENDING = "pending"
    BLOCKED = "blocked"
    UNFOLLOWED = "unfollowed"


class PostType(enum.Enum):
    """Types of social posts"""
    INVESTMENT_IDEA = "investment_idea"
    MARKET_ANALYSIS = "market_analysis"
    PORTFOLIO_UPDATE = "portfolio_update"
    EDUCATIONAL_CONTENT = "educational_content"
    QUESTION = "question"
    DISCUSSION = "discussion"
    NEWS_SHARE = "news_share"


class PostVisibility(enum.Enum):
    """Post visibility levels"""
    PUBLIC = "public"
    FOLLOWERS_ONLY = "followers_only"
    PRIVATE = "private"


class ReactionType(enum.Enum):
    """Types of reactions to posts"""
    LIKE = "like"
    LOVE = "love"
    INSIGHTFUL = "insightful"
    DISAGREE = "disagree"
    BULLISH = "bullish"
    BEARISH = "bearish"


class UserProfile(Base):
    """Extended user profile for social features"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Profile information
    display_name = Column(String(100))
    bio = Column(Text)
    profile_image_url = Column(String(500))
    cover_image_url = Column(String(500))
    
    # Social stats
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    
    # Investment stats for social display
    total_portfolio_value = Column(Float, default=0)
    total_returns = Column(Float, default=0)
    total_returns_percentage = Column(Float, default=0)
    best_performing_stock = Column(String(50))
    investment_style = Column(String(50))  # growth, value, dividend, momentum
    
    # Social settings
    is_public_profile = Column(Boolean, default=True)
    allow_portfolio_sharing = Column(Boolean, default=False)
    allow_direct_messages = Column(Boolean, default=True)
    show_performance_stats = Column(Boolean, default=True)
    
    # Verification and reputation
    is_verified = Column(Boolean, default=False)
    reputation_score = Column(Float, default=0)
    expertise_areas = Column(Text)  # JSON array of expertise areas
    
    # Activity tracking
    last_active_at = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    posts = relationship("SocialPost", back_populates="author", cascade="all, delete-orphan")
    followers = relationship("UserFollow", foreign_keys="UserFollow.following_id", back_populates="following")
    following = relationship("UserFollow", foreign_keys="UserFollow.follower_id", back_populates="follower")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, display_name='{self.display_name}')>"


class UserFollow(Base):
    """User follow relationships"""
    __tablename__ = "user_follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    
    # Follow details
    status = Column(Enum(FollowStatus), nullable=False, default=FollowStatus.ACTIVE)
    follow_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    unfollow_date = Column(DateTime(timezone=True))
    
    # Notification settings
    notify_on_posts = Column(Boolean, default=True)
    notify_on_portfolio_updates = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    follower = relationship("UserProfile", foreign_keys=[follower_id], back_populates="following")
    following = relationship("UserProfile", foreign_keys=[following_id], back_populates="followers")
    
    def __repr__(self):
        return f"<UserFollow(id={self.id}, follower_id={self.follower_id}, following_id={self.following_id})>"


class SocialPost(Base):
    """Social posts and content sharing"""
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    
    # Post content
    post_type = Column(Enum(PostType), nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    
    # Media attachments
    image_urls = Column(Text)  # JSON array of image URLs
    video_url = Column(String(500))
    
    # Investment-related data
    mentioned_stocks = Column(Text)  # JSON array of stock symbols
    mentioned_portfolios = Column(Text)  # JSON array of portfolio IDs
    investment_thesis = Column(Text)
    target_price = Column(Float)
    risk_level = Column(String(20))  # low, medium, high
    
    # Post settings
    visibility = Column(Enum(PostVisibility), nullable=False, default=PostVisibility.PUBLIC)
    allow_comments = Column(Boolean, default=True)
    allow_reactions = Column(Boolean, default=True)
    
    # Engagement metrics
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Content moderation
    is_flagged = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    moderation_notes = Column(Text)
    
    # SEO and discovery
    tags = Column(Text)  # JSON array of tags
    hashtags = Column(Text)  # JSON array of hashtags
    
    # Timestamps
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    edited_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("UserProfile", back_populates="posts")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("PostReaction", back_populates="post", cascade="all, delete-orphan")
    shares = relationship("PostShare", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SocialPost(id={self.id}, type='{self.post_type}', author_id={self.author_id})>"


class PostComment(Base):
    """Comments on social posts"""
    __tablename__ = "post_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    parent_comment_id = Column(Integer, ForeignKey("post_comments.id"), index=True)  # For nested comments
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    replies_count = Column(Integer, default=0)
    
    # Content moderation
    is_flagged = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("SocialPost", back_populates="comments")
    author = relationship("UserProfile")
    parent_comment = relationship("PostComment", remote_side=[id])
    replies = relationship("PostComment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PostComment(id={self.id}, post_id={self.post_id}, author_id={self.author_id})>"


class PostReaction(Base):
    """Reactions to social posts"""
    __tablename__ = "post_reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    
    # Reaction details
    reaction_type = Column(Enum(ReactionType), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("SocialPost", back_populates="reactions")
    user = relationship("UserProfile")
    
    def __repr__(self):
        return f"<PostReaction(id={self.id}, type='{self.reaction_type}', post_id={self.post_id})>"


class PostShare(Base):
    """Post sharing tracking"""
    __tablename__ = "post_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    
    # Share details
    share_message = Column(Text)
    share_platform = Column(String(50))  # internal, twitter, linkedin, whatsapp
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("SocialPost", back_populates="shares")
    user = relationship("UserProfile")
    
    def __repr__(self):
        return f"<PostShare(id={self.id}, post_id={self.post_id}, platform='{self.share_platform}')>"


class InvestmentIdea(Base):
    """Investment ideas shared by users"""
    __tablename__ = "investment_ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), index=True)
    
    # Investment details
    stock_symbol = Column(String(50), nullable=False, index=True)
    stock_name = Column(String(255), nullable=False)
    recommendation = Column(String(20), nullable=False)  # buy, sell, hold
    
    # Price targets
    current_price = Column(Float, nullable=False)
    target_price = Column(Float)
    stop_loss_price = Column(Float)
    
    # Investment thesis
    investment_thesis = Column(Text, nullable=False)
    key_catalysts = Column(Text)  # JSON array
    risks = Column(Text)  # JSON array
    
    # Time horizon and allocation
    time_horizon = Column(String(20))  # short_term, medium_term, long_term
    suggested_allocation = Column(Float)  # Percentage of portfolio
    
    # Performance tracking
    idea_performance = Column(Float, default=0)  # Performance since idea posted
    is_active = Column(Boolean, default=True)
    
    # Engagement metrics
    followers_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("UserProfile")
    post = relationship("SocialPost")
    followers = relationship("IdeaFollower", back_populates="idea", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InvestmentIdea(id={self.id}, symbol='{self.stock_symbol}', recommendation='{self.recommendation}')>"


class IdeaFollower(Base):
    """Users following investment ideas"""
    __tablename__ = "idea_followers"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("investment_ideas.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    
    # Following details
    follow_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    investment_amount = Column(Float)  # Amount invested based on idea
    entry_price = Column(Float)  # Price at which user entered
    
    # Status
    is_active = Column(Boolean, default=True)
    exit_date = Column(DateTime(timezone=True))
    exit_price = Column(Float)
    realized_return = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    idea = relationship("InvestmentIdea", back_populates="followers")
    user = relationship("UserProfile")
    
    def __repr__(self):
        return f"<IdeaFollower(id={self.id}, idea_id={self.idea_id}, user_id={self.user_id})>"


class CommunityGroup(Base):
    """Investment community groups"""
    __tablename__ = "community_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    
    # Group details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    group_image_url = Column(String(500))
    
    # Group settings
    is_public = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    allow_member_posts = Column(Boolean, default=True)
    
    # Group stats
    members_count = Column(Integer, default=1)  # Creator is first member
    posts_count = Column(Integer, default=0)
    
    # Group categories
    category = Column(String(50))  # stocks, mutual_funds, crypto, general
    tags = Column(Text)  # JSON array of tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("UserProfile")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CommunityGroup(id={self.id}, name='{self.name}', members={self.members_count})>"


class GroupMember(Base):
    """Community group memberships"""
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("community_groups.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    
    # Membership details
    role = Column(String(20), default="member")  # creator, admin, moderator, member
    join_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    is_muted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("CommunityGroup", back_populates="members")
    user = relationship("UserProfile")
    
    def __repr__(self):
        return f"<GroupMember(id={self.id}, group_id={self.group_id}, user_id={self.user_id}, role='{self.role}')>"
