import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user, login_required, roles_required, utils
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
import zipfile
from flask_cors import CORS
import datetime
import uuid
import smtplib

# Create app
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['UPLOAD_FOLDER'] = app.root_path + app.config['UPLOAD_FOLDER']

db = SQLAlchemy(app)
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})




# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('Users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('Roles.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    # If we were using Python 2.7, this would be __unicode__ instead.

    def __unicode__ (self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('Users', lazy='dynamic'))


tags_files = db.Table('tags_files',
    db.Column('tag_id', db.Integer, db.ForeignKey('Tags.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True)
)


class File(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    title = db.Column(db.String(255))
    desc = db.Column(db.UnicodeText())
    tags = db.relationship('Tag', secondary=tags_files, lazy='subquery', backref=db.backref('Files', lazy=True))
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


class Tag(db.Model):
    __tablename__ = 'Tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    weight = db.Column(db.Integer())
    tag_group_id = db.Column(db.Integer, db.ForeignKey('TagGroups.id'))
    tag_group = db.relationship("TagGroup", back_populates="tags")
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)

class TagGroup(db.Model):
    __tablename__ = 'TagGroups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    weight = db.Column(db.Integer())
    tags = db.relationship("Tag", back_populates="tag_group")
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


packages_files = db.Table('packages_files',
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True),
    db.Column('package_id', db.Integer, db.ForeignKey('Packages.id'), primary_key=True)
)


class Package(db.Model):
    __tablename__ = 'Packages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    user_name = db.Column(db.String(255))
    user_email = db.Column(db.String(255))
    files = db.relationship('File', secondary=packages_files, lazy='subquery', backref=db.backref('Packages', lazy=True))
    package_status_id = db.Column(db.Integer, db.ForeignKey('PackageStatuses.id'))
    package_status = db.relationship("PackageStatus", back_populates="packages")
    notification_status_id = db.Column(db.Integer, db.ForeignKey('NotificationStatuses.id'))
    notification_status = db.relationship("NotificationStatus", back_populates="packages")
    downloads = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


class PackageStatus(db.Model):
    __tablename__ = 'PackageStatuses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    packages = db.relationship("Package", back_populates="package_status")


class NotificationStatus(db.Model):
    __tablename__ = 'NotificationStatuses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    packages = db.relationship("Package", back_populates="notification_status")


class NotificationSetting(db.Model):
    __tablename__ = 'NotificationSettings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(255))
    message = db.Column(db.UnicodeText())
    login = db.Column(db.String(255))
    password = db.Column(db.String(255))
    smtp_server = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


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


# Most "def" initly needed functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def package_files(uuid):
    package = Package.query.filter_by(uuid=uuid).first()
    package.package_status_id = 2
    db.session.commit()
    zf = zipfile.ZipFile(package.path + package.name, "w", zipfile.ZIP_DEFLATED)
    for file in package.files:
        absname = os.path.abspath(os.path.join(file.path + file.name))
        arcname = absname[len(file.path):]
        zf.write(absname, arcname)
    zf.close()
    package.package_status_id = 3
    db.session.commit()


def send_notification(uuid):
    notification_settings = NotificationSetting.first()
    package = Package.query.filter_by(uuid=uuid).first()
    package.notification_status_id = 2
    db.session.commit()
    # Build the Mail
    header = 'From: %s\n' % notification_settings.login
    header += 'To: %s\n' % ','.join(package.user_email)
    header += 'Subject: %s\n\n' % notification_settings.subject
    message = header + notification_settings.message + '\n\n' + package.url
    # Send the Mail
    server = smtplib.SMTP(notification_settings.smtp_server)
    server.starttls()
    server.login(notification_settings.login, notification_settings.password)
    results = server.sendmail(notification_settings.login, package.user_email, message)
    server.quit()
    print results
    package.notification_status_id = 3
    db.session.commit()
    return results


# First Run / Init
@app.before_first_request
def create_db():
    db.create_all()
    # Populate Package Statuses
    package_statuses = PackageStatus.query.first()
    if package_statuses is None:
        db.session.add(PackageStatus(name="Waiting", tag_id="waiting"))
        db.session.add(PackageStatus(name="In Progress", tag_id="in-progress"))
        db.session.add(PackageStatus(name="Completed", tag_id="completed"))
        db.session.add(PackageStatus(name="Error", tag_id="error"))
        db.session.commit()
    notification_statuses = NotificationStatus.query.first()
    if notification_statuses is None:
        db.session.add(NotificationStatus(name="Waiting", tag_id="waiting"))
        db.session.add(NotificationStatus(name="In Progress", tag_id="in-progress"))
        db.session.add(NotificationStatus(name="Sent", tag_id="sent"))
        db.session.add(NotificationStatus(name="Error", tag_id="error"))
        db.session.commit()
    # Populate Roles, Admin and Users
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='end-user', description='End user')
    db.session.commit() 
    user = User.query.first()
    if user is None:
        encrypted_password = utils.hash_password('123456')
        user_datastore.create_user(email='admin@coalman.com', password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user('admin@coalman.com', 'admin')
        db.session.commit()


# Public Frontend
@app.route('/')
def index():
    return redirect(url_for('admin'))


# FILE APIs
@app.route('/api/v1/files', methods=['GET'])
def api_v1_files():
    results = files_schema.dump(File.query.all())
    return jsonify({'results': results.data})


@app.route('/api/v1/file/<id>', methods=['GET'])
def api_v1_file(id):
    results = file_schema.dump(File.query.filter_by(id=id).first())
    return jsonify({'results': results.data})


@app.route('/download/file/<id>')
@login_required
def download_file(id):
    file = File.query.filter_by(id=id).first()
    return send_from_directory(file.path, file.name)


@app.route('/api/v1/request/package', methods=['POST', 'GET'])
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
        db.session.commit()

        # Add Files
        for item in file_ids:
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                package.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        #send_notification(package.uuid)

        results['status'] = 'success'
        results['uuid'] = package.uuid

    else:
        results['status'] = 'error - No JSON Payload'

    return jsonify({'results': results})


@app.route('/download/package/<uuid>')
def download_package(uuid):
    package = Package.query.filter_by(uuid=uuid).first()
    # check for package first...
    if not os.path.isfile(package.path + package.name):
        # File does not exist...  Create Package
        package_files(package.uuid)
    package.downloads += 1
    db.session.commit()
    return send_from_directory(package.path, package.name)


# Tags APIs
@app.route('/api/v1/tags', methods=['GET'])
def api_v1_tags_all():
    results = tags_schema.dump(Tag.query.order_by(Tag.tag_group_id, Tag.weight).all())
    return jsonify({'results': results.data})


@app.route('/api/v1/tags/<tag_group_tag>', methods=['GET'])
def api_v1_tags(tag_group_tag):
    tag_group = TagGroup.query.filter_by(tag_id=tag_group_tag).first()
    results = tags_schema.dump(Tag.query.filter_by(tag_group=tag_group).order_by(Tag.weight).all())
    return jsonify({'results': results.data})


@app.route('/api/v1/tag_groups', methods=['GET'])
def api_v1_tag_groups():
    results = tag_groups_schema.dump(TagGroup.query.order_by(TagGroup.weight).all())
    return jsonify({'results': results.data})


# ADMIN Pages
@app.route('/admin')
@login_required
def admin():
    return redirect(url_for('admin_files'))


@app.route('/admin/files')
@login_required
def admin_files():
    files = File.query.all()
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_files.html', files=files, tag_groups=tag_groups)


@app.route('/admin/files/add', methods=['POST', 'GET'])
@login_required
def admin_files_add():
    if 'submit-add' in request.form:
        # Update Metadata
        file = File(title=request.form.get('title'), desc=request.form.get('desc'))
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
                # upload the file
                the_actual_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(the_actual_file.filename)))
                # update the db
                file.name = secure_filename(the_actual_file.filename)
                file.path = app.config['UPLOAD_FOLDER']
                db.session.commit()

        return redirect(url_for('admin_files'))

    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_add.html', tag_groups=tag_groups, tag_hash=tag_hash)


