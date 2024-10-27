from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from urllib.parse import urlparse
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

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
            # 檢查用戶名是否已存在
            if (request.form.get('username') != current_user.username and
                    User.query.filter_by(username=request.form.get('username')).first()):
                flash('此用戶名已被使用', 'danger')
                return redirect(url_for('auth.profile'))

            # 檢查郵箱是否已存在
            if (request.form.get('email') != current_user.email and
                    User.query.filter_by(email=request.form.get('email')).first()):
                flash('此電子郵件已被註冊', 'danger')
                return redirect(url_for('auth.profile'))

            try:
                current_user.username = request.form.get('username')
                current_user.email = request.form.get('email')
                db.session.commit()
                flash('個人資料已更新', 'success')
            except Exception as e:
                db.session.rollback()
                flash('更新失敗', 'danger')

            return redirect(url_for('auth.profile'))

        elif action == 'update_password':
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
