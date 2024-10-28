from app import db
from app.models import User
from .base_service import BaseService
from typing import Tuple, Optional, List
from datetime import datetime


class UserService(BaseService):
    @staticmethod
    def create_user(username: str, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        創建新用戶
        """
        try:
            # 檢查用戶名是否已存在
            if User.query.filter_by(username=username).first():
                return None, "用戶名已被使用"

            # 檢查郵箱是否已存在
            if User.query.filter_by(email=email).first():
                return None, "郵箱已被註冊"

            # 創建新用戶
            user = User(
                username=username,
                email=email
            )
            user.set_password(password)

            db.session.add(user)
            success, error = UserService.commit()

            if success:
                return user, None
            return None, error
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        通過ID獲取用戶
        """
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        通過郵箱獲取用戶
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def update_profile(user_id: int, username: str = None, email: str = None) -> Tuple[bool, Optional[str]]:
        """
        更新用戶資料
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用戶不存在"

            if username:
                # 檢查新用戶名是否已被使用
                existing_user = User.query.filter_by(username=username).first()
                if existing_user and existing_user.id != user_id:
                    return False, "用戶名已被使用"
                user.username = username

            if email:
                # 檢查新郵箱是否已被註冊
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user_id:
                    return False, "郵箱已被註冊"
                user.email = email

            return UserService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        更新密碼
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用戶不存在"

            if not user.check_password(current_password):
                return False, "當前密碼不正確"

            user.set_password(new_password)
            return UserService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_avatar(user_id: int, avatar_path: str) -> Tuple[bool, Optional[str]]:
        """
        更新頭像
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用戶不存在"

            user.avatar_path = avatar_path
            return UserService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_last_login(user_id: int) -> None:
        """
        更新最後登入時間
        """
        try:
            user = User.query.get(user_id)
            if user:
                user.last_login = datetime.utcnow()
                UserService.commit()
        except Exception:
            pass  # 忽略更新最後登入時間的錯誤

    @staticmethod
    def get_users_page(page: int = 1, per_page: int = 16) -> Tuple[List[User], int]:
        """
        獲取分頁的用戶列表
        """
        pagination = User.query.order_by(User.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.pages

    @staticmethod
    def get_active_users_count() -> int:
        """
        獲取活躍用戶數量（30天內有登入）
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        return User.query.filter(User.last_login >= thirty_days_ago).count()
