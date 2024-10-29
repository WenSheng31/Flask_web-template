# app/services/stats_service.py
from datetime import datetime, timedelta
from typing import Dict
from flask import current_app
from sqlalchemy import func
from app import db
from app.models import User, Post, Comment, Like
from .base_service import BaseService


class StatsService(BaseService):
    """統計服務類"""

    @staticmethod
    def get_site_statistics() -> Dict:
        """
        獲取網站統計數據
        Returns:
            Dict: 包含網站統計資訊的字典
        """
        try:
            # 計算本月新增用戶
            first_day_of_month = datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            # 使用者統計
            total_users = User.query.count()
            new_users_this_month = User.query.filter(
                User.created_at >= first_day_of_month
            ).count()

            # 文章統計
            total_posts = Post.query.count()

            # 最後更新時間
            latest_updates = []

            latest_user = User.query.order_by(User.created_at.desc()).first()
            if latest_user:
                latest_updates.append(latest_user.created_at)

            latest_post = Post.query.order_by(Post.created_at.desc()).first()
            if latest_post:
                latest_updates.append(latest_post.created_at)

            latest_comment = Comment.query.order_by(Comment.created_at.desc()).first()
            if latest_comment:
                latest_updates.append(latest_comment.created_at)

            latest_like = Like.query.order_by(Like.created_at.desc()).first()
            if latest_like:
                latest_updates.append(latest_like.created_at)

            last_update = max(latest_updates).strftime('%Y-%m-%d %H:%M') if latest_updates else '無資料'

            # 活躍用戶數（30天內有活動的用戶）
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = User.query.filter(
                User.last_login >= thirty_days_ago
            ).count()

            return {
                'total_users': total_users,
                'new_users_this_month': new_users_this_month,
                'total_posts': total_posts,
                'last_update': last_update,
                'active_users_count': active_users
            }

        except Exception as e:
            current_app.logger.error(f"Error getting site statistics: {str(e)}")
            return {
                'total_users': 0,
                'new_users_this_month': 0,
                'total_posts': 0,
                'last_update': '無資料',
                'active_users_count': 0
            }

    @staticmethod
    def get_new_users_count(days: int = 30) -> int:
        """
        獲取指定天數內的新增用戶數
        Args:
            days: 天數
        Returns:
            新增用戶數
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return User.query.filter(User.created_at >= cutoff_date).count()
        except Exception as e:
            current_app.logger.error(f"Error getting new users count: {str(e)}")
            return 0

    @staticmethod
    def get_user_activity_stats(user_id: int) -> Dict:
        """
        獲取指定用戶的活動統計
        Args:
            user_id: 用戶ID
        Returns:
            用戶活動統計資料
        """
        try:
            # 發文統計
            posts_count = Post.query.filter_by(user_id=user_id).count()

            # 留言統計
            comments_count = Comment.query.filter_by(user_id=user_id).count()

            # 獲得的讚
            received_likes = Like.query.join(Post).filter(
                Post.user_id == user_id
            ).count()

            # 最近活動
            last_post = Post.query.filter_by(user_id=user_id).order_by(
                Post.created_at.desc()
            ).first()

            last_comment = Comment.query.filter_by(user_id=user_id).order_by(
                Comment.created_at.desc()
            ).first()

            return {
                'posts_count': posts_count,
                'comments_count': comments_count,
                'received_likes': received_likes,
                'last_post_date': last_post.created_at if last_post else None,
                'last_comment_date': last_comment.created_at if last_comment else None
            }
        except Exception as e:
            current_app.logger.error(f"Error getting user activity stats: {str(e)}")
            return {
                'posts_count': 0,
                'comments_count': 0,
                'received_likes': 0,
                'last_post_date': None,
                'last_comment_date': None
            }

    @staticmethod
    def get_trending_content(days: int = 7) -> Dict:
        """
        獲取趨勢內容統計
        Args:
            days: 統計天數
        Returns:
            趨勢統計資料
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # 最熱門文章（按讚數+評論數）
            trending_posts = db.session.query(
                Post,
                func.count(distinct(Like.id)).label('likes_count'),
                func.count(distinct(Comment.id)).label('comments_count')
            ).outerjoin(Like).outerjoin(Comment).filter(
                Post.created_at >= cutoff_date
            ).group_by(Post.id).order_by(
                (func.count(distinct(Like.id)) + func.count(distinct(Comment.id))).desc()
            ).limit(5).all()

            # 活躍用戶（發文數+評論數）
            active_users = db.session.query(
                User,
                func.count(distinct(Post.id)).label('posts_count'),
                func.count(distinct(Comment.id)).label('comments_count')
            ).outerjoin(Post).outerjoin(Comment).filter(
                db.or_(
                    Post.created_at >= cutoff_date,
                    Comment.created_at >= cutoff_date
                )
            ).group_by(User.id).order_by(
                (func.count(distinct(Post.id)) + func.count(distinct(Comment.id))).desc()
            ).limit(5).all()

            return {
                'trending_posts': [
                    {
                        'post': post,
                        'likes': likes,
                        'comments': comments
                    } for post, likes, comments in trending_posts
                ],
                'active_users': [
                    {
                        'user': user,
                        'posts': posts,
                        'comments': comments
                    } for user, posts, comments in active_users
                ]
            }
        except Exception as e:
            current_app.logger.error(f"Error getting trending content: {str(e)}")
            return {
                'trending_posts': [],
                'active_users': []
            }
