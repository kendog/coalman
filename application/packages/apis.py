"""Routes for logged-in application."""
from flask import Blueprint, jsonify, render_template, request, url_for
from flask_login import current_user
from flask import current_app as app
#from ..schemas import FileSchema
from ..models import db, Package, File
from flask_security import login_required
from ..import auth
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims)
import uuid



# Blueprint Configuration
packages_apis_bp = Blueprint('packages_apis_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/api/v1')


@packages_apis_bp.route('/packages', methods=['GET'])
@jwt_required
def packages():
    packages = Package.query.all()
    return jsonify({'packages': packages})
    #return render_template('admin_packages.html', packages=packages)


@packages_apis_bp.route('/packages', methods=['POST'])
@jwt_required
def packages_add():
    results = {}
    if request.json:
        json_data = request.json  # will be

        recipient_name = json_data.get("recipient_name")
        recipient_email = json_data.get("recipient_email")
        file_ids = json_data.get("file_ids")

        package = Package(uuid=str(uuid.uuid4()), recipient_name=recipient_name, recipient_email=recipient_email)
        db.session.add(package)
        db.session.commit()
        package.package_status_id = 1
        package.notification_status_id = 1
        package.name = package.uuid + ".zip"
        package.path = app.config['TEMP_FOLDER']
        package.link = app.config['DOWNLOAD_PROTOCOL'] + '://' + app.config['DOWNLOAD_DOMAIN'] + url_for('packages_bp.download_package', uuid=package.uuid)
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

        return jsonify({'status': 'success','uuid':package.uuid,'link':package.link,'recipient_name':recipient_name,'recipient_email':recipient_email})
    else:
        return jsonify({'error': 'json not found'})

    return jsonify({'results': results})


@packages_apis_bp.route('/packages/<uuid>', methods=['PUT'])
@jwt_required
def packages_edit(uuid):
    results = {}
    if request.json:
        json_data = request.json  # will be

        recipient_name = json_data.get("recipient_name")
        recipient_email = json_data.get("recipient_email")
        file_ids = json_data.get("file_ids")

        package = Package.query.filter_by(uuid=uuid).first()
        package.recipient_name = recipient_name
        package.recipient_email = recipient_email
        package.files[:] = []
        db.session.commit()

        # Add Files
        for item in file_ids:
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                package.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if request.form.get("notify"):
            send_notification(package.uuid)

        return jsonify({'status': 'success','uuid':package.uuid,'link':package.link,'recipient_name':recipient_name,'recipient_email':recipient_email})
    else:
        return jsonify({'error': 'json not found'})

    return jsonify({'results': results})

@packages_apis_bp.route('/packages/<uuid>', methods=['DELETE'])
@jwt_required
def packages_delete(uuid):
    package = Package.query.filter_by(uuid=uuid).first()
    if package:
        db.session.delete(package)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'not found'})
