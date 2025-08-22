"""
Social Trading Service - Comprehensive social trading and community features
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json
import logging

from app.models.social import (
    UserProfile, UserFollow, SocialPost, PostComment, PostReaction, PostShare,
    InvestmentIdea, IdeaFollower, CommunityGroup, GroupMember,
    FollowStatus, PostType, PostVisibility, ReactionType
)
from app.models.user import User
from app.models.portfolio import Portfolio

logger = logging.getLogger(__name__)


class SocialTradingService:
    """Service for social trading and community features"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User Profile Management
    def create_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> UserProfile:
        """Create social profile for user"""
        try:
            # Check if profile already exists
            existing_profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if existing_profile:
                raise ValueError("User profile already exists")
            
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                display_name=profile_data.get("display_name"),
                bio=profile_data.get("bio"),
                profile_image_url=profile_data.get("profile_image_url"),
                cover_image_url=profile_data.get("cover_image_url"),
                investment_style=profile_data.get("investment_style", "balanced"),
                is_public_profile=profile_data.get("is_public_profile", True),
                allow_portfolio_sharing=profile_data.get("allow_portfolio_sharing", False),
                allow_direct_messages=profile_data.get("allow_direct_messages", True),
                show_performance_stats=profile_data.get("show_performance_stats", True),
                expertise_areas=json.dumps(profile_data.get("expertise_areas", [])),
                last_active_at=datetime.now()
            )
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            # Update investment stats
            self._update_profile_investment_stats(profile.id)
            
            logger.info(f"Created social profile {profile.id} for user {user_id}")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create user profile: {str(e)}")
            raise
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> UserProfile:
        """Update user profile"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")
            
            # Update fields
            for field, value in profile_data.items():
                if hasattr(profile, field):
                    if field == "expertise_areas" and isinstance(value, list):
                        setattr(profile, field, json.dumps(value))
                    else:
                        setattr(profile, field, value)
            
            profile.last_active_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Updated user profile {profile.id}")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update user profile: {str(e)}")
            raise
    
    def _update_profile_investment_stats(self, profile_id: int):
        """Update profile investment statistics"""
        try:
            profile = self.db.query(UserProfile).filter(UserProfile.id == profile_id).first()
            if not profile:
                return
            
            # Get user's portfolios
            portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == profile.user_id).all()
            
            if portfolios:
                total_value = sum(p.total_value or 0 for p in portfolios)
                total_invested = sum(p.total_invested or 0 for p in portfolios)
                total_returns = total_value - total_invested
                total_returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0
                
                profile.total_portfolio_value = total_value
                profile.total_returns = total_returns
                profile.total_returns_percentage = total_returns_percentage
                
                # Find best performing stock (simplified)
                profile.best_performing_stock = "RELIANCE"  # Would be calculated from actual holdings
                
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Failed to update profile investment stats: {str(e)}")
    
    # Follow System
    def follow_user(self, follower_user_id: int, following_user_id: int) -> UserFollow:
        """Follow another user"""
        try:
            if follower_user_id == following_user_id:
                raise ValueError("Cannot follow yourself")
            
            # Get profiles
            follower_profile = self.get_user_profile(follower_user_id)
            following_profile = self.get_user_profile(following_user_id)
            
            if not follower_profile or not following_profile:
                raise ValueError("User profile not found")
            
            # Check if already following
            existing_follow = self.db.query(UserFollow).filter(
                and_(
                    UserFollow.follower_id == follower_profile.id,
                    UserFollow.following_id == following_profile.id,
                    UserFollow.status == FollowStatus.ACTIVE
                )
            ).first()
            
            if existing_follow:
                raise ValueError("Already following this user")
            
            # Create follow relationship
            follow = UserFollow(
                follower_id=follower_profile.id,
                following_id=following_profile.id,
                status=FollowStatus.ACTIVE,
                follow_date=datetime.now()
            )
            
            self.db.add(follow)
            
            # Update counts
            follower_profile.following_count += 1
            following_profile.followers_count += 1
            
            self.db.commit()
            self.db.refresh(follow)
            
            logger.info(f"User {follower_user_id} followed user {following_user_id}")
            return follow
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to follow user: {str(e)}")
            raise
    
    def unfollow_user(self, follower_user_id: int, following_user_id: int) -> bool:
        """Unfollow a user"""
        try:
            # Get profiles
            follower_profile = self.get_user_profile(follower_user_id)
            following_profile = self.get_user_profile(following_user_id)
            
            if not follower_profile or not following_profile:
                raise ValueError("User profile not found")
            
            # Find follow relationship
            follow = self.db.query(UserFollow).filter(
                and_(
                    UserFollow.follower_id == follower_profile.id,
                    UserFollow.following_id == following_profile.id,
                    UserFollow.status == FollowStatus.ACTIVE
                )
            ).first()
            
            if not follow:
                raise ValueError("Not following this user")
            
            # Update follow status
            follow.status = FollowStatus.UNFOLLOWED
            follow.unfollow_date = datetime.now()
            
            # Update counts
            follower_profile.following_count = max(0, follower_profile.following_count - 1)
            following_profile.followers_count = max(0, following_profile.followers_count - 1)
            
            self.db.commit()
            
            logger.info(f"User {follower_user_id} unfollowed user {following_user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to unfollow user: {str(e)}")
            raise
    
    def get_followers(self, user_id: int, limit: int = 50) -> List[UserProfile]:
        """Get user's followers"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return []
        
        followers = self.db.query(UserProfile).join(
            UserFollow, UserProfile.id == UserFollow.follower_id
        ).filter(
            and_(
                UserFollow.following_id == profile.id,
                UserFollow.status == FollowStatus.ACTIVE
            )
        ).limit(limit).all()
        
        return followers
    
    def get_following(self, user_id: int, limit: int = 50) -> List[UserProfile]:
        """Get users that user is following"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return []
        
        following = self.db.query(UserProfile).join(
            UserFollow, UserProfile.id == UserFollow.following_id
        ).filter(
            and_(
                UserFollow.follower_id == profile.id,
                UserFollow.status == FollowStatus.ACTIVE
            )
        ).limit(limit).all()
        
        return following
    
    def is_following(self, follower_user_id: int, following_user_id: int) -> bool:
        """Check if user is following another user"""
        follower_profile = self.get_user_profile(follower_user_id)
        following_profile = self.get_user_profile(following_user_id)
        
        if not follower_profile or not following_profile:
            return False
        
        follow = self.db.query(UserFollow).filter(
            and_(
                UserFollow.follower_id == follower_profile.id,
                UserFollow.following_id == following_profile.id,
                UserFollow.status == FollowStatus.ACTIVE
            )
        ).first()
        
        return follow is not None
    
    # Social Posts
    def create_post(self, user_id: int, post_data: Dict[str, Any]) -> SocialPost:
        """Create a social post"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")
            
            # Create post
            post = SocialPost(
                author_id=profile.id,
                post_type=PostType(post_data["post_type"]),
                title=post_data.get("title"),
                content=post_data["content"],
                image_urls=json.dumps(post_data.get("image_urls", [])),
                video_url=post_data.get("video_url"),
                mentioned_stocks=json.dumps(post_data.get("mentioned_stocks", [])),
                mentioned_portfolios=json.dumps(post_data.get("mentioned_portfolios", [])),
                investment_thesis=post_data.get("investment_thesis"),
                target_price=post_data.get("target_price"),
                risk_level=post_data.get("risk_level"),
                visibility=PostVisibility(post_data.get("visibility", "public")),
                allow_comments=post_data.get("allow_comments", True),
                allow_reactions=post_data.get("allow_reactions", True),
                tags=json.dumps(post_data.get("tags", [])),
                hashtags=json.dumps(post_data.get("hashtags", []))
            )
            
            self.db.add(post)
            
            # Update profile post count
            profile.posts_count += 1
            
            self.db.commit()
            self.db.refresh(post)
            
            logger.info(f"Created post {post.id} by user {user_id}")
            return post
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create post: {str(e)}")
            raise
    
    def get_post(self, post_id: int, viewer_user_id: Optional[int] = None) -> Optional[SocialPost]:
        """Get a social post"""
        post = self.db.query(SocialPost).filter(SocialPost.id == post_id).first()
        
        if not post:
            return None
        
        # Check visibility permissions
        if post.visibility == PostVisibility.PRIVATE:
            if not viewer_user_id or post.author.user_id != viewer_user_id:
                return None
        elif post.visibility == PostVisibility.FOLLOWERS_ONLY:
            if not viewer_user_id:
                return None
            if post.author.user_id != viewer_user_id:
                # Check if viewer is following the author
                if not self.is_following(viewer_user_id, post.author.user_id):
                    return None
        
        # Increment view count
        post.views_count += 1
        self.db.commit()
        
        return post
    
    def get_user_posts(self, user_id: int, viewer_user_id: Optional[int] = None, 
                      limit: int = 20, offset: int = 0) -> List[SocialPost]:
        """Get posts by a user"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return []
        
        query = self.db.query(SocialPost).filter(SocialPost.author_id == profile.id)
        
        # Apply visibility filters
        if not viewer_user_id or user_id != viewer_user_id:
            if viewer_user_id and self.is_following(viewer_user_id, user_id):
                # Viewer is following, can see public and followers_only posts
                query = query.filter(SocialPost.visibility.in_([PostVisibility.PUBLIC, PostVisibility.FOLLOWERS_ONLY]))
            else:
                # Only public posts
                query = query.filter(SocialPost.visibility == PostVisibility.PUBLIC)
        
        posts = query.order_by(desc(SocialPost.published_at)).offset(offset).limit(limit).all()
        return posts
    
    def get_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> List[SocialPost]:
        """Get personalized feed for user"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return []
        
        # Get posts from followed users
        following_ids = [f.following_id for f in self.db.query(UserFollow).filter(
            and_(
                UserFollow.follower_id == profile.id,
                UserFollow.status == FollowStatus.ACTIVE
            )
        ).all()]
        
        # Include user's own posts
        following_ids.append(profile.id)
        
        if not following_ids:
            # If not following anyone, show public posts
            posts = self.db.query(SocialPost).filter(
                SocialPost.visibility == PostVisibility.PUBLIC
            ).order_by(desc(SocialPost.published_at)).offset(offset).limit(limit).all()
        else:
            posts = self.db.query(SocialPost).filter(
                and_(
                    SocialPost.author_id.in_(following_ids),
                    SocialPost.visibility.in_([PostVisibility.PUBLIC, PostVisibility.FOLLOWERS_ONLY])
                )
            ).order_by(desc(SocialPost.published_at)).offset(offset).limit(limit).all()
        
        return posts
    
    def react_to_post(self, user_id: int, post_id: int, reaction_type: str) -> PostReaction:
        """React to a post"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")
            
            post = self.db.query(SocialPost).filter(SocialPost.id == post_id).first()
            if not post:
                raise ValueError("Post not found")
            
            if not post.allow_reactions:
                raise ValueError("Reactions not allowed on this post")
            
            # Check if user already reacted
            existing_reaction = self.db.query(PostReaction).filter(
                and_(
                    PostReaction.post_id == post_id,
                    PostReaction.user_id == profile.id
                )
            ).first()
            
            if existing_reaction:
                # Update existing reaction
                existing_reaction.reaction_type = ReactionType(reaction_type)
                self.db.commit()
                return existing_reaction
            else:
                # Create new reaction
                reaction = PostReaction(
                    post_id=post_id,
                    user_id=profile.id,
                    reaction_type=ReactionType(reaction_type)
                )
                
                self.db.add(reaction)
                
                # Update post likes count (simplified)
                post.likes_count += 1
                
                self.db.commit()
                self.db.refresh(reaction)
                
                return reaction
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to react to post: {str(e)}")
            raise
    
    def comment_on_post(self, user_id: int, post_id: int, content: str, 
                       parent_comment_id: Optional[int] = None) -> PostComment:
        """Comment on a post"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")
            
            post = self.db.query(SocialPost).filter(SocialPost.id == post_id).first()
            if not post:
                raise ValueError("Post not found")
            
            if not post.allow_comments:
                raise ValueError("Comments not allowed on this post")
            
            # Create comment
            comment = PostComment(
                post_id=post_id,
                author_id=profile.id,
                parent_comment_id=parent_comment_id,
                content=content
            )
            
            self.db.add(comment)
            
            # Update post comments count
            post.comments_count += 1
            
            # Update parent comment replies count if it's a reply
            if parent_comment_id:
                parent_comment = self.db.query(PostComment).filter(
                    PostComment.id == parent_comment_id
                ).first()
                if parent_comment:
                    parent_comment.replies_count += 1
            
            self.db.commit()
            self.db.refresh(comment)
            
            logger.info(f"Created comment {comment.id} on post {post_id}")
            return comment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to comment on post: {str(e)}")
            raise

    # Investment Ideas
    def create_investment_idea(self, user_id: int, idea_data: Dict[str, Any]) -> InvestmentIdea:
        """Create an investment idea"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")

            # Create investment idea
            idea = InvestmentIdea(
                author_id=profile.id,
                stock_symbol=idea_data["stock_symbol"].upper(),
                stock_name=idea_data["stock_name"],
                recommendation=idea_data["recommendation"].lower(),
                current_price=idea_data["current_price"],
                target_price=idea_data.get("target_price"),
                stop_loss_price=idea_data.get("stop_loss_price"),
                investment_thesis=idea_data["investment_thesis"],
                key_catalysts=json.dumps(idea_data.get("key_catalysts", [])),
                risks=json.dumps(idea_data.get("risks", [])),
                time_horizon=idea_data.get("time_horizon", "medium_term"),
                suggested_allocation=idea_data.get("suggested_allocation", 5.0)
            )

            self.db.add(idea)
            self.db.commit()
            self.db.refresh(idea)

            # Create associated social post if requested
            if idea_data.get("create_post", True):
                post_content = f"💡 Investment Idea: {idea.recommendation.upper()} {idea.stock_symbol}\n\n"
                post_content += f"Current Price: ₹{idea.current_price}\n"
                if idea.target_price:
                    post_content += f"Target Price: ₹{idea.target_price}\n"
                post_content += f"\n{idea.investment_thesis}"

                post_data = {
                    "post_type": "investment_idea",
                    "title": f"{idea.recommendation.upper()} {idea.stock_symbol}",
                    "content": post_content,
                    "mentioned_stocks": [idea.stock_symbol],
                    "investment_thesis": idea.investment_thesis,
                    "target_price": idea.target_price,
                    "risk_level": idea_data.get("risk_level", "medium"),
                    "tags": [idea.stock_symbol, idea.recommendation, "investment_idea"],
                    "hashtags": [f"#{idea.stock_symbol}", f"#{idea.recommendation}"]
                }

                post = self.create_post(user_id, post_data)
                idea.post_id = post.id
                self.db.commit()

            logger.info(f"Created investment idea {idea.id} for {idea.stock_symbol}")
            return idea

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create investment idea: {str(e)}")
            raise

    def get_investment_idea(self, idea_id: int) -> Optional[InvestmentIdea]:
        """Get an investment idea"""
        return self.db.query(InvestmentIdea).filter(InvestmentIdea.id == idea_id).first()

    def get_investment_ideas(self, symbol: Optional[str] = None, recommendation: Optional[str] = None,
                           author_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> List[InvestmentIdea]:
        """Get investment ideas with filters"""
        query = self.db.query(InvestmentIdea).filter(InvestmentIdea.is_active == True)

        if symbol:
            query = query.filter(InvestmentIdea.stock_symbol == symbol.upper())

        if recommendation:
            query = query.filter(InvestmentIdea.recommendation == recommendation.lower())

        if author_id:
            query = query.filter(InvestmentIdea.author_id == author_id)

        ideas = query.order_by(desc(InvestmentIdea.created_at)).offset(offset).limit(limit).all()
        return ideas

    def follow_investment_idea(self, user_id: int, idea_id: int, investment_amount: Optional[float] = None,
                             entry_price: Optional[float] = None) -> IdeaFollower:
        """Follow an investment idea"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")

            idea = self.get_investment_idea(idea_id)
            if not idea:
                raise ValueError("Investment idea not found")

            # Check if already following
            existing_follow = self.db.query(IdeaFollower).filter(
                and_(
                    IdeaFollower.idea_id == idea_id,
                    IdeaFollower.user_id == profile.id,
                    IdeaFollower.is_active == True
                )
            ).first()

            if existing_follow:
                raise ValueError("Already following this investment idea")

            # Create idea follow
            idea_follow = IdeaFollower(
                idea_id=idea_id,
                user_id=profile.id,
                investment_amount=investment_amount,
                entry_price=entry_price or idea.current_price
            )

            self.db.add(idea_follow)

            # Update idea followers count
            idea.followers_count += 1

            self.db.commit()
            self.db.refresh(idea_follow)

            logger.info(f"User {user_id} followed investment idea {idea_id}")
            return idea_follow

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to follow investment idea: {str(e)}")
            raise

    def update_idea_performance(self, idea_id: int, current_price: float):
        """Update investment idea performance"""
        try:
            idea = self.get_investment_idea(idea_id)
            if not idea:
                return

            # Calculate performance since idea creation
            performance = (current_price - idea.current_price) / idea.current_price
            idea.idea_performance = performance

            # Update followers' performance
            followers = self.db.query(IdeaFollower).filter(
                and_(
                    IdeaFollower.idea_id == idea_id,
                    IdeaFollower.is_active == True
                )
            ).all()

            for follower in followers:
                if follower.entry_price:
                    follower_performance = (current_price - follower.entry_price) / follower.entry_price
                    # This would be stored in a separate performance tracking table in production

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to update idea performance: {str(e)}")

    # Community Groups
    def create_community_group(self, user_id: int, group_data: Dict[str, Any]) -> CommunityGroup:
        """Create a community group"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")

            # Create group
            group = CommunityGroup(
                creator_id=profile.id,
                name=group_data["name"],
                description=group_data.get("description"),
                group_image_url=group_data.get("group_image_url"),
                is_public=group_data.get("is_public", True),
                requires_approval=group_data.get("requires_approval", False),
                allow_member_posts=group_data.get("allow_member_posts", True),
                category=group_data.get("category", "general"),
                tags=json.dumps(group_data.get("tags", []))
            )

            self.db.add(group)
            self.db.commit()
            self.db.refresh(group)

            # Add creator as first member
            creator_membership = GroupMember(
                group_id=group.id,
                user_id=profile.id,
                role="creator"
            )

            self.db.add(creator_membership)
            self.db.commit()

            logger.info(f"Created community group {group.id}: {group.name}")
            return group

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create community group: {str(e)}")
            raise

    def join_community_group(self, user_id: int, group_id: int) -> GroupMember:
        """Join a community group"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")

            group = self.db.query(CommunityGroup).filter(CommunityGroup.id == group_id).first()
            if not group:
                raise ValueError("Community group not found")

            # Check if already a member
            existing_membership = self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == group_id,
                    GroupMember.user_id == profile.id,
                    GroupMember.is_active == True
                )
            ).first()

            if existing_membership:
                raise ValueError("Already a member of this group")

            # Create membership
            membership = GroupMember(
                group_id=group_id,
                user_id=profile.id,
                role="member"
            )

            self.db.add(membership)

            # Update group members count
            group.members_count += 1

            self.db.commit()
            self.db.refresh(membership)

            logger.info(f"User {user_id} joined community group {group_id}")
            return membership

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to join community group: {str(e)}")
            raise

    def get_community_groups(self, category: Optional[str] = None, is_public: bool = True,
                           limit: int = 20, offset: int = 0) -> List[CommunityGroup]:
        """Get community groups"""
        query = self.db.query(CommunityGroup).filter(CommunityGroup.is_public == is_public)

        if category:
            query = query.filter(CommunityGroup.category == category)

        groups = query.order_by(desc(CommunityGroup.members_count)).offset(offset).limit(limit).all()
        return groups

    def get_user_groups(self, user_id: int) -> List[CommunityGroup]:
        """Get groups that user is a member of"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return []

        groups = self.db.query(CommunityGroup).join(
            GroupMember, CommunityGroup.id == GroupMember.group_id
        ).filter(
            and_(
                GroupMember.user_id == profile.id,
                GroupMember.is_active == True
            )
        ).all()

        return groups

    # Discovery and Search
    def search_users(self, query: str, limit: int = 20) -> List[UserProfile]:
        """Search for users"""
        users = self.db.query(UserProfile).filter(
            and_(
                UserProfile.is_public_profile == True,
                or_(
                    UserProfile.display_name.ilike(f"%{query}%"),
                    UserProfile.bio.ilike(f"%{query}%")
                )
            )
        ).limit(limit).all()

        return users

    def search_posts(self, query: str, post_type: Optional[str] = None,
                    limit: int = 20) -> List[SocialPost]:
        """Search for posts"""
        search_query = self.db.query(SocialPost).filter(
            and_(
                SocialPost.visibility == PostVisibility.PUBLIC,
                or_(
                    SocialPost.title.ilike(f"%{query}%"),
                    SocialPost.content.ilike(f"%{query}%")
                )
            )
        )

        if post_type:
            search_query = search_query.filter(SocialPost.post_type == PostType(post_type))

        posts = search_query.order_by(desc(SocialPost.published_at)).limit(limit).all()
        return posts

    def get_trending_posts(self, limit: int = 20) -> List[SocialPost]:
        """Get trending posts based on engagement"""
        # Simple trending algorithm based on recent engagement
        cutoff_date = datetime.now() - timedelta(days=7)

        posts = self.db.query(SocialPost).filter(
            and_(
                SocialPost.visibility == PostVisibility.PUBLIC,
                SocialPost.published_at >= cutoff_date
            )
        ).order_by(
            desc(SocialPost.likes_count + SocialPost.comments_count + SocialPost.shares_count)
        ).limit(limit).all()

        return posts

    def get_top_investors(self, limit: int = 20) -> List[UserProfile]:
        """Get top performing investors"""
        top_investors = self.db.query(UserProfile).filter(
            and_(
                UserProfile.is_public_profile == True,
                UserProfile.show_performance_stats == True,
                UserProfile.total_returns_percentage.isnot(None)
            )
        ).order_by(desc(UserProfile.total_returns_percentage)).limit(limit).all()

        return top_investors

    # Analytics and Insights
    def get_user_social_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user's social statistics"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {}

        # Get additional stats
        total_likes = self.db.query(func.sum(SocialPost.likes_count)).filter(
            SocialPost.author_id == profile.id
        ).scalar() or 0

        total_comments = self.db.query(func.sum(SocialPost.comments_count)).filter(
            SocialPost.author_id == profile.id
        ).scalar() or 0

        total_views = self.db.query(func.sum(SocialPost.views_count)).filter(
            SocialPost.author_id == profile.id
        ).scalar() or 0

        # Investment ideas stats
        ideas_count = self.db.query(InvestmentIdea).filter(
            InvestmentIdea.author_id == profile.id
        ).count()

        ideas_followers = self.db.query(func.sum(InvestmentIdea.followers_count)).filter(
            InvestmentIdea.author_id == profile.id
        ).scalar() or 0

        return {
            "profile_id": profile.id,
            "followers_count": profile.followers_count,
            "following_count": profile.following_count,
            "posts_count": profile.posts_count,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_views": total_views,
            "investment_ideas_count": ideas_count,
            "ideas_followers_count": ideas_followers,
            "reputation_score": profile.reputation_score,
            "is_verified": profile.is_verified
        }
