"""Routes for logged-in application."""
from flask import Blueprint, render_template
from flask_login import current_user
from flask import current_app as app
#from .assets import compile_auth_assets
#from flask_login import login_required

# Blueprint Configuration
public_bp = Blueprint('public_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)


# Public Frontend
@public_bp.route('/')
def index():
    return render_template('index.html')
