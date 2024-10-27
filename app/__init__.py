from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    from app.models.user import User
    return User.query.get(int(id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 配置上傳路徑
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads/avatars')
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 限制上傳大小為 1MB

    # 確保上傳目錄存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 設置登入頁面的端點
    login_manager.login_message = '請先登入後再訪問此頁面'  # 自定義提示訊息
    login_manager.login_message_category = 'warning'  # 設置提示訊息的類別

    # 註冊藍圖
    from app.routes.main import main_bp
    from app.routes.settings import settings_bp
    from app.routes.auth import auth_bp
    from app.routes.post import post_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)

    # 添加自定義過濾器
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        return s.replace('\n', '<br>') if s else ''

    # 確保錯誤處理模板存在
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # 創建所有數據表
    with app.app_context():
        db.create_all()

    return app
