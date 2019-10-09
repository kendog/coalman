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
files_apis_bp = Blueprint('files_apis_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/api/v1')


# FILE APIs
@files_apis_bp.route('/files', methods=['GET'])
@jwt_required
def files():
    results = FileSchema(many=True).dump(File.query.all())
    return jsonify({'files': results})


@files_apis_bp.route('/file/<id>', methods=['GET'])
@jwt_required
def file(id):
    results = FileSchema().dump(File.query.filter_by(id=id).first())
    return jsonify({'file': results})
