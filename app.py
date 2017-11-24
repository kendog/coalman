import os
from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user, login_required, roles_required, utils
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename

# Create app
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
ma = Marshmallow(app)

ALLOWED_EXTENSIONS = set(['pdf', 'PDF', 'png', 'PNG'])

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


class FilterType(db.Model):
    __tablename__ = 'FilterTypes'
    id = db.Column(db.String(225), primary_key=True)
    name = db.Column(db.String(255))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Define Schemas
class FilterSchema(ma.Schema):
    class Meta:
        model = Filter
        # Fields to expose
        fields = ('name', 'filter_type')


class FileSchema(ma.Schema):

    filters = ma.Nested(FilterSchema, many=True)

    class Meta:
        model = File
        # Fields to expose

        fields = ('id', 'name', 'title', 'desc', 'filters')


file_schema = FileSchema()
files_schema = FileSchema(many=True)
filter_schema = FilterSchema()
filters_schema = FilterSchema(many=True)


# First Run / Init
@app.before_first_request
def create_db():
    db.create_all()
    # Populate Files
    file = File.query.first()
    if file is None:
        db.session.add(File(name="file1.pdf", path="/files/", title="File 1 (PDF)", desc="File 1 is a PDF."))
        db.session.add(File(name="file2.pdf", path="/files/", title="File 2 (PDF)", desc="File 2 is a PDF."))
        db.session.add(File(name="file3.pdf", path="/files/", title="File 3 (PDF)", desc="File 3 is a PDF."))
        db.session.add(File(name="file4.pdf", path="/files/", title="File 4 (PDF)", desc="File 4 is a PDF."))
        db.session.add(File(name="file5.pdf", path="/files/", title="File 5 (PDF)", desc="File 5 is a PDF."))
        db.session.add(File(name="file6.pdf", path="/files/", title="File 6 (PDF)", desc="File 6 is a PDF."))
        db.session.add(File(name="file7.pdf", path="/files/", title="File 7 (PDF)", desc="File 7 is a PDF."))
        db.session.add(File(name="file8.pdf", path="/files/", title="File 8 (PDF)", desc="File 8 is a PDF."))
        db.session.add(File(name="file9.pdf", path="/files/", title="File 9 (PDF)", desc="File 9 is a PDF."))
        db.session.commit()
    # Populate FilterGroup
    filter_group = FilterType.query.first()
    if filter_group is None:
        db.session.add(FilterType(id="region", name="Region"))
        db.session.add(FilterType(id="vertical", name="Vertical"))
        db.session.add(FilterType(id="category", name="Category"))
        db.session.commit()
    # Populate Filters
    filter = Filter.query.first()
    if filter is None:
        db.session.add(Filter(name="Americas", filter_type="region", weight=0))
        db.session.add(Filter(name="APAC", filter_type="region", weight=1))
        db.session.add(Filter(name="EMEA", filter_type="region", weight=2))
        db.session.add(Filter(name="E-commerce", filter_type="vertical", weight=0))
        db.session.add(Filter(name="Education", filter_type="vertical", weight=1))
        db.session.add(Filter(name="Energy", filter_type="vertical", weight=2))
        db.session.add(Filter(name="Financial Services", filter_type="vertical", weight=3))
        db.session.add(Filter(name="Government", filter_type="vertical", weight=4))
        db.session.add(Filter(name="Healthcare", filter_type="vertical", weight=5))
        db.session.add(Filter(name="Insurance", filter_type="vertical", weight=6))
        db.session.add(Filter(name="Manufacturing", filter_type="vertical", weight=7))
        db.session.add(Filter(name="Media &amp; Entertainment", filter_type="vertical", weight=8))
        db.session.add(Filter(name="Reseller &amp; Service Provider", filter_type="vertical", weight=9))
        db.session.add(Filter(name="Retail", filter_type="vertical", weight=10))
        db.session.add(Filter(name="Scientific Research", filter_type="vertical", weight=11))
        db.session.add(Filter(name="Service Provider", filter_type="vertical", weight=12))
        db.session.add(Filter(name="Technology", filter_type="vertical", weight=13))
        db.session.add(Filter(name="Telecommunications", filter_type="vertical", weight=14))
        db.session.add(Filter(name="Travel &amp; Hospitality", filter_type="vertical", weight=15))
        db.session.add(Filter(name="Web Services", filter_type="vertical", weight=16))
        db.session.add(Filter(name="Identity and Policy Control", filter_type="category", weight=0))
        db.session.add(Filter(name="Network Management", filter_type="category", weight=1))
        db.session.add(Filter(name="Network Operating System", filter_type="category", weight=2))
        db.session.add(Filter(name="Routers", filter_type="category", weight=3))
        db.session.add(Filter(name="Security", filter_type="category", weight=4))
        db.session.add(Filter(name="Services", filter_type="category", weight=5))
        db.session.add(Filter(name="Software Defined Networking", filter_type="category", weight=6))
        db.session.add(Filter(name="Switches", filter_type="category", weight=7))
        db.session.add(Filter(name="Wireless", filter_type="category", weight=8))
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
def files():
    results = files_schema.dump(File.query.all())
    return jsonify({'results': results.data})


