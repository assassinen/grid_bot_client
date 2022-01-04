from flask import Blueprint, render_template
from flask_login import login_required, current_user
from project import app, db

main = Blueprint('main', __name__)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


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


if __name__ == '__main__':
    app.run()
