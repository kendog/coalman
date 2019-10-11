"""Routes for logged-in application."""
from flask import Blueprint, jsonify, render_template, request, url_for
from flask_login import current_user
from flask import current_app as app
#from ..schemas import FileSchema
from ..models import db, Archive, File
from flask_security import login_required
from ..import auth
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims)
import uuid



# Blueprint Configuration
archives_apis_bp = Blueprint('archives_apis_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/api/v1')


@archives_apis_bp.route('/archives', methods=['GET'])
@jwt_required
def archives():
    archives = Archive.query.all()
    return jsonify({'archives': archives})
    #return render_template('admin_archives.html', archives=archives)


@archives_apis_bp.route('/archives', methods=['POST'])
@jwt_required
def archives_add():
    results = {}
    if request.json:
        json_data = request.json  # will be

        recipient_name = json_data.get("recipient_name")
        recipient_email = json_data.get("recipient_email")
        file_ids = json_data.get("file_ids")

        archive = Archive(uuid=str(uuid.uuid4()), recipient_name=recipient_name, recipient_email=recipient_email)
        db.session.add(archive)
        db.session.commit()
        archive.archive_status_id = 1
        archive.notification_status_id = 1
        archive.name = archive.uuid + ".zip"
        archive.path = app.config['TEMP_FOLDER']
        archive.link = app.config['DOWNLOAD_PROTOCOL'] + '://' + app.config['DOWNLOAD_DOMAIN'] + url_for('archives_bp.download_archive', uuid=archive.uuid)
        db.session.commit()

        # Add Files
        for item in file_ids:
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                archive.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if json_data.get("notify"):
            send_notification(archive.uuid)

        return jsonify({'status': 'success','uuid':archive.uuid,'link':archive.link,'recipient_name':recipient_name,'recipient_email':recipient_email})
    else:
        return jsonify({'error': 'json not found'})

    return jsonify({'results': results})


@archives_apis_bp.route('/archives/<uuid>', methods=['PUT'])
@jwt_required
def archives_edit(uuid):
    results = {}
    if request.json:
        json_data = request.json  # will be

        recipient_name = json_data.get("recipient_name")
        recipient_email = json_data.get("recipient_email")
        file_ids = json_data.get("file_ids")

        archive = Archive.query.filter_by(uuid=uuid).first()
        archive.recipient_name = recipient_name
        archive.recipient_email = recipient_email
        archive.files[:] = []
        db.session.commit()

        # Add Files
        for item in file_ids:
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                archive.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if request.form.get("notify"):
            send_notification(archive.uuid)

        return jsonify({'status': 'success','uuid':archive.uuid,'link':archive.link,'recipient_name':recipient_name,'recipient_email':recipient_email})
    else:
        return jsonify({'error': 'json not found'})

    return jsonify({'results': results})

@archives_apis_bp.route('/archives/<uuid>', methods=['DELETE'])
@jwt_required
def archives_delete(uuid):
    archive = Archive.query.filter_by(uuid=uuid).first()
    if archive:
        db.session.delete(archive)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'not found'})
