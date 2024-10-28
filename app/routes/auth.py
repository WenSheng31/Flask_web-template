from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.services import UserService
from urllib.parse import urlparse


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """處理用戶登入"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = UserService.get_user_by_email(email)
        if user is None or not user.check_password(password):
            flash('電子郵件或密碼錯誤', 'danger')
            return redirect(url_for('auth.login'))

        # 更新最後登入時間
        UserService.update_last_login(user.id)
        login_user(user, remember=remember)

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')

        flash('登入成功！', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', title='登入')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """處理用戶註冊"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('密碼不一致', 'danger')
            return redirect(url_for('auth.register'))

        user, error = UserService.create_user(username, email, password)
        if error:
            flash(error, 'danger')
            return redirect(url_for('auth.register'))

        flash('註冊成功！請登入。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='註冊')


@auth_bp.route('/logout')
@login_required
def logout():
    """處理用戶登出"""
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """處理用戶個人資料更新"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            success, error = UserService.update_profile(
                user_id=current_user.id,
                username=request.form.get('username'),
                email=request.form.get('email')
            )
            if success:
                flash('個人資料已更新', 'success')
            else:
                flash(f'更新失敗: {error}', 'danger')

        elif action == 'update_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password != confirm_password:
                flash('新密碼與確認密碼不符', 'danger')
            else:
                success, error = UserService.update_password(
                    user_id=current_user.id,
                    current_password=current_password,
                    new_password=new_password
                )
                if success:
                    flash('密碼已更新', 'success')
                else:
                    flash(f'更新失敗: {error}', 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', title='個人資料')
