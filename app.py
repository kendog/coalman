import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user, login_required, roles_required, utils
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
import zipfile
from flask_cors import CORS

# Create app
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['UPLOAD_FOLDER'] = app.root_path + '/uploads/'
app.config['DOWNLOAD_FOLDER'] = app.root_path + '/downloads/'
app.config['ALLOWED_EXTENSIONS'] = set(['pdf', 'PDF', 'png', 'PNG'])

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


filters_files = db.Table('tags',
    db.Column('filter_id', db.Integer, db.ForeignKey('Filters.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True)
)


class File(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    title = db.Column(db.String(255))
    desc = db.Column(db.String(255))
    filters = db.relationship('Filter', secondary=filters_files, lazy='subquery', backref=db.backref('Files', lazy=True))


class Filter(db.Model):
    __tablename__ = 'Filters'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    filter_type = db.Column(db.String(225))
    weight = db.Column(db.Integer())
    filter_type_id = db.Column(db.Integer, db.ForeignKey('FilterTypes.id'))
    filter_type = db.relationship("FilterType", back_populates="filters")


class FilterType(db.Model):
    __tablename__ = 'FilterTypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    tag = db.Column(db.String(255))
    filters = db.relationship("Filter", back_populates="filter_type")


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Define Schemas
class FilterTypeSchema(ma.Schema):
    class Meta:
        model = FilterType
        # Fields to expose
        fields = ('name', 'tag')


class FilterSchema(ma.Schema):
    filter_type = ma.Nested(FilterTypeSchema)

    class Meta:
        model = Filter
        # Fields to expose
        fields = ('name', 'filter_type')


class FilterSchema2(ma.Schema):
    filter_type = ma.Nested(FilterTypeSchema)

    class Meta:
        model = Filter
        # Fields to expose
        fields = ('name', 'filter_type_id', 'id')


class FileSchema(ma.Schema):
    filters = ma.Nested(FilterSchema2, many=True)

    class Meta:
        model = File
        # Fields to expose

        fields = ('id', 'name', 'title', 'desc', 'filters')


file_schema = FileSchema()
files_schema = FileSchema(many=True)
filter_schema = FilterSchema2()
filters_schema = FilterSchema2(many=True)
filtertype_schema = FileSchema()
filtertypes_schema = FileSchema(many=True)


# First Run / Init
@app.before_first_request
def create_db():
    db.create_all()
    # Populate FilterGroup
    filter_group = FilterType.query.first()
    if filter_group is None:
        region = FilterType(tag="region", name="Region")
        vertical = FilterType(tag="vertical", name="Vertical")
        category = FilterType(tag="category", name="Category")
        db.session.add(region)
        db.session.add(vertical)
        db.session.add(category)
        db.session.commit()
    # Populate Filters
    filter = Filter.query.first()
    if filter is None:
        filter_type = FilterType.query.filter_by(tag='region').first()
        db.session.add(Filter(name="Americas", filter_type=filter_type, weight=0))
        db.session.add(Filter(name="APAC", filter_type=filter_type, weight=1))
        db.session.add(Filter(name="EMEA", filter_type=filter_type, weight=2))
        filter_type = FilterType.query.filter_by(tag='vertical').first()
        db.session.add(Filter(name="E-commerce", filter_type=filter_type, weight=0))
        db.session.add(Filter(name="Education", filter_type=filter_type, weight=1))
        db.session.add(Filter(name="Energy", filter_type=filter_type, weight=2))
        db.session.add(Filter(name="Financial Services", filter_type=filter_type, weight=3))
        db.session.add(Filter(name="Government", filter_type=filter_type, weight=4))
        db.session.add(Filter(name="Healthcare", filter_type=filter_type, weight=5))
        db.session.add(Filter(name="Insurance", filter_type=filter_type, weight=6))
        db.session.add(Filter(name="Manufacturing", filter_type=filter_type, weight=7))
        db.session.add(Filter(name="Media & Entertainment", filter_type=filter_type, weight=8))
        db.session.add(Filter(name="Reseller & Service Provider", filter_type=filter_type, weight=9))
        db.session.add(Filter(name="Retail", filter_type=filter_type, weight=10))
        db.session.add(Filter(name="Scientific Research", filter_type=filter_type, weight=11))
        db.session.add(Filter(name="Service Provider", filter_type=filter_type, weight=12))
        db.session.add(Filter(name="Technology", filter_type=filter_type, weight=13))
        db.session.add(Filter(name="Telecommunications", filter_type=filter_type, weight=14))
        db.session.add(Filter(name="Travel & Hospitality", filter_type=filter_type, weight=15))
        db.session.add(Filter(name="Web Services", filter_type=filter_type, weight=16))
        filter_type = FilterType.query.filter_by(tag='category').first()
        db.session.add(Filter(name="Identity and Policy Control", filter_type=filter_type, weight=0))
        db.session.add(Filter(name="Network Management", filter_type=filter_type, weight=1))
        db.session.add(Filter(name="Network Operating System", filter_type=filter_type, weight=2))
        db.session.add(Filter(name="Routers", filter_type=filter_type, weight=3))
        db.session.add(Filter(name="Security", filter_type=filter_type, weight=4))
        db.session.add(Filter(name="Services", filter_type=filter_type, weight=5))
        db.session.add(Filter(name="Software Defined Networking", filter_type=filter_type, weight=6))
        db.session.add(Filter(name="Switches", filter_type=filter_type, weight=7))
        db.session.add(Filter(name="Wireless", filter_type=filter_type, weight=8))
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
#   return redirect(url_for('admin_files'))


# FILE APIs
@app.route('/api/v1/files', methods=['GET'])
def api_v1_files():
    results = files_schema.dump(File.query.all())
    return jsonify({'results': results.data})


@app.route('/api/v1/file/<id>', methods=['GET'])
def api_v1_file(id):
    results = file_schema.dump(File.query.filter_by(id=id).first())
    return jsonify({'results': results.data})


# Zip APIs
@app.route('/zip')
def zip():
    file = File.query.filter_by(id=id).first()
    zf = zipfile.ZipFile(app.config['DOWNLOAD_FOLDER'] + "myzip.zip", "w", zipfile.ZIP_DEFLATED)
    absname = os.path.abspath(os.path.join(file.path, file.name))
    arcname = absname[len(abs_src) + 1:]
    print 'zipping %s as %s' % (os.path.join(dirname, filename), arcname)
    zf.write(absname, arcname)
    zf.close()

#    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
 #   abs_src = os.path.abspath(src)
  #  for dirname, subdirs, files in os.walk(src):
   #     for filename in files:
    #        absname = os.path.abspath(os.path.join(dirname, filename))
     #       arcname = absname[len(abs_src) + 1:]
      #      print 'zipping %s as %s' % (os.path.join(dirname, filename), arcname)
       #     zf.write(absname, arcname)
    #zf.close()


# Send APIs
@app.route('/download/<id>')
def send_file(id):
    file = File.query.filter_by(id=id).first()
    return send_from_directory(file.path, file.name)


# Tags APIs
@app.route('/api/v1/filters', methods=['GET'])
def filters_all():
    return redirect(url_for('filters', filter_type='all'))


@app.route('/api/v1/filters/<filter_type>', methods=['GET'])
def filters(filter_type):
    if filter_type == 'all':
        results = filters_schema.dump(Filter.query.order_by(Filter.filter_type_id, Filter.weight).all())
    else:
        filter_type = FilterType.query.filter_by(tag=filter_type).first()
        results = filters_schema.dump(Filter.query.filter_by(filter_type=filter_type).order_by(Filter.weight).all())
    return jsonify({'results': results.data})


# ADMIN Pages
@app.route('/admin')
@login_required
def admin():
    return redirect(url_for('admin_files'))


@app.route('/admin/files')
@roles_required('admin')
def admin_files():
    files = File.query.all()
    return render_template('admin_files.html', files=files)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/admin/files/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_files_add():
    if 'submit-add' in request.form:
        # Update Metadata
        file = File(title=request.form.get('title'), desc=request.form.get('desc'))
        db.session.add(file)
        db.session.commit()

        # Update Tags
        tags = request.form.getlist('tags')
        for tag_id in tags:
            exists = db.session.query(Filter.id).filter_by(id=tag_id).scalar()
            if exists:
                file.filters.append(Filter.query.filter_by(id=tag_id).first())
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

    filter_hash = {}
    filter_hash['region'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='region').first()).order_by(Filter.weight).all()
    filter_hash['vertical'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='vertical').first()).order_by(Filter.weight).all()
    filter_hash['category'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='category').first()).order_by(Filter.weight).all()
    return render_template('admin_files_add.html', filter_hash=filter_hash)


