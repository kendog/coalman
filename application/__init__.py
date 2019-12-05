"""Initialize app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import babel
from flask_security import Security, SQLAlchemyUserDatastore, utils
from .db import db
from .models import User, Role
from flask_mail import Mail
#from flask_moment import Moment
#from flask_wtf.csrf import CSRFProtect
from flask_dropzone import Dropzone

login_manager = LoginManager()
sess = Session()
flask_bcrypt = Bcrypt()
jwt = JWTManager()
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
mail = Mail()


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
    mail.init_app(app)
    #moment = Moment(app)
    #csrf = CSRFProtect(app)
    dropzone = Dropzone(app)

    migrate = Migrate(app, db)
    security = Security(app, user_datastore)

    app.jinja_env.filters['datetime'] = format_datetime
    #app.jinja_env.globals['momentjs'] = momentjs


    with app.app_context():

        # import parts of our application
        from . import auth
        from . import files
        from . import archives
        from . import profiles
        from . import accounts
        from . import projects
        from . import tags
        from . import message_templates
        from . import pages
        from . import users
        from . import notifications
#        from . import issues
#        from . import calendar
#        from . import specs
#        from . import specmanager
        from . import seed
        return app


# jinja Date Stuff
def format_datetime(value, format='default'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'dateonly':
        format="MM/dd/YYYY"
    elif format == 'default':
        format = "MM/dd/yy HH:mm"
    return babel.dates.format_datetime(value, format)