@app.route('/error/uploads/<errors>')
@login_required
def error_uploads(errors):
    return render_template('error_uploads.html', errors=errors)


@app.route('/admin/files/edit/<id>', methods=['POST', 'GET'])
@login_required
def admin_files_edit(id):
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
                    # upload the file
                    the_actual_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(the_actual_file.filename)))
                    # update the db
                    file.name = secure_filename(the_actual_file.filename)
                    file.path = app.config['UPLOAD_FOLDER']
                    db.session.commit()

            return redirect(url_for('admin_files'))

    file = File.query.filter_by(id=id).first()
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_edit.html', file=file, tag_groups=tag_groups, tag_hash=tag_hash)


@app.route('/admin/files/delete/<id>', methods=['POST', 'GET'])
@login_required
def admin_files_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(File.id).filter_by(id=id).scalar()
        if exists:
            file = File.query.filter_by(id=id).first()
            db.session.delete(file)
            db.session.commit()
            return redirect(url_for('admin_files'))
    file = File.query.filter_by(id=id).first()
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_delete.html', file=file, tag_groups=tag_groups, tag_hash=tag_hash)


@app.route('/admin/apis')
@roles_required('admin')
def admin_apis():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_apis.html', tag_groups=tag_groups)


@app.route('/admin/tags')
@roles_required('admin')
def admin_tags_all():
    return redirect(url_for('admin_tags', tag_group_tag='all'))


@app.route('/admin/tags/<tag_group_tag>')
@roles_required('admin')
def admin_tags(tag_group_tag):
    tag_groups = TagGroup.query.all()
    tag_group = None
    if tag_group_tag == 'all':
        tags = Tag.query.order_by(Tag.weight).all()
    else:
        tag_group = TagGroup.query.filter_by(tag_id=tag_group_tag).first()
        tags = Tag.query.filter_by(tag_group_id=tag_group.id).order_by(Tag.weight).all()
    return render_template('admin_tags.html', tags=tags, tag_group=tag_group, tag_groups=tag_groups)


