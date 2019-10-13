"""Routes for logged-in application."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from flask import current_app as app
#from .assets import compile_auth_assets
#from flask_login import login_required
from ..models import TagGroup


# Blueprint Configuration
pages_bp = Blueprint('pages_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)


# Public Frontend
@pages_bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    else:
        return render_template('index.html')


# API Documentation
#@pages_bp.route('/dashboard')
#@login_required
#def dashboard():
#    return render_template('dashboard.html')


# API Documentation
@pages_bp.route('/api')
@login_required
def api_documetation():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('apis.html', tag_groups=tag_groups)
