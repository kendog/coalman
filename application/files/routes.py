"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, File, Tag, TagGroup


# Blueprint Configuration
files_bp = Blueprint('files_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@files_bp.route('/download/file/<id>')
@login_required
def download_file(id):
    file = File.query.filter_by(id=id).first()
    return send_from_directory(file.path, file.name)


@files_bp.route('/error/uploads/<errors>')
@login_required
def error_uploads(errors):
    return render_template('error_uploads.html', errors=errors)



# User Pages
@files_bp.route('/files')
@login_required
def admin_files():
    files = File.query.all()
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_files.html', files=files, tag_groups=tag_groups)


@files_bp.route('/files/add', methods=['POST', 'GET'])
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
                directory = app.config['UPLOAD_FOLDER'] + str(file.id) + '/'
                try:
                    os.stat(directory)
                except:
                    os.mkdir(directory)
                # upload the file
                the_actual_file.save(os.path.join(directory, secure_filename(the_actual_file.filename)))
                # update the db
                file.name = secure_filename(the_actual_file.filename)
                file.path = directory
                db.session.commit()

        return redirect(url_for('files_bp.admin_files'))

    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_add.html', tag_groups=tag_groups, tag_hash=tag_hash)


@files_bp.route('/files/edit/<id>', methods=['POST', 'GET'])
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
                    directory = app.config['UPLOAD_FOLDER'] + str(file.id) + '/'
                    try:
                        os.stat(directory)
                    except:
                        os.mkdir(directory)
                    # upload the file
                    the_actual_file.save(os.path.join(directory, secure_filename(the_actual_file.filename)))
                    # update the db
                    file.name = secure_filename(the_actual_file.filename)
                    file.path = directory
                    db.session.commit()

            return redirect(url_for('files_bp.admin_files'))

    file = File.query.filter_by(id=id).first()
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_edit.html', file=file, tag_groups=tag_groups, tag_hash=tag_hash)


@files_bp.route('/files/delete/<id>', methods=['POST', 'GET'])
@login_required
def admin_files_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(File.id).filter_by(id=id).scalar()
        if exists:
            file = File.query.filter_by(id=id).first()
            db.session.delete(file)
            db.session.commit()
            return redirect(url_for('files_bp.admin_files'))
    file = File.query.filter_by(id=id).first()
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_delete.html', file=file, tag_groups=tag_groups, tag_hash=tag_hash)
