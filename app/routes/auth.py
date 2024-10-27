from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import os
import time


auth_bp = Blueprint('auth', __name__)


def allowed_file(filename):
    """檢查文件是否為允許的類型"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
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
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('登入成功！', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', title='登入')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
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

        if User.query.filter_by(email=email).first():
            flash('此電子郵件已被註冊', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('此用戶名已被使用', 'danger')
            return redirect(url_for('auth.register'))

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
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            try:
                # 處理頭像上傳
                if 'avatar' in request.files:
                    file = request.files['avatar']
                    if file and allowed_file(file.filename):
                        # 生成安全的文件名
                        filename = secure_filename(f"avatar_{current_user.id}_{int(time.time())}.jpg")
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                        # 保存並處理圖片
                        image = Image.open(file)
                        # 將圖片轉換為正方形
                        min_side = min(image.size)
                        left = (image.width - min_side) // 2
                        top = (image.height - min_side) // 2
                        right = left + min_side
                        bottom = top + min_side
                        image = image.crop((left, top, right, bottom))
                        # 調整大小
                        image = image.resize((300, 300), Image.Resampling.LANCZOS)
                        # 保存
                        image.save(filepath, 'JPEG', quality=85)

                        # 刪除舊頭像
                        if current_user.avatar_path:
                            old_avatar = os.path.join(current_app.root_path, 'static', current_user.avatar_path)
                            if os.path.exists(old_avatar):
                                os.remove(old_avatar)

                        # 更新數據庫
                        current_user.avatar_path = f"uploads/avatars/{filename}"

                # 檢查用戶名和郵箱是否被其他用戶使用
                new_username = request.form.get('username')
                new_email = request.form.get('email')

                if new_username != current_user.username:
                    if User.query.filter_by(username=new_username).first():
                        flash('此用戶名已被使用', 'danger')
                        return redirect(url_for('auth.profile'))

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

        elif action == 'update_password':
            # 密碼更新邏輯
            if not current_user.check_password(request.form.get('current_password')):
                flash('目前密碼不正確', 'danger')
            elif request.form.get('new_password') != request.form.get('confirm_password'):
                flash('新密碼與確認密碼不符', 'danger')
            else:
                try:
                    current_user.set_password(request.form.get('new_password'))
                    db.session.commit()
                    flash('密碼已更新', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('更新失敗', 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', title='個人資料')
