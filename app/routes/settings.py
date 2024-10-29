from datetime import datetime, timedelta
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.services import UserService


# 系統配置常量
class SystemConfig:
    """系統配置常量"""
    VERSION = '1.0.0'
    LAST_UPDATE = '2024-10-27'
    ACTIVE_DAYS_THRESHOLD = 30
    DEFAULT_PAGE_SIZE = 20

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

def get_system_statistics() -> dict:
    """
    獲取系統統計數據

    Returns:
        dict: 包含系統統計資訊的字典
    """
    try:
        # 計算時間閾值
        active_threshold = datetime.now() - timedelta(days=SystemConfig.ACTIVE_DAYS_THRESHOLD)

        # 獲取用戶統計
        total_users = User.query.count()
        active_users = User.query.filter(User.last_login >= active_threshold).count()

        return {
            'total_users': total_users,
            'active_users': active_users,
            'system_version': SystemConfig.VERSION,
            'last_update': SystemConfig.LAST_UPDATE,
        }
    except Exception as e:
        current_app.logger.error(f"Error getting system statistics: {str(e)}")
        return {
            'total_users': 0,
            'active_users': 0,
            'system_version': SystemConfig.VERSION,
            'last_update': SystemConfig.LAST_UPDATE,
        }

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            success, error = UserService.update_profile(
                user_id=current_user.id,
                username=request.form.get('username'),
                email=request.form.get('email')
            )
        elif action == 'update_password':
            success, error = UserService.update_password(
                user_id=current_user.id,
                current_password=request.form.get('current_password'),
                new_password=request.form.get('new_password')
            )
        else:
            success, error = False, '無效的操作'

        flash('操作' + ('成功' if success else f'失敗: {error}'),
              'success' if success else 'danger')
        return redirect(url_for('settings.index'))

    return render_template('pages/settings.html',
                           title='設定',
                           stats=get_system_statistics())

@settings_bp.errorhandler(Exception)
def handle_error(error):
    """
    統一錯誤處理

    Args:
        error: 錯誤實例

    Returns:
        重定向到設定頁面
    """
    db.session.rollback()
    current_app.logger.error(f"Settings error: {str(error)}")
    flash(f'發生錯誤: {str(error)}', 'danger')
    return redirect(url_for('settings.index'))
