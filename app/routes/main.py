from flask import render_template, Blueprint

main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route('/')
def index():
    return render_template('main/index.html', title='首頁')

@main_bp.route('/about')
def about():
    return render_template('main/about.html', title='關於我們')
