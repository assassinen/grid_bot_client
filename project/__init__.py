from flask import Flask
from .config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# init SQLAlchemy so we can use it later in our models
# db = SQLAlchemy()
# migrate = Migrate()

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login'

from .bots import bots as bots_blueprint
app.register_blueprint(bots_blueprint)

# blueprint for auth routes in our app
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .wsgi import main as main_blueprint
app.register_blueprint(main_blueprint)



# def create_app():
#     app = Flask(__name__)
#
#     # app.config['SECRET_KEY'] = 'secret-key-goes-here'
#     # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
#     # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     # app.config['DEBUG'] = True
#     app.config.from_object(Config)
#
#     db.init_app(app)
#     migrate.init_app(app, db)
#
#     login_manager = LoginManager()
#     login_manager.login_view = 'auth.login'
#     login_manager.init_app(app)
#
#     from .models import User
#
#     @login_manager.user_loader
#     def load_user(user_id):
#         # since the user_id is just the primary key of our user table, use it in the query for the user
#         return User.query.get(int(user_id))
#
#     from .bots import bots as bots_blueprint
#     app.register_blueprint(bots_blueprint)
#
#     # blueprint for auth routes in our app
#     from .auth import auth as auth_blueprint
#     app.register_blueprint(auth_blueprint)
#
#     # blueprint for non-auth parts of app
#     from .app import main as main_blueprint
#     app.register_blueprint(main_blueprint)
#
#     return app