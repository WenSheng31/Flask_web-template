from flask import render_template, Blueprint, request
from app.models.user import User
from app.models.post import Post
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import func

main_bp = Blueprint('main', __name__, url_prefix='/')


@main_bp.route('/')
def index():
    # 獲取最新的5篇文章
    latest_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    # 獲取總用戶數
    total_users = User.query.count()

    # 獲取本月新增用戶數
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_users_this_month = User.query.filter(User.created_at >= first_day_of_month).count()

    # 獲取總文章數
    total_posts = Post.query.count()

    # 最後更新時間（這裡用最新註冊用戶或最新文章的時間，取較新的）
    latest_user = User.query.order_by(User.created_at.desc()).first()
    latest_post = Post.query.order_by(Post.created_at.desc()).first()

    last_update = None
    if latest_user and latest_post:
        last_update = max(latest_user.created_at, latest_post.created_at)
    elif latest_user:
        last_update = latest_user.created_at
    elif latest_post:
        last_update = latest_post.created_at

    last_update = last_update.strftime('%Y-%m-%d %H:%M') if last_update else '無資料'

    return render_template('main/index.html',
                           title='首頁',
                           latest_posts=latest_posts,
                           total_users=total_users,
                           total_posts=total_posts,
                           new_users_this_month=new_users_this_month,
                           last_update=last_update)

@main_bp.route('/about')
def about():
    return render_template('main/about.html', title='關於我們')

@main_bp.route('/members')
def members():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=16, error_out=False)
    users = pagination.items
    return render_template('main/members.html',
                         title='會員列表',
                         users=users,
                         pagination=pagination)
