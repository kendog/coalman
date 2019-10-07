"""Routes for logged-in application."""
from flask import Blueprint, render_template, session
from flask_login import current_user
from flask import current_app as app
#from .assets import compile_auth_assets
#from flask_login import login_required
from flask_marshmallow import Marshmallow
from .models import TagGroup, Tag, File
from flask import jsonify


ma = Marshmallow()
# Blueprint Configuration
apis_bp = Blueprint('apis_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)

# Define Schemas
class TagGroupSchema(ma.Schema):
    class Meta:
        model = TagGroup
        # Fields to expose
        fields = ('name', 'tag_id')


class TagSchema(ma.Schema):
    tag_group = ma.Nested(TagGroupSchema)

    class Meta:
        model = Tag
        # Fields to expose
        fields = ('name', 'tag_id', 'tag_group')


class FileSchema(ma.Schema):
    tags = ma.Nested(TagGroupSchema, many=True)

    class Meta:
        model = File
        # Fields to expose
        fields = ('id', 'name', 'title', 'desc', 'tags')


file_schema = FileSchema()
files_schema = FileSchema(many=True)
tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
tag_group_schema = TagGroupSchema()
tag_groups_schema = TagGroupSchema(many=True)


# FILE APIs
@apis_bp.route('/api/v1/files', methods=['GET'])
def api_v1_files():
    results = files_schema.dump(File.query.all())
    return jsonify({'results': results})


@apis_bp.route('/api/v1/file/<id>', methods=['GET'])
def api_v1_file(id):
    results = file_schema.dump(File.query.filter_by(id=id).first())
    return jsonify({'results': results.data})


@apis_bp.route('/api/v1/request/package', methods=['POST', 'GET'])
def api_v1_request_package():
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


# Tags APIs
@apis_bp.route('/api/v1/tags', methods=['GET'])
def api_v1_tags_all():
    results = tags_schema.dump(Tag.query.order_by(Tag.tag_group_id, Tag.weight).all())
    return jsonify({'results': results.data})


@apis_bp.route('/api/v1/tags/<tag_group_tag>', methods=['GET'])
def api_v1_tags(tag_group_tag):
    tag_group = TagGroup.query.filter_by(tag_id=tag_group_tag).first()
    results = tags_schema.dump(Tag.query.filter_by(tag_group=tag_group).order_by(Tag.weight).all())
    return jsonify({'results': results.data})


@apis_bp.route('/api/v1/tag_groups', methods=['GET'])
def api_v1_tag_groups():
    results = tag_groups_schema.dump(TagGroup.query.order_by(TagGroup.weight).all())
    return jsonify({'results': results.data})
