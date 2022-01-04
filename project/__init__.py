from flask import Flask
from .config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'users.login'

from project.routes.bots import bots as bots_blueprint
app.register_blueprint(bots_blueprint)

# blueprint for users routes in our app
from project.routes.users import users as user_blueprint
app.register_blueprint(user_blueprint)

# blueprint for non-users parts of app
from .wsgi import main as main_blueprint
app.register_blueprint(main_blueprint)
