from flask import current_app as app
from ..models import User, MessageTemplate, Notification
from flask_security import current_user
from ..db import db
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory, send_file
from ..models import User, File, Tag
from flask_mail import Message
from .. import mail
import boto3
from werkzeug.utils import secure_filename
import os
import shutil
from io import BytesIO



s3_client = boto3.client(
   "s3",
   aws_access_key_id=app.config['AWS_ACCESS_KEY'],
   aws_secret_access_key=app.config['AWS_SECRET_KEY']
)

# Most "def" initly needed functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



def get_s3_file(s3_bucket, s3_key):
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    memory_file = BytesIO(response["Body"].read())
    return send_file(memory_file, attachment_filename="preview.pdf", as_attachment=False)


def get_file(file_id):
    file = File.query.filter_by(id=file_id).first()
    if app.config['UPLOAD_TO_S3']:
        response = s3_client.get_object(Bucket=app.config['S3_BUCKET'], Key=file.s3_key)
        memory_file = BytesIO(response["Body"].read())
        return send_file(memory_file, attachment_filename=file.name, as_attachment=False)
    else:
        return send_from_directory(file.path, file.name)


def update_file_tags(file_id, tag_list):
    tags = []
    for item in tag_list:
        exists = db.session.query(Tag.id).filter_by(id=item).scalar()
        if exists:
            tags.append(Tag.query.filter_by(id=item).first())

    file = File.query.filter_by(id=file_id).first()
    file.tags[:] = tags
    db.session.commit()



def upload_file(file_id, the_request_file):

    if the_request_file and allowed_file(the_request_file.filename):
        file = File.query.filter_by(id=file_id).first()

        directory = app.instance_path + app.config['UPLOAD_FOLDER'] + current_user.email + '/' + str(file.id) + '/'

        # Create DIR Python 3.2 or above
        os.makedirs(directory, exist_ok=True)
        # upload the file
        filename = secure_filename(the_request_file.filename)
        filepath = os.path.join(directory, filename)
        the_request_file.save(filepath)
        # update the db
        file.name = filename
        file.path = directory
        db.session.commit()

        if app.config['UPLOAD_TO_S3']:
            upload_to_s3(file.id)


def upload_to_s3(file_id):
    file = File.query.filter_by(id=file_id).first()
    s3_key = current_user.email + '/' + str(file.id) + '/' + file.name
    s3_client.upload_file(file.path + file.name, app.config["S3_BUCKET"], s3_key, ExtraArgs={'ContentType': "application/pdf"})
    file.s3_key = s3_key
    file.s3_url = "{}{}".format(app.config["S3_URL"], s3_key)
    db.session.commit()


def delete_file(file_id):
    directory = app.instance_path + app.config['UPLOAD_FOLDER'] + current_user.email + '/' + str(file_id) + '/'
    if os.path.exists(directory):
        shutil.rmtree(directory)

    if app.config['UPLOAD_TO_S3']:
        delete_dir_from_s3(file_id)


def delete_dir_from_s3(file_id):
    s3_key_prefix = current_user.email + '/' + str(file_id) + '/'
    for key in get_matching_s3_keys(bucket=app.config["S3_BUCKET"], prefix=s3_key_prefix):
        s3_client.delete_object(Bucket=app.config["S3_BUCKET"], Key=key)


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

        try:
            contents = resp['Contents']
        except KeyError:
            return

        for obj in contents:
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
