import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required, current_user
from flask import current_app as app
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, File, Tag, TagGroup
from werkzeug.utils import secure_filename
import boto3
import shutil

s3_client = boto3.client(
   "s3",
   aws_access_key_id=app.config['AWS_ACCESS_KEY'],
   aws_secret_access_key=app.config['AWS_SECRET_KEY']
)

# Blueprint Configuration
files_bp = Blueprint('files_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


# Most "def" initly needed functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@files_bp.route('/download/file/<id>')
@login_required
def download_file(id):
    file = File.query.filter_by(id=id).first()
    return send_from_directory(file.path, file.name)


@files_bp.route('/error/uploads/<errors>')
@login_required
def error_uploads(errors):
    return render_template('error_uploads.html', errors=errors)



# Files Pages
@files_bp.route('/files')
@login_required
def files():
    files = []
    if current_user.has_role('admin'):
        files = File.query.all()
    else:
        files = File.query.filter_by(user_id=current_user.id).all()
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('files/list.html', files=files, tag_groups=tag_groups)


@files_bp.route('/files/add', methods=['POST', 'GET'])
@login_required
def files_add():
    if 'submit-add' in request.form:
        # Update Metadata
        file = File(title=request.form.get('title'), desc=request.form.get('desc'), user_id=current_user.id)
        db.session.add(file)
        db.session.commit()

        # Update Tags
        tags = request.form.getlist('tags')
        for item in tags:
            exists = db.session.query(Tag.id).filter_by(id=item).scalar()
            if exists:
                file.tags.append(Tag.query.filter_by(id=item).first())
                db.session.commit()

        # Upload File
        if 'file' in request.files:
            the_actual_file = request.files['file']
            if the_actual_file and allowed_file(the_actual_file.filename):
                directory = app.instance_path + app.config['UPLOAD_FOLDER'] + current_user.email + '/' + str(file.id) + '/'

                # Create DIR Python 3.2 or above
                os.makedirs(directory, exist_ok=True)
                # upload the file
                the_actual_file.save(os.path.join(directory, secure_filename(the_actual_file.filename)))
                # update the db
                file.name = secure_filename(the_actual_file.filename)
                file.path = directory
                db.session.commit()

                if app.config['UPLOAD_TO_S3']:
                    the_actual_file.filename = secure_filename(the_actual_file.filename)
                    s3_key = current_user.email + '/' + str(file.id) + '/' + the_actual_file.filename
                    s3_client.upload_file(os.path.join(directory, secure_filename(the_actual_file.filename)), app.config["S3_BUCKET"], s3_key, ExtraArgs={'ContentType': "application/pdf"})
                    s3_url = "{}{}".format(app.config["S3_URL"], s3_key)
                    file.s3_key = s3_key
                    file.s3_url = s3_url
                    db.session.commit()

        return redirect(url_for('files_bp.files'))

    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('files/form.html', template_mode='add', tag_groups=tag_groups, tag_hash=tag_hash)


@files_bp.route('/files/edit/<id>', methods=['POST', 'GET'])
@login_required
def files_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(File.id).filter_by(id=id).scalar()
        if exists:
            # Update Metadata
            file = File.query.filter_by(id=id).first()
            file.title = request.form.get('title')
            file.desc = request.form.get('desc')
            db.session.commit()

            # Update Tags
            tags = request.form.getlist('tags')
            new_tags = []
            for item in tags:
                exists = db.session.query(Tag.id).filter_by(id=item).scalar()
                if exists:
                    new_tags.append(Tag.query.filter_by(id=item).first())
            file.tags[:] = new_tags
            db.session.commit()

            # Upload File
            if 'file' in request.files:
                the_actual_file = request.files['file']
                if the_actual_file and allowed_file(the_actual_file.filename):
                    directory = app.instance_path + app.config['UPLOAD_FOLDER'] + current_user.email + '/' + str(file.id) + '/'

                    # Create DIR Python 3.2 or above
                    os.makedirs(directory, exist_ok=True)
                    # upload the file
                    the_actual_file.save(os.path.join(directory, secure_filename(the_actual_file.filename)))
                    # update the db
                    file.name = secure_filename(the_actual_file.filename)
                    file.path = directory
                    db.session.commit()

                    if app.config['UPLOAD_TO_S3']:
                        the_actual_file.filename = secure_filename(the_actual_file.filename)
                        s3_key = current_user.email + '/' + str(file.id) + '/' + the_actual_file.filename
                        s3_client.upload_file(os.path.join(directory, secure_filename(the_actual_file.filename)), app.config["S3_BUCKET"], s3_key, ExtraArgs={'ContentType': "application/pdf"})
                        s3_url = "{}{}".format(app.config["S3_URL"], s3_key)
                        file.s3_key = s3_key
                        file.s3_url = s3_url
                        db.session.commit()

            return redirect(url_for('files_bp.files'))

    file = File.query.filter_by(id=id).first()
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('files/form.html', template_mode='edit', file=file, tag_groups=tag_groups, tag_hash=tag_hash)


@files_bp.route('/files/delete/<id>', methods=['POST', 'GET'])
@login_required
def files_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(File.id).filter_by(id=id).scalar()
        if exists:
            file = File.query.filter_by(id=id).first()
            db.session.delete(file)
            db.session.commit()

            directory = app.instance_path + app.config['UPLOAD_FOLDER'] + current_user.email + '/' + str(file.id) + '/'
            shutil.rmtree(directory)

            if app.config['UPLOAD_TO_S3']:
                s3_key_prefix = current_user.email + '/' + str(file.id) + '/'
                for key in get_matching_s3_keys(bucket=app.config["S3_BUCKET"], prefix=s3_key_prefix):
                    s3_client.delete_object(Bucket=app.config["S3_BUCKET"], Key=key)
            return redirect(url_for('files_bp.files'))

    file = File.query.filter_by(id=id).first()
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('files/form.html', template_mode='delete', file=file, tag_groups=tag_groups, tag_hash=tag_hash)


def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3_client.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
