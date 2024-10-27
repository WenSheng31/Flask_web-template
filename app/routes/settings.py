from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from datetime import datetime, timedelta


settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


def get_system_stats():
    """獲取系統統計數據"""
    try:
        # 獲取總用戶數
        total_users = User.query.count()

        # 獲取活躍用戶數（最近30天內有登入的用戶）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = User.query.filter(User.last_login >= thirty_days_ago).count()

        return {
            'total_users': total_users,
            'active_users': active_users,
            'system_version': '1.0.0',
            'last_update': '2024-10-27'
        }
    except Exception as e:
        # 如果發生錯誤，返回預設值
        return {
            'total_users': 0,
            'active_users': 0,
            'system_version': '1.0.0',
            'last_update': '2024-10-27'
        }

@settings_bp.route('/')
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            try:
                current_user.username = request.form.get('username', current_user.username)
                current_user.email = request.form.get('email', current_user.email)
                db.session.commit()
                flash('個人資料已更新', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'更新失敗: {str(e)}', 'danger')

        elif action == 'update_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not current_user.check_password(current_password):
                flash('目前密碼不正確', 'danger')
            elif new_password != confirm_password:
                flash('新密碼與確認密碼不符', 'danger')
            else:
                try:
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash('密碼已更新', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'更新失敗: {str(e)}', 'danger')

        return redirect(url_for('settings.index'))

    # 獲取系統統計數據
    stats = get_system_stats()

    return render_template('pages/settings.html',
                           title='設定',
                           stats=stats,
                           )
