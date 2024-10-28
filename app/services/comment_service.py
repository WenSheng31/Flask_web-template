from typing import Tuple, Optional, List, Dict
from datetime import datetime
from flask import current_app
from app import db
from app.models import Comment
from .base_service import BaseService


class CommentService(BaseService):
    """留言服務類"""

    # 配置常量
    DEFAULT_PAGE_SIZE = 20
    MAX_REPLY_DEPTH = 3  # 最大回覆深度

    @staticmethod
    def create_comment(user_id: int, post_id: int, content: str,
                       parent_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        創建新留言

        Args:
            user_id: 用戶ID
            post_id: 文章ID
            content: 留言內容
            parent_id: 父留言ID（用於回覆）

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            # 驗證輸入
            if not content.strip():
                return False, "留言內容不能為空"

            # 檢查回覆深度
            if parent_id:
                depth = CommentService.get_comment_depth(parent_id)
                if depth >= CommentService.MAX_REPLY_DEPTH:
                    return False, f"最多只能回覆 {CommentService.MAX_REPLY_DEPTH} 層"

            # 創建留言
            comment = Comment(
                user_id=user_id,
                post_id=post_id,
                content=content,
                parent_id=parent_id
            )

            return CommentService.save_to_db(comment)

        except Exception as e:
            current_app.logger.error(f"Error creating comment: {str(e)}")
            return False, str(e)

    @staticmethod
    def get_comment_by_id(comment_id: int) -> Optional[Comment]:
        """
        通過ID獲取留言

        Args:
            comment_id: 留言ID

        Returns:
            Optional[Comment]: 留言實例或None
        """
        try:
            return Comment.query.get(comment_id)
        except Exception as e:
            current_app.logger.error(f"Error getting comment: {str(e)}")
            return None

    @staticmethod
    def delete_comment(comment_id: int) -> Tuple[bool, Optional[str]]:
        """
        刪除留言

        Args:
            comment_id: 留言ID

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            comment = Comment.query.get(comment_id)
            if not comment:
                return False, "留言不存在"

            return CommentService.delete_from_db(comment)

        except Exception as e:
            current_app.logger.error(f"Error deleting comment: {str(e)}")
            return False, str(e)

    @classmethod
    def get_post_comments(cls, post_id: int, page: int = 1,
                          per_page: int = None) -> Tuple[List[Comment], int]:
        """
        獲取文章的留言列表

        Args:
            post_id: 文章ID
            page: 頁碼
            per_page: 每頁數量

        Returns:
            Tuple[List[Comment], int]: (留言列表, 總頁數)
        """
        try:
            per_page = per_page or cls.DEFAULT_PAGE_SIZE
            pagination = Comment.query.filter_by(
                post_id=post_id,
                parent_id=None  # 只獲取頂層留言
            ).order_by(
                Comment.created_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            return pagination.items, pagination.pages

        except Exception as e:
            current_app.logger.error(f"Error getting post comments: {str(e)}")
            return [], 0

    @staticmethod
    def get_comment_depth(comment_id: int) -> int:
        """
        獲取留言的深度

        Args:
            comment_id: 留言ID

        Returns:
            int: 留言深度（0表示頂層留言）
        """
        try:
            depth = 0
            comment = Comment.query.get(comment_id)

            while comment and comment.parent_id:
                depth += 1
                comment = comment.parent

            return depth

        except Exception as e:
            current_app.logger.error(f"Error getting comment depth: {str(e)}")
            return 0

    @staticmethod
    def get_user_comments(user_id: int, page: int = 1,
                          per_page: int = 20) -> Tuple[List[Comment], int]:
        """
        獲取用戶的所有留言

        Args:
            user_id: 用戶ID
            page: 頁碼
            per_page: 每頁數量

        Returns:
            Tuple[List[Comment], int]: (留言列表, 總頁數)
        """
        try:
            pagination = Comment.query.filter_by(
                user_id=user_id
            ).order_by(
                Comment.created_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            return pagination.items, pagination.pages

        except Exception as e:
            current_app.logger.error(f"Error getting user comments: {str(e)}")
            return [], 0

    @staticmethod
    def update_comment(comment_id: int, content: str) -> Tuple[bool, Optional[str]]:
        """
        更新留言內容

        Args:
            comment_id: 留言ID
            content: 新的留言內容

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            if not content.strip():
                return False, "留言內容不能為空"

            comment = Comment.query.get(comment_id)
            if not comment:
                return False, "留言不存在"

            comment.content = content
            comment.updated_at = datetime.utcnow()

            return CommentService.commit()

        except Exception as e:
            current_app.logger.error(f"Error updating comment: {str(e)}")
            return False, str(e)

    @staticmethod
    def get_comment_statistics(post_id: int) -> Dict:
        """
        獲取文章留言統計資訊

        Args:
            post_id: 文章ID

        Returns:
            Dict: 統計資訊字典
        """
        try:
            total_comments = Comment.query.filter_by(post_id=post_id).count()
            total_replies = Comment.query.filter(
                Comment.post_id == post_id,
                Comment.parent_id.isnot(None)
            ).count()

            return {
                'total_comments': total_comments,
                'total_replies': total_replies,
                'root_comments': total_comments - total_replies
            }

        except Exception as e:
            current_app.logger.error(f"Error getting comment statistics: {str(e)}")
            return {
                'total_comments': 0,
                'total_replies': 0,
                'root_comments': 0
            }
