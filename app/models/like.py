from app import db
from datetime import datetime


class Like(db.Model):
    """按讚模型"""
    __tablename__ = 'likes'

    # 基本欄位
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='按讚時間')

    # 外鍵關聯
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用戶ID')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, comment='文章ID')

    # 確保每個用戶只能對同一篇文章按讚一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
    )

    def __repr__(self):
        return f'<Like {self.id}: User {self.user_id} -> Post {self.post_id}>'

    def to_dict(self):
        """轉換為字典格式（用於API回應）"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'post_id': self.post_id
        }

    @classmethod
    def get_user_likes(cls, user_id):
        """獲取用戶的所有按讚記錄"""
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_post_likes(cls, post_id):
        """獲取文章的所有按讚記錄"""
        return cls.query.filter_by(post_id=post_id).all()
