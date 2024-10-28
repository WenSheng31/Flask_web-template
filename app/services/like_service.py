from typing import Tuple, List, Dict, Optional
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import func
from app import db
from app.models import Like, Post
from .base_service import BaseService


class LikeService(BaseService):
    """按讚服務類"""

    @staticmethod
    def toggle_like(user_id: int, post_id: int) -> Tuple[bool, bool, int]:
        """
        切換文章的按讚狀態

        Args:
            user_id: 用戶ID
            post_id: 文章ID

        Returns:
            Tuple[bool, bool, int]: (是否成功, 當前是否為按讚狀態, 當前按讚數)
        """
        try:
            # 檢查文章是否存在
            post = Post.query.get(post_id)
            if not post:
                return False, False, 0

            # 檢查是否已經按讚
            existing_like = Like.query.filter_by(
                post_id=post_id,
                user_id=user_id
            ).first()

            if existing_like:
                # 取消按讚
                db.session.delete(existing_like)
                db.session.commit()
                return True, False, post.like_count
            else:
                # 新增按讚
                new_like = Like(post_id=post_id, user_id=user_id)
                db.session.add(new_like)
                db.session.commit()
                return True, True, post.like_count

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error toggling like: {str(e)}")
            return False, False, 0

    @staticmethod
    def is_post_liked_by_user(post_id: int, user_id: int) -> bool:
        """
        檢查用戶是否已對文章按讚

        Args:
            post_id: 文章ID
            user_id: 用戶ID

        Returns:
            bool: 是否已按讚
        """
        try:
            return Like.query.filter_by(
                post_id=post_id,
                user_id=user_id
            ).first() is not None
        except Exception as e:
            current_app.logger.error(f"Error checking like status: {str(e)}")
            return False

    @staticmethod
    def get_user_liked_posts(user_id: int, page: int = 1,
                             per_page: int = 10) -> Tuple[List[Post], int]:
        """
        獲取用戶按讚的文章列表

        Args:
            user_id: 用戶ID
            page: 頁碼
            per_page: 每頁數量

        Returns:
            Tuple[List[Post], int]: (文章列表, 總頁數)
        """
        try:
            pagination = Post.query.join(
                Like
            ).filter(
                Like.user_id == user_id
            ).order_by(
                Like.created_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            return pagination.items, pagination.pages
        except Exception as e:
            current_app.logger.error(f"Error getting liked posts: {str(e)}")
            return [], 0

    @staticmethod
    def get_post_likes_statistics(post_id: int) -> Dict:
        """
        獲取文章按讚統計資訊

        Args:
            post_id: 文章ID

        Returns:
            Dict: 統計資訊字典
        """
        try:
            total_likes = Like.query.filter_by(post_id=post_id).count()
            recent_likes = Like.query.filter(
                Like.post_id == post_id,
                Like.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()

            return {
                'total_likes': total_likes,
                'recent_likes': recent_likes,
                'trend': recent_likes / total_likes if total_likes > 0 else 0
            }
        except Exception as e:
            current_app.logger.error(f"Error getting like statistics: {str(e)}")
            return {
                'total_likes': 0,
                'recent_likes': 0,
                'trend': 0
            }

    @staticmethod
    def get_trending_posts(days: int = 7, limit: int = 10) -> List[Post]:
        """
        獲取趨勢文章（根據最近按讚數）

        Args:
            days: 統計天數
            limit: 返回數量

        Returns:
            List[Post]: 趨勢文章列表
        """
        try:
            since = datetime.utcnow() - timedelta(days=days)
            return Post.query.join(
                Like
            ).filter(
                Like.created_at >= since
            ).group_by(
                Post.id
            ).order_by(
                func.count(Like.id).desc()
            ).limit(limit).all()
        except Exception as e:
            current_app.logger.error(f"Error getting trending posts: {str(e)}")
            return []
