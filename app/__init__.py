from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes.main import main_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)

    return app
