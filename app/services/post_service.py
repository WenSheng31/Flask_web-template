from app import db
from app.models import Post
from .base_service import BaseService
from typing import Tuple, Optional, Any
from datetime import datetime
from sqlalchemy import or_


class PostService(BaseService):
    @staticmethod
    def create_post(user_id: int, title: str, content: str) -> Tuple[Optional[Post], Optional[str]]:
        """
        創建新文章
        :param user_id: 用戶ID
        :param title: 文章標題
        :param content: 文章內容
        :return: (Post object, error message)
        """
        try:
            if not title.strip():
                return None, "標題不能為空"
            if not content.strip():
                return None, "內容不能為空"

            post = Post(
                title=title,
                content=content,
                user_id=user_id
            )
            db.session.add(post)
            success, error = PostService.commit()

            if success:
                return post, None
            return None, error
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_post_by_id(post_id: int) -> Optional[Post]:
        """
        通過ID獲取文章
        :param post_id: 文章ID
        :return: Post object or None
        """
        return Post.query.get(post_id)

    @staticmethod
    def get_posts_page(page: int = 1, per_page: int = 10) -> Any:
        """
        獲取分頁的文章列表
        :param page: 頁碼
        :param per_page: 每頁數量
        :return: Pagination object
        """
        return Post.query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def update_post(post_id: int, title: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        更新文章
        :param post_id: 文章ID
        :param title: 新標題
        :param content: 新內容
        :return: (success boolean, error message)
        """
        try:
            if not title.strip():
                return False, "標題不能為空"
            if not content.strip():
                return False, "內容不能為空"

            post = Post.query.get(post_id)
            if not post:
                return False, "文章不存在"

            post.title = title
            post.content = content
            post.updated_at = datetime.utcnow()

            return PostService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_post(post_id: int) -> Tuple[bool, Optional[str]]:
        """
        刪除文章
        :param post_id: 文章ID
        :return: (success boolean, error message)
        """
        try:
            post = Post.query.get(post_id)
            if not post:
                return False, "文章不存在"

            db.session.delete(post)
            return PostService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_user_posts(user_id: int, page: int = 1, per_page: int = 10) -> Any:
        """
        獲取指定用戶的文章列表
        :param user_id: 用戶ID
        :param page: 頁碼
        :param per_page: 每頁數量
        :return: Pagination object
        """
        return Post.query.filter_by(user_id=user_id) \
            .order_by(Post.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def search_posts(query: str, page: int = 1, per_page: int = 10) -> Any:
        """
        搜索文章
        :param query: 搜索關鍵字
        :param page: 頁碼
        :param per_page: 每頁數量
        :return: Pagination object
        """
        return Post.query.filter(
            or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%')
            )
        ).order_by(Post.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)
