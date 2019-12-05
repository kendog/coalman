import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory, send_file
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from flask_security import roles_required, roles_accepted, current_user
from flask import current_app as app
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import File, Tag, TagGroup, Project
from werkzeug.utils import secure_filename
import boto3
import shutil
from sqlalchemy import or_, and_
from io import BytesIO
#from flask_wtf.csrf import CSRFProtect, CSRFError

s3_client = boto3.client(
   "s3",
   aws_access_key_id=app.config['AWS_ACCESS_KEY'],
   aws_secret_access_key=app.config['AWS_SECRET_KEY']
)

# Most "def" initly needed functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



# Blueprint Configuration
dropzone_bp = Blueprint('dropzone_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/dropzone')


# Basic Dropzone Example
@dropzone_bp.route('/basic')
@login_required
def basic():
    return render_template('/dropzone/basic.html')


@dropzone_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        uploaded_path = app.config['UPLOADED_PATH'] + '/' + current_user.email
        os.makedirs(uploaded_path, exist_ok=True)
        f = request.files.get('file')
        if allowed_file(f.filename):
            f.save(os.path.join(uploaded_path, f.filename))
    return redirect(url_for('dropzone_bp.completed'))


@dropzone_bp.route('/completed')
@login_required
def completed():
    return render_template('/dropzone/completed.html')


# handle CSRF error
#@dropzone_bp.errorhandler(CSRFError)
#def csrf_error(e):
#    return e.description, 400


#@dropzone_bp.route('/upload')
#@login_required
#def handle_upload():
#    if request.method == 'POST':
#        f = request.files.get('file')
#        if f.filename.split('.')[1] != 'png':
#            return 'PNG only!', 400  # return the error message, with a proper 4XX code
#        path = app.instance_path + app.config['UPLOAD_FOLDER'] + current_user.email + '/'
#        f.save(os.path.join('the/path/to/save', f.filename))
#    return render_template('index.html')
