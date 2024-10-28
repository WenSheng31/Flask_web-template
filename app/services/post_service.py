from typing import Tuple, Optional, Any, List
from datetime import datetime, timedelta
from sqlalchemy import or_, func
from flask import current_app
from app import db
from app.models import Post
from .base_service import BaseService


class PostService(BaseService):
    """文章服務類"""

    # 配置常量
    DEFAULT_PAGE_SIZE = 10
    EXCERPT_LENGTH = 200

    @staticmethod
    def create_post(user_id: int, title: str, content: str) -> Tuple[Optional[Post], Optional[str]]:
        """
        創建新文章

        Args:
            user_id: 用戶ID
            title: 文章標題
            content: 文章內容

        Returns:
            Tuple[Optional[Post], Optional[str]]: (文章實例, 錯誤訊息)
        """
        try:
            # 驗證輸入
            if not title.strip():
                return None, "標題不能為空"
            if not content.strip():
                return None, "內容不能為空"

            # 創建文章
            post = Post(
                title=title,
                content=content,
                user_id=user_id
            )

            success, error = PostService.save_to_db(post)
            return (post, None) if success else (None, error)

        except Exception as e:
            current_app.logger.error(f"Error creating post: {str(e)}")
            return None, str(e)

    @staticmethod
    def get_post_by_id(post_id: int) -> Optional[Post]:
        """
        通過ID獲取文章

        Args:
            post_id: 文章ID

        Returns:
            Optional[Post]: 文章實例或None
        """
        try:
            return Post.query.get(post_id)
        except Exception as e:
            current_app.logger.error(f"Error getting post: {str(e)}")
            return None

    @classmethod
    def get_posts_page(cls, page: int = 1, per_page: int = None) -> Any:
        """
        獲取分頁的文章列表

        Args:
            page: 頁碼
            per_page: 每頁數量

        Returns:
            分頁對象
        """
        try:
            per_page = per_page or cls.DEFAULT_PAGE_SIZE
            return Post.query.order_by(
                Post.created_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        except Exception as e:
            current_app.logger.error(f"Error getting posts page: {str(e)}")
            return None

    @staticmethod
    def update_post(post_id: int, title: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        更新文章

        Args:
            post_id: 文章ID
            title: 新標題
            content: 新內容

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            # 驗證輸入
            if not title.strip():
                return False, "標題不能為空"
            if not content.strip():
                return False, "內容不能為空"

            post = Post.query.get(post_id)
            if not post:
                return False, "文章不存在"

            # 更新文章
            post.title = title
            post.content = content
            post.updated_at = datetime.utcnow()

            return PostService.commit()

        except Exception as e:
            current_app.logger.error(f"Error updating post: {str(e)}")
            return False, str(e)

    @staticmethod
    def delete_post(post_id: int) -> Tuple[bool, Optional[str]]:
        """
        刪除文章

        Args:
            post_id: 文章ID

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            post = Post.query.get(post_id)
            if not post:
                return False, "文章不存在"

            return PostService.delete_from_db(post)

        except Exception as e:
            current_app.logger.error(f"Error deleting post: {str(e)}")
            return False, str(e)

    @classmethod
    def get_user_posts(cls, user_id: int, page: int = 1, per_page: int = None) -> Any:
        """
        獲取指定用戶的文章列表

        Args:
            user_id: 用戶ID
            page: 頁碼
            per_page: 每頁數量

        Returns:
            分頁對象
        """
        try:
            per_page = per_page or cls.DEFAULT_PAGE_SIZE
            return Post.query.filter_by(
                user_id=user_id
            ).order_by(
                Post.created_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        except Exception as e:
            current_app.logger.error(f"Error getting user posts: {str(e)}")
            return None

    @classmethod
    def search_posts(cls, query: str, page: int = 1, per_page: int = None) -> Any:
        """
        搜索文章

        Args:
            query: 搜索關鍵字
            page: 頁碼
            per_page: 每頁數量

        Returns:
            分頁對象
        """
        try:
            per_page = per_page or cls.DEFAULT_PAGE_SIZE
            return Post.query.filter(
                or_(
                    Post.title.ilike(f'%{query}%'),
                    Post.content.ilike(f'%{query}%')
                )
            ).order_by(
                Post.created_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        except Exception as e:
            current_app.logger.error(f"Error searching posts: {str(e)}")
            return None

    @staticmethod
    def get_latest_posts(limit: int = 5) -> List[Post]:
        """
        獲取最新文章

        Args:
            limit: 限制數量

        Returns:
            List[Post]: 文章列表
        """
        try:
            return Post.query.order_by(
                Post.created_at.desc()
            ).limit(limit).all()
        except Exception as e:
            current_app.logger.error(f"Error getting latest posts: {str(e)}")
            return []

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
            from app.models import Like  # 僅在需要時導入 Like

            since = datetime.utcnow() - timedelta(days=days)
            return Post.query.join(
                Like
            ).filter(
                Post.created_at >= since
            ).group_by(
                Post.id
            ).order_by(
                func.count(Like.id).desc()
            ).limit(limit).all()
        except Exception as e:
            current_app.logger.error(f"Error getting trending posts: {str(e)}")
            return []
