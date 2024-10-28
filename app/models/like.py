from app import db
from datetime import datetime


class Like(db.Model):
    """按讚模型"""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 外鍵關聯
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    # 設置複合唯一約束，確保每個用戶只能對同一篇文章按讚一次
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)

    # 關聯關係
    user = db.relationship('User', backref=db.backref('likes', lazy=True))
    post = db.relationship('Post', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Like {self.id}>'
