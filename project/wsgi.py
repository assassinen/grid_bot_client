from flask import Blueprint, render_template
from flask_login import login_required, current_user
from project import app

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'Иван'},
            'body': 'Ура, Flask работает!'
        },
        {
            'author': {'username': 'Даша'},
            'body': 'Осталось разобраться с аутентификацией'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

if __name__ == '__main__':
    app.run()