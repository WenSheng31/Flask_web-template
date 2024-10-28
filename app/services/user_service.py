import os
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime, timedelta
from app import db
from app.models import User
from .base_service import BaseService
from typing import Tuple, Optional, Any


class UserService(BaseService):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    AVATAR_SIZE = (300, 300)

    @staticmethod
    def create_user(username: str, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        創建新用戶
        :param username: 用戶名
        :param email: 電子郵件
        :param password: 密碼
        :return: (User object, error message)
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
        :param user_id: 用戶ID
        :return: User object or None
        """
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        通過郵箱獲取用戶
        :param email: 郵箱
        :return: User object or None
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def update_profile(user_id: int, username: str = None, email: str = None) -> Tuple[bool, Optional[str]]:
        """
        更新用戶資料
        :param user_id: 用戶ID
        :param username: 新用戶名
        :param email: 新郵箱
        :return: (success, error message)
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
    def allowed_file(filename: str) -> bool:
        """
        檢查文件是否允許上傳
        :param filename: 文件名
        :return: bool
        """
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in UserService.ALLOWED_EXTENSIONS

    @staticmethod
    def process_avatar(file, user_id: int, app) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        處理頭像上傳
        :param file: 上傳的文件
        :param user_id: 用戶ID
        :param app: Flask app對象
        :return: (success, file_path, error_message)
        """
        try:
            if not file:
                return False, None, "未選擇文件"

            if not UserService.allowed_file(file.filename):
                return False, None, "不支持的文件格式"

            # 生成安全的文件名
            timestamp = int(datetime.utcnow().timestamp())
            filename = secure_filename(f"avatar_{user_id}_{timestamp}.jpg")

            # 確保上傳目錄存在
            upload_dir = os.path.join(app.static_folder, 'uploads', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)

            filepath = os.path.join(upload_dir, filename)

            # 處理圖片
            image = Image.open(file)

            # 將圖片轉換為RGB模式（處理PNG等格式）
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            # 裁剪為正方形
            width, height = image.size
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            right = left + size
            bottom = top + size
            image = image.crop((left, top, right, bottom))

            # 調整大小
            image = image.resize(UserService.AVATAR_SIZE, Image.Resampling.LANCZOS)

            # 保存圖片
            image.save(filepath, 'JPEG', quality=85)

            # 返回相對路徑
            return True, f"uploads/avatars/{filename}", None

        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def update_avatar(user_id: int, file, app) -> Tuple[bool, Optional[str]]:
        """
        更新用戶頭像
        :param user_id: 用戶ID
        :param file: 上傳的文件
        :param app: Flask app對象
        :return: (success, error_message)
        """
        try:
            # 處理新頭像
            success, file_path, error = UserService.process_avatar(file, user_id, app)
            if not success:
                return False, error

            # 更新數據庫
            user = User.query.get(user_id)
            if not user:
                return False, "用戶不存在"

            # 刪除舊頭像
            if user.avatar_path:
                old_avatar = os.path.join(app.static_folder, user.avatar_path)
                if os.path.exists(old_avatar):
                    os.remove(old_avatar)

            # 更新頭像路徑
            user.avatar_path = file_path
            db.session.commit()

            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        更新密碼
        :param user_id: 用戶ID
        :param current_password: 當前密碼
        :param new_password: 新密碼
        :return: (success, error_message)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用戶不存在"

            if not user.check_password(current_password):
                return False, "當前密碼不正確"

            if len(new_password) < 6:
                return False, "新密碼長度不能小於6位"

            user.set_password(new_password)
            return UserService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_last_login(user_id: int) -> None:
        """
        更新最後登入時間
        :param user_id: 用戶ID
        """
        try:
            user = User.query.get(user_id)
            if user:
                user.last_login = datetime.utcnow()
                db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def get_users_page(page: int = 1, per_page: int = 16) -> Any:
        """
        獲取分頁的用戶列表
        :param page: 頁碼
        :param per_page: 每頁數量
        :return: Pagination object
        """
        return User.query.order_by(User.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_active_users_count(days: int = 30) -> int:
        """
        獲取活躍用戶數量
        :param days: 天數
        :return: 活躍用戶數量
        """
        since = datetime.utcnow() - timedelta(days=days)
        return User.query.filter(User.last_login >= since).count()

    @staticmethod
    def get_new_users_count(days: int = 30) -> int:
        """
        獲取新增用戶數量
        :param days: 天數
        :return: 新增用戶數量
        """
        since = datetime.utcnow() - timedelta(days=days)
        return User.query.filter(User.created_at >= since).count()