from app import db
from datetime import datetime
from .like import Like
from .comment import Comment


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 定義與 User 模型的關係
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    @property
    def like_count(self):
        """獲取按讚數量"""
        return Like.query.filter_by(post_id=self.id).count()

    @property
    def comment_count(self):
        """獲取留言數量"""
        return Comment.query.filter_by(post_id=self.id).count()

    def is_liked_by(self, user):
        """檢查用戶是否已按讚"""
        if not user:
            return False
        return Like.query.filter_by(
            user_id=user.id,
            post_id=self.id
        ).first() is not None

    def __repr__(self):
        return f'<Post {self.id}>'
