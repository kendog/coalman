import os
from flask import Blueprint, render_template, redirect, url_for, send_from_directory
from flask_login import current_user, login_required
from flask import current_app as app
#from .assets import compile_auth_assets
#from flask_login import login_required
from ..models import TagGroup, Account, Project
from sqlalchemy import or_, and_
import datetime


# Blueprint Configuration
pages_bp = Blueprint('pages_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)



# favicon for older bowsers
@pages_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Public Frontend
@pages_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('pages_bp.dashboard'))
    else:
        return redirect(url_for('security.login'))

@pages_bp.route('/dashboard')
@login_required
def dashboard():

    months_ago = datetime.datetime.now() + datetime.timedelta(-90)
    years_ago = datetime.datetime.now() + datetime.timedelta(-365)

    if current_user.has_role('super-admin'):
        projects = Project.query.all()
        return render_template('dashboard.html', projects=projects, months_ago=months_ago, years_ago=years_ago)
    else:
        projects = Project.query\
            .join(Account)\
            .filter(and_(Project.account_id == Account.id, Account.id == current_user.account_id))\
            .order_by(Project.account_id).all()
        return render_template('dashboard.html', months_ago=months_ago, years_ago=years_ago)


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
