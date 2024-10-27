# 標準庫導入
from datetime import datetime

# 第三方套件導入
from flask import render_template, Blueprint, request

# 本地應用導入
from app.models.user import User
from app.models.post import Post

# 常數配置
POSTS_PER_PAGE = 5
MEMBERS_PER_PAGE = 16
DATE_FORMAT = '%Y-%m-%d %H:%M'

# 創建主要藍圖
main_bp = Blueprint('main', __name__, url_prefix='/')


def get_latest_posts(limit=POSTS_PER_PAGE):
    """
    獲取最新的文章
    :param limit: 限制返回的文章數量
    :return: 文章列表
    """
    return Post.query.order_by(Post.created_at.desc()).limit(limit).all()


def get_user_statistics():
    """
    獲取用戶統計資料
    :return: dict 包含總用戶數和本月新增用戶數
    """
    total_users = User.query.count()

    # 計算本月新增用戶
    first_day_of_month = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    new_users_this_month = User.query.filter(
        User.created_at >= first_day_of_month
    ).count()

    return {
        'total': total_users,
        'new_this_month': new_users_this_month
    }


def get_last_update_time():
    """
    獲取最後更新時間
    :return: str 格式化的最後更新時間
    """
    latest_user = User.query.order_by(User.created_at.desc()).first()
    latest_post = Post.query.order_by(Post.created_at.desc()).first()

    last_update = None
    if latest_user and latest_post:
        last_update = max(latest_user.created_at, latest_post.created_at)
    elif latest_user:
        last_update = latest_user.created_at
    elif latest_post:
        last_update = latest_post.created_at

    return last_update.strftime(DATE_FORMAT) if last_update else '無資料'


# 路由定義
@main_bp.route('/')
def index():
    """首頁視圖函數"""
    # 獲取統計資料
    user_stats = get_user_statistics()

    # 準備模板數據
    template_data = {
        'title': '首頁',
        'latest_posts': get_latest_posts(),
        'total_users': user_stats['total'],
        'total_posts': Post.query.count(),
        'new_users_this_month': user_stats['new_this_month'],
        'last_update': get_last_update_time()
    }

    return render_template('main/index.html', **template_data)


@main_bp.route('/about')
def about():
    """關於頁面視圖函數"""
    return render_template('main/about.html', title='關於我們')


@main_bp.route('/members')
def members():
    """會員列表視圖函數"""
    # 獲取當前頁碼
    page = request.args.get('page', 1, type=int)

    # 查詢會員資料
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=MEMBERS_PER_PAGE,
        error_out=False
    )

    # 準備模板數據
    template_data = {
        'title': '會員列表',
        'users': pagination.items,
        'pagination': pagination
    }

    return render_template('main/members.html', **template_data)
