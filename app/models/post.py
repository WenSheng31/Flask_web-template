from app import db
from datetime import datetime


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 關聯
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def like_count(self):
        """獲取按讚數量"""
        return self.likes.count()

    def is_liked_by(self, user):
        """檢查用戶是否已按讚"""
        if not user:
            return False
        return bool(self.likes.filter_by(user_id=user.id).first())

    def __repr__(self):
        return f'<Post {self.id}>'
