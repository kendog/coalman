"""Routes for logged-in application."""
from flask import Blueprint, jsonify, render_template
from flask_login import current_user
from flask import current_app as app
from .schemas import FileSchema
from ..models import File, Tag, TagGroup
from flask_security import login_required
from ..import auth
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims)

# Schema Configurations
file_schema = FileSchema()
files_schema = FileSchema(many=True)

# Blueprint Configuration
v1_files_bp = Blueprint('v1_files_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/api/v1')


# FILE APIs
@v1_files_bp.route('/files', methods=['GET'])
@jwt_required
def files():
    results = files_schema.dump(File.query.all())
    return jsonify({'results': results})


@v1_files_bp.route('/file/<id>', methods=['GET'])
@jwt_required
def file(id):
    results = file_schema.dump(File.query.filter_by(id=id).first())
    return jsonify({'results': results.data})


@v1_files_bp.route('/request/package', methods=['POST', 'GET'])
@jwt_required
def request_package():
    results = {}
    if request.json:
        json_data = request.json  # will be

        user_name = json_data.get("user_name")
        user_email = json_data.get("user_email")
        file_ids = json_data.get("file_ids")

        package = Package(uuid=str(uuid.uuid4()), user_name=user_name, user_email=user_email)
        db.session.add(package)
        db.session.commit()
        package.package_status_id = 1
        package.notification_status_id = 1
        package.name = package.uuid + ".zip"
        package.path = app.config['TEMP_FOLDER']
        package.link = app.config['DOWNLOAD_PROTOCOL'] + '://' + app.config['DOWNLOAD_DOMAIN'] + url_for('download_package', uuid=package.uuid)
        db.session.commit()

        # Add Files
        for item in file_ids:
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                package.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if json_data.get("notify"):
            send_notification(package.uuid)

        results['status'] = 'success'
        results['uuid'] = package.uuid

    else:
        results['status'] = 'error - No JSON Payload'

    return jsonify({'results': results})
