from flask import render_template, Blueprint, request
from app.models.user import User
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import func

main_bp = Blueprint('main', __name__, url_prefix='/')


@main_bp.route('/')
def index():
    # 獲取總用戶數
    total_users = User.query.count()

    # 獲取本月新增用戶數
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_users_this_month = User.query.filter(User.created_at >= first_day_of_month).count()

    # 最後更新時間（這裡用最新註冊用戶的時間）
    latest_user = User.query.order_by(User.created_at.desc()).first()
    last_update = latest_user.created_at.strftime('%Y-%m-%d %H:%M') if latest_user else '無資料'

    return render_template('main/index.html',
                           title='首頁',
                           total_users=total_users,
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