# Tags APIs
@app.route('/api/v1/filters', methods=['GET'])
def filters():
    # filter_hash = {}
    # filter_hash['regions'] = filters_schema.dump(Filter.query.filter_by(filter_type='region').order_by(Filter.weight).all()).data
    # filter_hash['verticals'] = filters_schema.dump(Filter.query.filter_by(filter_type='vertical').order_by(Filter.weight).all()).data
    # filter_hash['categories'] = filters_schema.dump(Filter.query.filter_by(filter_type='category').order_by(Filter.weight).all()).data
    # return jsonify({'results': filter_hash})
    results = filters_schema.dump(Filter.query.order_by(Filter.filter_type, Filter.weight).all())
    return jsonify({'results': results.data})


@app.route('/api/v1/filters/<filter_type>', methods=['GET'])
def regions(filter_type):
    results = filters_schema.dump(Filter.query.filter_by(filter_type=filter_type).order_by(Filter.weight).all())
    return jsonify({'results': results.data})


# ADMIN Pages
@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/admin/files')
@roles_required('admin')
def admin_files():
    files = File.query.all()
    return render_template('admin_files.html', files=files)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/files/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_files_add():
    if 'submit-add' in request.form:
        # Update Metadata
        file = File(title=request.form.get('title'), desc=request.form.get('desc'))
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

        return redirect(url_for('admin_files_edit', id=file.id))

    filter_hash = {}
    filter_hash['region'] = Filter.query.filter_by(filter_type='region').order_by(Filter.weight).all()
    filter_hash['vertical'] = Filter.query.filter_by(filter_type='vertical').order_by(Filter.weight).all()
    filter_hash['category'] = Filter.query.filter_by(filter_type='category').order_by(Filter.weight).all()
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
    filter_hash['region'] = Filter.query.filter_by(filter_type='region').order_by(Filter.weight).all()
    filter_hash['vertical'] = Filter.query.filter_by(filter_type='vertical').order_by(Filter.weight).all()
    filter_hash['category'] = Filter.query.filter_by(filter_type='category').order_by(Filter.weight).all()
    return render_template('admin_files_edit.html', file=file, filter_hash=filter_hash)


@app.route('/admin/files/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_files_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(Filter.id).filter_by(id=id).scalar()
        if exists:
            file = File.query.filter_by(id=id).first()
            db.session.delete(file)
            db.session.commit()
            return redirect(url_for('admin_files'))
    file = File.query.filter_by(id=id).first()
    filter_hash = {}
    filter_hash['region'] = Filter.query.filter_by(filter_type='region').order_by(Filter.weight).all()
    filter_hash['vertical'] = Filter.query.filter_by(filter_type='vertical').order_by(Filter.weight).all()
    filter_hash['category'] = Filter.query.filter_by(filter_type='category').order_by(Filter.weight).all()
    return render_template('admin_files_delete.html', file=file, filter_hash=filter_hash)


@app.route('/admin/filters')
@roles_required('admin')
def admin_filters_all():
    filters = Filter.query.order_by(Filter.weight).all()
    return render_template('admin_filters.html', filter_type='all', filters=filters)


@app.route('/admin/filters/<filter_type>')
@roles_required('admin')
def admin_filters(filter_type):
    filters = Filter.query.filter_by(filter_type=filter_type).order_by(Filter.weight).all()
    return render_template('admin_filters.html', filter_type=filter_type, filters=filters)


@app.route('/admin/filters/add/<filter_type>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_filters_add(filter_type):
    if 'submit-add' in request.form:
        filter_type = request.form['filter_type']
        db.session.add(Filter(name=request.form['name'], filter_type=filter_type, weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('admin_filters', filter_type=filter_type))
    filter_types = FilterType.query.all()
    return render_template('admin_filters_add.html', filter_type=filter_type, filter_types=filter_types)


@app.route('/admin/filters/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_filters_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(Filter.id).filter_by(id=id).scalar()
        if exists:
            filter = Filter.query.filter_by(id=id).first()
            filter.name = request.form.get('name')
            filter.filter_type = request.form.get('filter_type')
            filter.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('admin_filters', filter_type=filter.filter_type))
    filter = Filter.query.filter_by(id=id).first()
    filter_types = FilterType.query.all()
    return render_template('admin_filters_edit.html', filter=filter, filter_types=filter_types)


@app.route('/admin/filters/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_filters_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(Filter.id).filter_by(id=id).scalar()
        if exists:
            filter = Filter.query.filter_by(id=id).first()
            filter_type = filter.filter_type
            db.session.delete(filter)
            db.session.commit()
            return redirect(url_for('admin_filters', filter_type=filter_type))
    filter = Filter.query.filter_by(id=id).first()
    filter_types = FilterType.query.all()
    return render_template('admin_filters_delete.html', filter=filter, filter_types=filter_types)


if __name__ == "__main__":
    app.run('localhost')
