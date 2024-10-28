from datetime import datetime, timedelta
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User


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
        active_threshold = datetime.utcnow() - timedelta(days=SystemConfig.ACTIVE_DAYS_THRESHOLD)

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


class ProfileManager:
    """個人資料管理類"""

    @staticmethod
    def update_profile(form_data: dict) -> tuple:
        """
        更新個人資料

        Args:
            form_data: 表單數據

        Returns:
            tuple: (是否成功, 提示訊息)
        """
        try:
            current_user.username = form_data.get('username', current_user.username)
            current_user.email = form_data.get('email', current_user.email)
            db.session.commit()
            return True, '個人資料已更新'
        except Exception as e:
            db.session.rollback()
            return False, f'更新失敗: {str(e)}'

    @staticmethod
    def update_password(form_data: dict) -> tuple:
        """
        更新密碼

        Args:
            form_data: 表單數據

        Returns:
            tuple: (是否成功, 提示訊息)
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


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    設定頁面視圖
    GET: 顯示設定頁面
    POST: 處理設定更新請求
    """
    if request.method == 'POST':
        action = request.form.get('action')

        # 根據操作類型處理不同的設定更新
        if action == 'update_profile':
            success, message = ProfileManager.update_profile(request.form)
        elif action == 'update_password':
            success, message = ProfileManager.update_password(request.form)
        else:
            success, message = False, '無效的操作'

        # 設置提示訊息
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('settings.index'))

    # 準備頁面數據
    template_data = {
        'title': '設定',
        'stats': get_system_statistics(),
    }

    return render_template('pages/settings.html', **template_data)


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


# 系統維護相關路由
@settings_bp.route('/maintenance', methods=['POST'])
@login_required
def maintenance():
    """系統維護操作（需要管理員權限）"""
    if not current_user.is_admin:
        flash('無權限執行此操作', 'danger')
        return redirect(url_for('settings.index'))

    action = request.form.get('action')

    try:
        if action == 'clear_inactive_users':
            # 清理不活躍用戶
            threshold = datetime.utcnow() - timedelta(days=180)  # 半年未登入
            inactive_users = User.query.filter(User.last_login < threshold).all()
            for user in inactive_users:
                db.session.delete(user)
            db.session.commit()
            flash(f'已清理 {len(inactive_users)} 個不活躍用戶', 'success')
        else:
            flash('無效的維護操作', 'danger')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Maintenance error: {str(e)}")
        flash(f'維護操作失敗: {str(e)}', 'danger')

    return redirect(url_for('settings.index'))
