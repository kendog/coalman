"""Routes for logged-in application."""
from flask import Blueprint, jsonify, render_template
from flask_login import current_user
from flask import current_app as app
from ..models import TagGroup
from flask_security import login_required
from ..import auth
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims)


# Blueprint Configuration
apis_bp = Blueprint('apis_bp', __name__,
                    template_folder='templates',
                    static_folder='static')

# Documentation
@apis_bp.route('/api')
@login_required
def admin_apis():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_apis.html', tag_groups=tag_groups)
