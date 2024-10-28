from app import db
from app.models import Like, Post
from .base_service import BaseService
from typing import Tuple, Optional


class LikeService(BaseService):
    @staticmethod
    def toggle_like(user_id: int, post_id: int) -> Tuple[bool, bool, int]:
        """
        切換文章的按讚狀態
        :param user_id: 用戶ID
        :param post_id: 文章ID
        :return: Tuple[是否成功, 當前是否為按讚狀態, 當前按讚數]
        """
        try:
            # 檢查是否已經按讚
            existing_like = Like.query.filter_by(
                post_id=post_id,
                user_id=user_id
            ).first()

            post = Post.query.get(post_id)
            if not post:
                return False, False, 0

            if existing_like:
                # 如果已按讚，則取消
                db.session.delete(existing_like)
                db.session.commit()
                return True, False, post.like_count
            else:
                # 如果未按讚，則添加
                new_like = Like(post_id=post_id, user_id=user_id)
                db.session.add(new_like)
                db.session.commit()
                return True, True, post.like_count
        except Exception as e:
            db.session.rollback()
            return False, False, 0

    @staticmethod
    def is_post_liked_by_user(post_id: int, user_id: int) -> bool:
        """
        檢查用戶是否已對文章按讚
        :param post_id: 文章ID
        :param user_id: 用戶ID
        :return: 是否已按讚
        """
        return Like.query.filter_by(
            post_id=post_id,
            user_id=user_id
        ).first() is not None

    @staticmethod
    def get_post_likes_count(post_id: int) -> int:
        """
        獲取文章的按讚數量
        :param post_id: 文章ID
        :return: 按讚數量
        """
        return Like.query.filter_by(post_id=post_id).count()

    @staticmethod
    def get_user_liked_posts(user_id: int, page: int = 1, per_page: int = 10) -> Tuple[list, int]:
        """
        獲取用戶按讚的文章列表
        :param user_id: 用戶ID
        :param page: 頁碼
        :param per_page: 每頁數量
        :return: Tuple[文章列表, 總頁數]
        """
        pagination = Post.query.join(Like).filter(
            Like.user_id == user_id
        ).order_by(Like.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return pagination.items, pagination.pages

    @staticmethod
    def get_post_likers(post_id: int, page: int = 1, per_page: int = 20) -> list:
        """
        獲取文章的按讚用戶列表
        :param post_id: 文章ID
        :param page: 頁碼
        :param per_page: 每頁數量
        :return: 用戶列表
        """
        from app.models import User
        return User.query.join(Like).filter(
            Like.post_id == post_id
        ).order_by(Like.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
