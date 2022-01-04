from flask import Blueprint, render_template
from flask_login import login_required, current_user
from project import app

main = Blueprint('main', __name__)

# app = create_app()

#
# @main.route('/')
# def index():
#     return render_template('index.html')

@main.route('/')
@main.route('/index')
@login_required
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
    return render_template('profile.html', name=current_user.name)

if __name__ == '__main__':
    app.run()
