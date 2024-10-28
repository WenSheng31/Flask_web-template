from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(id):
    """載入用戶，用於 Flask-Login"""
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """用戶模型"""
    __tablename__ = 'user'

    # 基本欄位
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False, comment='用戶名')
    email = db.Column(db.String(120), unique=True, index=True, nullable=False, comment='電子郵件')
    password_hash = db.Column(db.String(128), comment='密碼雜湊')
    avatar_path = db.Column(db.String(200), nullable=True, comment='頭像路徑')

    # 時間相關欄位
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='創建時間')
    last_login = db.Column(db.DateTime, default=datetime.utcnow, comment='最後登入時間')

    # 狀態欄位
    is_active = db.Column(db.Boolean, default=True, comment='是否啟用')
    is_admin = db.Column(db.Boolean, default=False, comment='是否為管理員')

    # 關聯關係
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        """
        設置密碼

        Args:
            password: 原始密碼
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        驗證密碼

        Args:
            password: 待驗證的密碼

        Returns:
            bool: 密碼是否正確
        """
        return check_password_hash(self.password_hash, password)

    def like_post(self, post) -> None:
        """
        對文章按讚

        Args:
            post: 文章實例
        """
        if not self.has_liked_post(post):
            from app.models.like import Like
            like = Like(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post) -> None:
        """
        取消文章按讚

        Args:
            post: 文章實例
        """
        from app.models.like import Like
        like = Like.query.filter_by(user_id=self.id, post_id=post.id).first()
        if like:
            db.session.delete(like)

    def has_liked_post(self, post) -> bool:
        """
        檢查是否已對文章按讚

        Args:
            post: 文章實例

        Returns:
            bool: 是否已按讚
        """
        from app.models.like import Like
        return Like.query.filter_by(user_id=self.id, post_id=post.id).first() is not None

    @property
    def posts_count(self) -> int:
        """獲取發文總數"""
        return self.posts.count()

    @property
    def received_likes_count(self) -> int:
        """獲取收到的總讚數"""
        from app.models.like import Like
        from app.models.post import Post
        return Like.query.join(Post).filter(Post.user_id == self.id).count()

    def __repr__(self) -> str:
        """模型的字符串表示"""
        return f'<User {self.username}>'
