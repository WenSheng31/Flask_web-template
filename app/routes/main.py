from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from flask_login import current_user
from sqlalchemy.orm import joinedload
from app import db
from app.models import User, Post
from app.services import UserService

main_bp = Blueprint('main', __name__, url_prefix='/')


def get_active_users(limit: int = 12) -> list:
    """
    獲取活躍用戶列表

    Args:
        limit: 返回用戶數量限制，預設12人

    Returns:
        活躍用戶列表
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    return User.query.filter(
        User.last_login >= thirty_days_ago
    ).order_by(
        User.last_login.desc()
    ).limit(limit).all()


def get_site_statistics() -> dict:
    """
    獲取網站統計資訊

    Returns:
        包含網站統計資訊的字典
    """
    # 獲取最後更新時間
    latest_user = User.query.order_by(User.created_at.desc()).first()
    latest_post = Post.query.order_by(Post.created_at.desc()).first()

    # 計算最後更新時間
    last_update = None
    if latest_user and latest_post:
        last_update = max(latest_user.created_at, latest_post.created_at)
    elif latest_user:
        last_update = latest_user.created_at
    elif latest_post:
        last_update = latest_post.created_at

    return last_update.strftime('%Y-%m-%d %H:%M') if last_update else '無資料'


@main_bp.route('/')
def index():
    """首頁視圖"""
    # 獲取用戶統計
    user_stats = UserService.get_user_statistics()

    # 獲取最新文章
    latest_posts = Post.query.options(
        joinedload(Post.author)
    ).order_by(Post.created_at.desc()).limit(10).all()

    # 準備模板數據
    template_data = {
        'title': '首頁',
        'latest_posts': latest_posts,
        'total_users': user_stats['total'],
        'total_posts': Post.query.count(),
        'new_users_this_month': user_stats['new_this_month'],
        'last_update': get_site_statistics(),
        'active_users': get_active_users()
    }

    # 如果用戶已登入，添加用戶統計資訊
    if current_user.is_authenticated:
        user_activity_stats = UserService.get_user_stats(current_user.id)
        template_data['user_stats'] = {
            'posts_count': user_activity_stats['posts_count'],
            'received_likes': user_activity_stats['received_likes']
        }

    return render_template('main/index.html', **template_data)


@main_bp.route('/members')
def members():
    """會員列表視圖"""
    page = request.args.get('page', 1, type=int)
    per_page = 16  # 每頁顯示的會員數量

    pagination = User.query.order_by(
        User.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('main/members.html',
                           title='會員列表',
                           users=pagination.items,
                           pagination=pagination)


@main_bp.route('/about')
def about():
    """關於頁面視圖"""
    return render_template('main/about.html',
                           title='關於我們')
