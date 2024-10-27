from flask import render_template, Blueprint

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('/settings.html', title='設定')
