from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.services import UserService
from urllib.parse import urlparse

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用戶登入處理
    GET: 顯示登入頁面
    POST: 處理登入請求
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 獲取表單數據
        credentials = {
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'remember': bool(request.form.get('remember'))
        }

        # 驗證用戶
        user = UserService.get_user_by_email(credentials['email'])
        if not user or not user.check_password(credentials['password']):
            flash('電子郵件或密碼錯誤', 'danger')
            return redirect(url_for('auth.login'))

        # 更新登入時間
        success, error = UserService.update_last_login(user.id)
        if not success:
            current_app.logger.error(f"Failed to update last login time: {error}")

        # 登入用戶
        login_user(user, remember=credentials['remember'])
        flash('登入成功！', 'success')

        # 處理重定向
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    return render_template('auth/login.html', title='登入')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用戶註冊處理
    GET: 顯示註冊頁面
    POST: 處理註冊請求
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 獲取註冊資料
        user_data = {
            'email': request.form.get('email'),
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'confirm_password': request.form.get('confirm_password')
        }

        # 驗證密碼
        if user_data['password'] != user_data['confirm_password']:
            flash('密碼不一致', 'danger')
            return redirect(url_for('auth.register'))

        # 創建用戶
        user, error = UserService.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )

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
    """
    用戶個人資料管理
    GET: 顯示個人資料頁面
    POST: 處理個人資料更新
    """
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            # 處理頭像更新
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file.filename:
                    success, error = UserService.update_avatar(
                        user_id=current_user.id,
                        file=file
                    )  # 移除 app 參數
                    if not success:
                        flash(f'頭像更新失敗: {error}', 'danger')
                        return redirect(url_for('auth.profile'))

            # 處理基本資料更新
            profile_data = {
                'username': request.form.get('username'),
                'email': request.form.get('email')
            }

            success, error = UserService.update_profile(
                user_id=current_user.id,
                **profile_data
            )

            flash('個人資料已更新' if success else f'更新失敗: {error}',
                  'success' if success else 'danger')


        elif action == 'update_password':
            # 處理密碼更新
            password_data = {
                'current_password': request.form.get('current_password'),
                'new_password': request.form.get('new_password')
            }
            # 驗證輸入
            if not all(password_data.values()):
                flash('請填寫所有密碼欄位', 'danger')
                return redirect(url_for('auth.profile'))
            success, error = UserService.update_password(
                user_id=current_user.id,
                current_password=password_data['current_password'],
                new_password=password_data['new_password']
            )
            flash('密碼已更新' if success else f'更新失敗: {error}',
                  'success' if success else 'danger')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', title='個人資料')
