from app import db
from datetime import datetime


class Comment(db.Model):
    """留言模型"""
    __tablename__ = 'comment'

    # 基本欄位
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False, comment='留言內容')

    # 時間相關欄位
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='創建時間')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新時間')

    # 外鍵關聯
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='留言者ID')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, comment='文章ID')
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), comment='父留言ID，用於回覆功能')

    # 關聯關係
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def reply_count(self):
        """獲取回覆數量"""
        return self.replies.count()

    def __repr__(self):
        return f'<Comment {self.id}>'

    def to_dict(self):
        """轉換為字典格式（用於API回應）"""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'post_id': self.post_id,
            'parent_id': self.parent_id,
            'reply_count': self.reply_count
        }
