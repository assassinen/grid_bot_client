from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from .models import User
from .forms import LoginForm, RegistrationForm
from . import db, app

auth = Blueprint('auth', __name__)

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     email = request.form.get('username')
#     password = request.form.get('password')
#     remember = True if request.form.get('remember') else False
#
#     user = User.query.filter_by(email=email).first()
#     if not user or not check_password_hash(user.password, password):
#         flash('Please check your login details and try again.')
#         return render_template('login.html',  title='Sign In', form=form)
#
#     login_user(user, remember=remember)
#     return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

# @auth.route('/login')
# def login():
#     return render_template('__login.html')
#
#
# @auth.route('/login', methods=['POST'])
# def login_post():
#     email = request.form.get('email')
#     password = request.form.get('password')
#     remember = True if request.form.get('remember') else False
#
#     user = User.query.filter_by(email=email).first()
#     if not user or not check_password_hash(user.password, password):
#         flash('Please check your login details and try again.')
#         return redirect(url_for('auth.login'))
#
#     login_user(user, remember=remember)
#     return redirect(url_for('main.profile'))


# @auth.route('/signup')
# def signup():
#     return render_template('signup.html')
#
#
# @auth.route('/signup', methods=['POST'])
# def signup_post():
#     email = request.form.get('email')
#     name = request.form.get('name')
#     password = request.form.get('password')
#
#     user = User.query.filter_by(email=email).first()
#     if user:
#         flash('Email address already exists')
#         return redirect(url_for('auth.signup'))
#
#     new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
#
#     db.session.add(new_user)
#     db.session.commit()
#
#     return redirect(url_for('auth.login'))
#
#
# @auth.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('main.index'))
