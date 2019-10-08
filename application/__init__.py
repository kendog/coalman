"""Initialize app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate


db = SQLAlchemy()
login_manager = LoginManager()
sess = Session()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)

    # Application Configuration
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    login_manager = LoginManager(app)
    sess.init_app(app)

    migrate = Migrate(app, db)

    with app.app_context():
        # import parts of our application
        from . import apis
        #from . import auth
        from . import files
        from . import packages
        from . import profiles
        from . import tags
        from . import messages
        from . import public
        from . import users


        return app