# 標準庫導入
from datetime import datetime, timedelta

# 第三方套件導入
from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_required, current_user

# 本地應用導入
from app import db
from app.models.user import User

# 常數配置
SYSTEM_VERSION = '1.0.0'
LAST_UPDATE = '2024-10-27'
ACTIVE_DAYS_THRESHOLD = 30

# 創建設定藍圖
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


# 工具函數
def get_user_counts():
    """
    獲取用戶統計數據
    :return: tuple(int, int) 總用戶數和活躍用戶數
    """
    try:
        # 計算總用戶數
        total_users = User.query.count()

        # 計算活躍用戶數（最近30天內有登入的用戶）
        thirty_days_ago = datetime.utcnow() - timedelta(days=ACTIVE_DAYS_THRESHOLD)
        active_users = User.query.filter(User.last_login >= thirty_days_ago).count()

        return total_users, active_users
    except Exception as e:
        return 0, 0


def get_system_stats():
    """
    獲取系統統計數據
    :return: dict 系統統計資訊
    """
    total_users, active_users = get_user_counts()

    return {
        'total_users': total_users,
        'active_users': active_users,
        'system_version': SYSTEM_VERSION,
        'last_update': LAST_UPDATE
    }


def handle_profile_update(form_data):
    """
    處理個人資料更新
    :param form_data: 表單數據
    :return: tuple(bool, str) 操作是否成功及訊息
    """
    try:
        current_user.username = form_data.get('username', current_user.username)
        current_user.email = form_data.get('email', current_user.email)
        db.session.commit()
        return True, '個人資料已更新'
    except Exception as e:
        db.session.rollback()
        return False, f'更新失敗: {str(e)}'


def handle_password_update(form_data):
    """
    處理密碼更新
    :param form_data: 表單數據
    :return: tuple(bool, str) 操作是否成功及訊息
    """
    current_password = form_data.get('current_password')
    new_password = form_data.get('new_password')
    confirm_password = form_data.get('confirm_password')

    # 驗證密碼
    if not current_user.check_password(current_password):
        return False, '目前密碼不正確'

    if new_password != confirm_password:
        return False, '新密碼與確認密碼不符'

    try:
        current_user.set_password(new_password)
        db.session.commit()
        return True, '密碼已更新'
    except Exception as e:
        db.session.rollback()
        return False, f'更新失敗: {str(e)}'


def handle_settings_action(action, form_data):
    """
    處理設定頁面的不同操作
    :param action: 操作類型
    :param form_data: 表單數據
    :return: bool 操作是否成功
    """
    handlers = {
        'update_profile': handle_profile_update,
        'update_password': handle_password_update
    }

    handler = handlers.get(action)
    if not handler:
        flash('無效的操作', 'danger')
        return False

    success, message = handler(form_data)
    flash(message, 'success' if success else 'danger')
    return success


# 視圖函數
@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """設定頁面視圖函數"""
    if request.method == 'POST':
        action = request.form.get('action')
        handle_settings_action(action, request.form)
        return redirect(url_for('settings.index'))

    # 準備頁面數據
    template_data = {
        'title': '設定',
        'stats': get_system_stats(),
    }

    return render_template('pages/settings.html', **template_data)


# 錯誤處理
@settings_bp.errorhandler(Exception)
def handle_error(error):
    """
    統一錯誤處理
    :param error: 錯誤實例
    :return: redirect
    """
    db.session.rollback()
    flash(f'發生錯誤: {str(error)}', 'danger')
    return redirect(url_for('settings.index'))
