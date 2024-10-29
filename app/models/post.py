from app import db
from datetime import datetime


class Post(db.Model):
    """文章模型"""
    __tablename__ = 'post'

    # 基本欄位
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, comment='標題')
    content = db.Column(db.Text, nullable=False, comment='內容')

    # 時間相關欄位
    created_at = db.Column(db.DateTime, default=datetime.now, comment='創建時間')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新時間')

    # 外鍵
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='作者ID')

    # 關聯關係
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def like_count(self):
        """獲取按讚數量"""
        return self.likes.count()

    @property
    def comments_count(self) -> int:
        """獲取留言數量"""
        return self.comments.count()

    def is_liked_by(self, user):
        """檢查用戶是否已按讚此文章"""
        if not user:
            return False
        return bool(self.likes.filter_by(user_id=user.id).first())

    def __repr__(self):
        return f'<Post {self.id}>'
