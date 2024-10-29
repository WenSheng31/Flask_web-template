import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config


# 初始化資料庫
db = SQLAlchemy()

# 初始化登入管理器並配置
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # 設定登入頁面的路由
login_manager.login_message = '請先登入後再訪問此頁面'  # 設定未登入時的提示訊息
login_manager.login_message_category = 'warning'  # 設定提示訊息的樣式類別


@login_manager.user_loader
def load_user(id):
    """
    Flask-Login 的使用者載入回調函數
    :param id: 使用者 ID
    :return: 使用者實例
    """
    from app.models.user import User
    return User.query.get(int(id))


def register_blueprints(app):
    """
    註冊所有藍圖
    :param app: Flask 應用程式實例
    """
    # 導入所有藍圖
    from app.routes.main import main_bp
    from app.routes.settings import settings_bp
    from app.routes.auth import auth_bp
    from app.routes.post import post_bp

    # 註冊藍圖
    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)


def register_error_handlers(app):
    """
    註冊錯誤處理器
    :param app: Flask 應用程式實例
    """

    @app.errorhandler(404)
    def page_not_found(e):
        """處理 404 找不到頁面錯誤"""
        return render_template('errors/404.html', title='頁面未找到'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """處理 500 伺服器內部錯誤"""
        return render_template('errors/500.html', title='服務器錯誤'), 500


def register_template_filters(app):
    """
    註冊模板過濾器
    :param app: Flask 應用程式實例
    """

    @app.template_filter('nl2br')
    def nl2br_filter(s):
        """
        將換行符轉換為 HTML 的 <br> 標籤
        :param s: 輸入字串
        :return: 轉換後的字串
        """
        return s.replace('\n', '<br>') if s else ''


def configure_uploads(app):
    """
    配置檔案上傳相關設定
    :param app: Flask 應用程式實例
    """
    # 設定上傳檔案儲存路徑
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads/avatars')
    # 設定上傳檔案大小上限為 1MB
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
    # 確保上傳目錄存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def create_app(config_class=Config):
    """
    應用程式工廠函數
    :param config_class: 配置類，預設使用 Config
    :return: 配置完成的 Flask 應用程式實例
    """
    # 建立 Flask 應用程式實例
    app = Flask(__name__)

    # 載入配置
    app.config.from_object(config_class)

    # 配置檔案上傳
    configure_uploads(app)

    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)

    # 註冊藍圖、錯誤處理器和模板過濾器
    register_blueprints(app)
    register_error_handlers(app)
    register_template_filters(app)

    # 建立資料表
    with app.app_context():
        db.create_all()

    return app
