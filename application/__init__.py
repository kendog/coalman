"""Initialize app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
sess = Session()
flask_bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)

    # Application Configuration
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    login_manager = LoginManager(app)
    sess.init_app(app)
    flask_bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    app.jinja_env.filters['datetime'] = format_datetime


    with app.app_context():
        # import parts of our application
        from . import auth
        from . import files
        from . import packages
        from . import profiles
        from . import tags
        from . import messages
        from . import pages
        from . import users

        return app

# jinja Date Stuff
def format_datetime(value, format='small'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE MM/dd/y HH:mm"
    elif format == 'small':
        format = "MM/dd/yy HH:mm"
    return babel.dates.format_datetime(value, format)
