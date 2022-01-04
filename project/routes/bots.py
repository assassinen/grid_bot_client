from flask import Blueprint, render_template
from flask_login import login_required, current_user

bots = Blueprint('bots', __name__)

@bots.route('/list')
@login_required
def list():
    return 'hello1'