@app.route('/admin/tags/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tags_add():
    if 'submit-add' in request.form:
        tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
        db.session.add(Tag(name=request.form['name'], tag_id=request.form['tag_id'], tag_group=tag_group, weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('admin_tags', tag_group_tag=tag_group.tag_id))
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_add.html', tag_groups=tag_groups)


@app.route('/admin/tags/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tags_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(Tag.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
            tag = Tag.query.filter_by(id=id).first()
            tag.name = request.form.get('name')
            tag.tag_id = request.form.get('tag_id')
            tag.tag_group = tag_group
            tag.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('admin_tags', tag_group_tag=tag_group.tag_id))
    tag = Tag.query.filter_by(id=id).first()
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_edit.html', tag=tag, tag_groups=tag_groups)


@app.route('/admin/tags/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tags_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(Tag.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
            tag = Tag.query.filter_by(id=id).first()
            db.session.delete(tag)
            db.session.commit()
            return redirect(url_for('admin_tags', tag_group_tag=tag_group.tag_id))
    tag = Tag.query.filter_by(id=id).first()
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_delete.html', tag=tag, tag_groups=tag_groups)


@app.route('/admin/tag_groups')
@roles_required('admin')
def admin_tag_groups():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_tag_groups.html', tag_groups=tag_groups)


@app.route('/admin/tag_groups/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tag_groups_add():
    if 'submit-add' in request.form:
        db.session.add(TagGroup(name=request.form['name'], tag_id=request.form['tag_id'], weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('admin_tag_groups'))
    return render_template('admin_tag_groups_add.html')


@app.route('/admin/tag_groups/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tag_groups_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(TagGroup.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=id).first()
            tag_group.name = request.form.get('name')
            tag_group.tag_id = request.form.get('tag_id')
            tag_group.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('admin_tag_groups'))
    tag_group = TagGroup.query.filter_by(id=id).first()
    return render_template('admin_tag_groups_edit.html', tag_group=tag_group)


@app.route('/admin/tag_groups/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tag_groups_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(TagGroup.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=id).first()
            db.session.delete(tag_group)
            db.session.commit()
            return redirect(url_for('admin_tag_groups'))
    tag_group = TagGroup.query.filter_by(id=id).first()
    return render_template('admin_tag_groups_delete.html', tag_group=tag_group)


@app.route('/admin/packages')
@roles_required('admin')
def admin_packages():
    packages = Package.query.all()
    return render_template('admin_packages.html', packages=packages)


@app.route('/admin/packages/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_packages_add():
    if 'submit-add' in request.form:
        # Update Metadata
        package = Package(uuid=str(uuid.uuid4()), user_name=request.form.get('user_name'), user_email=request.form.get('user_email'))
        db.session.add(package)
        db.session.commit()
        package.package_status_id = 1
        package.notification_status_id = 1
        package.name = package.uuid + ".zip"
        package.path = app.config['TEMP_FOLDER']
        db.session.commit()
        # Add Files
        file_ids = request.form.getlist('files')
        for item in file_ids:
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                package.files.append(File.query.filter_by(id=item).first())
                db.session.commit()
        return redirect(url_for('admin_packages'))
    files = File.query.all()
    return render_template('admin_packages_add.html', files=files)


@app.route('/admin/packages/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_packages_delete(id):
    package = Package.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if package:
            db.session.delete(package)
            db.session.commit()
            return redirect(url_for('admin_packages'))
    return render_template('admin_packages_delete.html', package=package)


@app.route('/admin/users')
@roles_required('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_users_add():
    if 'submit-add' in request.form:
        encrypted_password = utils.hash_password(request.form['password'])
        user_datastore.create_user(email=request.form['email'], password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user(request.form['email'], request.form['role'])
        db.session.commit()
        return redirect(url_for('admin_users'))
    roles = Role.query.all()
    return render_template('admin_users_add.html', roles=roles)


@app.route('/admin/users/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_users_edit(id):
    if 'submit-edit' in request.form:
        exists = user_datastore.get_user(id)
        if exists:
            user = user_datastore.get_user(id)
            user_datastore.remove_role_from_user(user.email, 'admin')
            user_datastore.remove_role_from_user(user.email, 'end-user')
            user_datastore.add_role_to_user(user.email, request.form['role'])
            db.session.commit()
        return redirect(url_for('admin_users'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    return render_template('admin_users_edit.html', user=user, roles=roles)


@app.route('/admin/users/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_users_delete(id):
    if 'submit-delete' in request.form:
        exists = user_datastore.get_user(id)
        if exists:
            user = user_datastore.get_user(id)
            db.session.delete(user)
            db.session.commit()
        return redirect(url_for('admin_users'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    return render_template('admin_users_delete.html', user=user, roles=roles)


if __name__ == "__main__":
    app.run('localhost')
