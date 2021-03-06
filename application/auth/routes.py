''' controller and routes for users '''
import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)
from flask_jwt_extended import get_jwt_claims

from flask import current_app as app
from flask_jwt_extended import JWTManager
from ..db import db
from ..models import User, Role, roles_users
from flask_security import SQLAlchemyUserDatastore, utils


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)

jwt = JWTManager(app)

# Blueprint Configuration
auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/auth')



@jwt.user_claims_loader
def add_claims_to_access_token(current_user):
    user = user_datastore.get_user(current_user)
    roles = Role.query.join(roles_users).join(User).filter((roles_users.c.user_id == User.id) & (roles_users.c.role_id == Role.id)).filter(User.email == current_user).all()
    return {
        'username': current_user,
        'roles': roles[0].name
    }


@auth_bp.route('', methods=['POST'])
def auth_user():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({"error": "Invalid Credentials"}), 400

    user = user_datastore.get_user(username)
    if user and utils.verify_password(password, user.password):
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return jsonify({"access_token":access_token,"refresh_token":refresh_token}), 200

    return jsonify({"error": "Invalid Credentials"}), 400


@auth_bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({"access_token":access_token}), 200


@auth_bp.route('/claims', methods=['GET'])
@jwt_required
def protected():
    return jsonify(get_jwt_claims()), 200
