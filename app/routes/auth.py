# 標準庫導入
import os
import time
from datetime import datetime
from urllib.parse import urlparse

# 第三方套件導入
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image

# 本地應用導入
from app.models.user import User
from app import db

# 創建認證藍圖
auth_bp = Blueprint('auth', __name__)

# 常數配置
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
AVATAR_SIZE = (300, 300)


# 工具函數
def allowed_file(filename):
    """
    檢查上傳的檔案是否為允許的類型
    :param filename: 檔案名稱
    :return: bool 是否允許
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_avatar_image(file, user_id):
    """
    處理用戶上傳的頭像
    :param file: 上傳的檔案
    :param user_id: 用戶ID
    :return: 儲存的檔案路徑
    """
    # 生成安全的檔案名
    filename = secure_filename(f"avatar_{user_id}_{int(time.time())}.jpg")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # 處理圖片
    image = Image.open(file)

    # 將圖片裁剪為正方形
    min_side = min(image.size)
    left = (image.width - min_side) // 2
    top = (image.height - min_side) // 2
    right = left + min_side
    bottom = top + min_side
    image = image.crop((left, top, right, bottom))

    # 調整大小
    image = image.resize(AVATAR_SIZE, Image.Resampling.LANCZOS)

    # 保存圖片
    image.save(filepath, 'JPEG', quality=85)

    return f"uploads/avatars/{filename}"


def delete_old_avatar(avatar_path):
    """
    刪除舊的頭像檔案
    :param avatar_path: 頭像路徑
    """
    if avatar_path:
        old_avatar = os.path.join(current_app.root_path, 'static', avatar_path)
        if os.path.exists(old_avatar):
            os.remove(old_avatar)


# 認證相關路由
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """處理用戶登入"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('電子郵件或密碼錯誤', 'danger')
            return redirect(url_for('auth.login'))

        # 更新最後登入時間
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)

        # 處理下一頁重定向
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

        # 驗證輸入
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


@auth_bp.route('/logout')
@login_required
def logout():
    """處理用戶登出"""
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('main.index'))


# 個人資料管理路由
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """處理用戶個人資料更新"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            return handle_profile_update()
        elif action == 'update_password':
            return handle_password_update()

    return render_template('auth/profile.html', title='個人資料')


def handle_profile_update():
    """處理個人資料更新邏輯"""
    try:
        # 處理頭像上傳
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                # 刪除舊頭像
                delete_old_avatar(current_user.avatar_path)
                # 處理新頭像
                current_user.avatar_path = process_avatar_image(file, current_user.id)

        # 更新用戶資料
        new_username = request.form.get('username')
        new_email = request.form.get('email')

        # 驗證用戶名
        if new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                flash('此用戶名已被使用', 'danger')
                return redirect(url_for('auth.profile'))

        # 驗證電子郵件
        if new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('此電子郵件已被註冊', 'danger')
                return redirect(url_for('auth.profile'))

        # 更新資料
        current_user.username = new_username
        current_user.email = new_email
        db.session.commit()
        flash('個人資料已更新', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'更新失敗: {str(e)}', 'danger')

    return redirect(url_for('auth.profile'))


def handle_password_update():
    """處理密碼更新邏輯"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('目前密碼不正確', 'danger')
        elif new_password != confirm_password:
            flash('新密碼與確認密碼不符', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('密碼已更新', 'success')

    except Exception as e:
        db.session.rollback()
        flash('更新失敗', 'danger')

    return redirect(url_for('auth.profile'))