@app.route('/error/uploads/<errors>')
@login_required
def error_uploads(errors):
    return render_template('error_uploads.html', errors=errors)


@app.route('/admin/files/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
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
            new_filters = []
            for tag_id in tags:
                exists = db.session.query(Filter.id).filter_by(id=tag_id).scalar()
                if exists:
                    new_filters.append(Filter.query.filter_by(id=tag_id).first())
            file.filters[:] = new_filters
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

            return redirect(url_for('admin_files_edit', id=file.id))

    file = File.query.filter_by(id=id).first()
    filter_hash = {}
    filter_hash['region'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='region').first()).order_by(Filter.weight).all()
    filter_hash['vertical'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='vertical').first()).order_by(Filter.weight).all()
    filter_hash['category'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='category').first()).order_by(Filter.weight).all()
    return render_template('admin_files_edit.html', file=file, filter_hash=filter_hash)


@app.route('/admin/files/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_files_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(File.id).filter_by(id=id).scalar()
        if exists:
            file = File.query.filter_by(id=id).first()
            db.session.delete(file)
            db.session.commit()
            return redirect(url_for('admin_files'))
    file = File.query.filter_by(id=id).first()
    filter_hash = {}
    filter_hash['region'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='region').first()).order_by(Filter.weight).all()
    filter_hash['vertical'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='vertical').first()).order_by(Filter.weight).all()
    filter_hash['category'] = Filter.query.filter_by(filter_type=FilterType.query.filter_by(tag='category').first()).order_by(Filter.weight).all()
    return render_template('admin_files_delete.html', file=file, filter_hash=filter_hash)


