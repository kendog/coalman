''' controller and routes for users '''
import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims)
from flask import current_app as app
from flask_jwt_extended import JWTManager
from ..models import db, User, Role
from flask_security import SQLAlchemyUserDatastore, utils


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)

jwt = JWTManager(app)

# Blueprint Configuration
auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static')



@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {
        'username': identity['username'],
        'role': identity['role']
    }


@app.route('/auth', methods=['POST'])
def auth_user():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    # Create an example UserObject
    #user = User.query.filter_by(email=username).first()
    user = user_datastore.get_user(username)
    if user and utils.verify_password(password, user.password):

        # Identity can be any data that is json serializable
        identity = {}
        identity['username'] = user.email
        identity['end-user'] = "admin"
        if user.has_role("admin"):
            identity['role'] = "admin"

        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify({"access_token":access_token,"refresh_token":refresh_token}), 200

    return jsonify({"msg": "Invalid Credentials"}), 400
