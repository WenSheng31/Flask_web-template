import os
from typing import Tuple, Optional
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app
from app.models import User
from .base_service import BaseService


class UserService(BaseService):
    """用戶服務類"""

    # 配置常量
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    AVATAR_SIZE = (300, 300)  # 頭像尺寸
    AVATAR_QUALITY = 85  # 圖片品質

    @staticmethod
    def create_user(username: str, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        創建新用戶

        Args:
            username: 用戶名
            email: 電子郵件
            password: 密碼

        Returns:
            Tuple[Optional[User], Optional[str]]: (用戶實例, 錯誤訊息)
        """
        try:
            # 檢查用戶名和郵箱是否已存在
            if User.query.filter_by(username=username).first():
                return None, "用戶名已被使用"
            if User.query.filter_by(email=email).first():
                return None, "郵箱已被註冊"

            # 創建新用戶
            user = User(username=username, email=email)
            user.set_password(password)

            success, error = UserService.save_to_db(user)
            return (user, None) if success else (None, error)

        except Exception as e:
            current_app.logger.error(f"Error creating user: {str(e)}")
            return None, str(e)

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根據ID獲取用戶"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """根據郵箱獲取用戶"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def update_profile(user_id: int, username: Optional[str] = None,
                       email: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        更新用戶資料

        Args:
            user_id: 用戶ID
            username: 新用戶名
            email: 新郵箱

        Returns:
            Tuple[bool, str]: (是否成功, 錯誤訊息)
        """
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return False, "用戶不存在"

            if username:
                existing_user = User.query.filter_by(username=username).first()
                if existing_user and existing_user.id != user_id:
                    return False, "用戶名已被使用"
                user.username = username

            if email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user_id:
                    return False, "郵箱已被註冊"
                user.email = email

            return UserService.commit()

        except Exception as e:
            current_app.logger.error(f"Error updating profile: {str(e)}")
            return False, str(e)

    @staticmethod
    def update_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        更新用戶密碼

        Args:
            user_id: 用戶ID
            current_password: 當前密碼
            new_password: 新密碼

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            # 獲取用戶
            user = UserService.get_user_by_id(user_id)
            if not user:
                return False, "用戶不存在"

            # 驗證當前密碼
            if not user.check_password(current_password):
                return False, "當前密碼不正確"

            # 驗證新密碼
            if len(new_password) < 6:
                return False, "新密碼長度不能小於6位"

            # 更新密碼
            user.set_password(new_password)
            return UserService.commit()

        except Exception as e:
            current_app.logger.error(f"Error updating password: {str(e)}")
            return False, str(e)

    @staticmethod
    def update_last_login(user_id: int) -> Tuple[bool, Optional[str]]:
        """
        更新用戶最後登入時間

        Args:
            user_id: 用戶ID

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return False, "用戶不存在"

            user.last_login = datetime.now()
            return UserService.commit()

        except Exception as e:
            current_app.logger.error(f"Error updating last login: {str(e)}")
            return False, str(e)

    @classmethod
    def process_avatar(cls, file, user_id: int) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        處理頭像上傳

        Args:
            file: 上傳的文件
            user_id: 用戶ID

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (是否成功, 文件路徑, 錯誤訊息)
        """
        try:
            if not file:
                return False, None, "未選擇文件"

            if not cls.allowed_file(file.filename):
                return False, None, "不支持的文件格式"

            # 生成安全的文件名
            timestamp = int(datetime.now().timestamp())
            filename = secure_filename(f"avatar_{user_id}_{timestamp}.jpg")

            # 確保上傳目錄存在
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)

            filepath = os.path.join(upload_dir, filename)

            # 處理圖片
            image = Image.open(file)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            # 裁剪為正方形
            width, height = image.size
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            image = image.crop((left, top, left + size, top + size))

            # 調整大小
            image = image.resize(cls.AVATAR_SIZE, Image.Resampling.LANCZOS)

            # 保存圖片
            image.save(filepath, 'JPEG', quality=cls.AVATAR_QUALITY)

            return True, f"uploads/avatars/{filename}", None

        except Exception as e:
            current_app.logger.error(f"Error processing avatar: {str(e)}")
            return False, None, str(e)

    @staticmethod
    def update_avatar(user_id: int, file) -> Tuple[bool, Optional[str]]:
        """
        更新用戶頭像
        Args:
            user_id: 用戶ID
            file: 上傳的文件
        Returns:
            Tuple[bool, str]: (是否成功, 錯誤信息)
        """
        try:
            if not file or not file.filename:
                return False, "未選擇文件"

            # 檢查文件類型
            if not UserService.allowed_file(file.filename):
                return False, "不支持的文件格式"

            user = User.query.get(user_id)
            if not user:
                return False, "用戶不存在"

            # 生成文件名
            timestamp = int(datetime.now().timestamp())
            filename = secure_filename(f"avatar_{user_id}_{timestamp}.jpg")

            # 確保上傳目錄存在
            upload_folder = os.path.join(current_app.static_folder, 'uploads', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)

            # 完整文件路徑
            filepath = os.path.join(upload_folder, filename)

            # 處理並保存圖片
            try:
                # 打開圖片
                image = Image.open(file)

                # 轉換格式
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')

                # 裁剪為正方形
                min_side = min(image.size)
                left = (image.width - min_side) // 2
                top = (image.height - min_side) // 2
                image = image.crop((left, top, left + min_side, top + min_side))

                # 調整大小
                image = image.resize((300, 300), Image.Resampling.LANCZOS)

                # 保存圖片
                image.save(filepath, 'JPEG', quality=85)
            except Exception as e:
                return False, f"圖片處理失敗: {str(e)}"

            # 刪除舊頭像
            if user.avatar_path:
                old_avatar = os.path.join(current_app.static_folder, user.avatar_path)
                if os.path.exists(old_avatar):
                    try:
                        os.remove(old_avatar)
                    except Exception:
                        current_app.logger.warning(f"Failed to delete old avatar: {old_avatar}")

            # 更新資料庫
            user.avatar_path = f"uploads/avatars/{filename}"
            success, error = UserService.commit()

            if not success:
                # 如果資料庫更新失敗，刪除新上傳的文件
                if os.path.exists(filepath):
                    os.remove(filepath)
                return False, error

            return True, None

        except Exception as e:
            current_app.logger.error(f"Error updating avatar: {str(e)}")
            return False, str(e)

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """檢查文件是否為允許的格式"""
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