@app.route('/admin/filters')
@roles_required('admin')
def admin_filters_all():
    return redirect(url_for('admin_filters', filter_type_tag='all'))


@app.route('/admin/filters/<filter_type_tag>')
@roles_required('admin')
def admin_filters(filter_type_tag):
    filter_types = FilterType.query.all()
    filter_type = None
    if filter_type_tag == 'all':
        filters = Filter.query.order_by(Filter.weight).all()
    else:
        filter_type = FilterType.query.filter_by(tag=filter_type_tag).first()
        filters = Filter.query.filter_by(filter_type_id=filter_type.id).order_by(Filter.weight).all()
    return render_template('admin_filters.html', filters=filters, filter_type=filter_type, filter_types=filter_types)


@app.route('/admin/filters/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_filters_add():
    if 'submit-add' in request.form:
        filter_type = FilterType.query.filter_by(id=request.form.get('filter_type_id')).first()
        db.session.add(Filter(name=request.form['name'], filter_type_id=filter_type.id, weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('admin_filters', filter_type_tag=filter_type.tag))
    filter_types = FilterType.query.all()
    return render_template('admin_filters_add.html', filter_types=filter_types)


@app.route('/admin/filters/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_filters_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(Filter.id).filter_by(id=id).scalar()
        if exists:
            filter_type = FilterType.query.filter_by(id=request.form.get('filter_type_id')).first()
            filter = Filter.query.filter_by(id=id).first()
            filter.name = request.form.get('name')
            filter.filter_type_id = filter_type.id
            filter.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('admin_filters', filter_type_tag=filter_type.tag))
    filter = Filter.query.filter_by(id=id).first()
    filter_types = FilterType.query.all()
    return render_template('admin_filters_edit.html', filter=filter, filter_types=filter_types)


@app.route('/admin/filters/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_filters_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(Filter.id).filter_by(id=id).scalar()
        if exists:
            print "request.form.get('filter_type_id')"
            print request.form.get('filter_type_id')
            filter_type = FilterType.query.filter_by(id=request.form.get('filter_type_id')).first()
            print filter_type.id
            filter = Filter.query.filter_by(id=id).first()
            db.session.delete(filter)
            db.session.commit()
            return redirect(url_for('admin_filters', filter_type_tag=filter_type.tag))
    filter = Filter.query.filter_by(id=id).first()
    filter_types = FilterType.query.all()
    return render_template('admin_filters_delete.html', filter=filter, filter_types=filter_types)


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
