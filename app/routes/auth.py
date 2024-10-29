from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.services import UserService
from urllib.parse import urlparse
from app.models.user import User
from app import db
from app.utils.validators import PasswordValidator


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
    """處理用戶註冊"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 驗證密碼強度
        is_valid, message = PasswordValidator.validate_password(password)
        if not is_valid:
            flash(message, 'danger')
            return redirect(url_for('auth.register'))

        # 驗證密碼確認
        if password != confirm_password:
            flash('密碼不一致', 'danger')
            return redirect(url_for('auth.register'))

        # 檢查電子郵件是否已存在
        if User.query.filter_by(email=email).first():
            flash('此電子郵件已被註冊', 'danger')
            return redirect(url_for('auth.register'))

        # 檢查用戶名是否已存在
        if User.query.filter_by(username=username).first():
            flash('此用戶名已被使用', 'danger')
            return redirect(url_for('auth.register'))

        # 創建新用戶
        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('註冊成功！請登入。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='註冊')

@auth_bp.route('/check-password-strength', methods=['POST'])
def check_password_strength():
    """檢查密碼強度的API"""
    password = request.json.get('password', '')
    is_valid, message = PasswordValidator.validate_password(password)

    return jsonify({
        'valid': is_valid,
        'message': message
    })

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

        if action == 'update_avatar':
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file.filename:
                    success, error = UserService.update_avatar(current_user.id, file)
                    if not success:
                        flash(f'頭像更新失敗: {error}', 'danger')
                    else:
                        flash('頭像已更新', 'success')
            return redirect(url_for('auth.profile'))

        elif action == 'update_profile':
            success, error = UserService.update_profile(
                user_id=current_user.id,
                username=request.form.get('username'),
                email=request.form.get('email')
            )
            flash('個人資料已更新' if success else f'更新失敗: {error}',
                  'success' if success else 'danger')

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
                flash('密碼已更新' if success else f'更新失敗: {error}',
                      'success' if success else 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', title='個人資料')
