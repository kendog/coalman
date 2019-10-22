"""Routes for logged-in application."""
from flask import Blueprint, jsonify, render_template
from flask_login import current_user
from flask import current_app as app
from ..schemas import FileSchema
from ..models import File, Tag, TagGroup
from flask_security import login_required
from ..import auth
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims)


# Blueprint Configuration
notifications_apis_bp = Blueprint('notifications_apis_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/api/v1')


# Notification APIs
@notifications_apis_bp.route('/sms', methods=['POST'])
@jwt_required
def sms():
    return jsonify({'sms': 'stub'})


@notifications_apis_bp.route('/email', methods=['POST'])
@jwt_required
def email(id):
    return jsonify({'email': 'stub'})
