from app import db
from app.models import Comment
from .base_service import BaseService
from typing import Tuple, Optional, List


class CommentService(BaseService):
    @staticmethod
    def create_comment(user_id: int, post_id: int, content: str, parent_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        創建新留言
        """
        try:
            comment = Comment(
                user_id=user_id,
                post_id=post_id,
                content=content,
                parent_id=parent_id
            )
            db.session.add(comment)
            return CommentService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_comment_by_id(comment_id: int) -> Optional[Comment]:
        """
        通過ID獲取留言
        """
        return Comment.query.get(comment_id)

    @staticmethod
    def delete_comment(comment_id: int) -> Tuple[bool, Optional[str]]:
        """
        刪除留言
        """
        try:
            comment = Comment.query.get(comment_id)
            if not comment:
                return False, "留言不存在"

            db.session.delete(comment)
            return CommentService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_post_comments(post_id: int, page: int = 1, per_page: int = 20) -> Tuple[List[Comment], int]:
        """
        獲取文章的留言列表
        """
        pagination = Comment.query.filter_by(post_id=post_id)\
            .order_by(Comment.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.pages
