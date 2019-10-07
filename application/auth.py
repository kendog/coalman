"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required, logout_user, current_user, login_user
from flask import current_app as app
from werkzeug.security import generate_password_hash
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from .models import db, User
from .import login_manager



# Blueprint Configuration
auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)



@main_bp.route('/download/file/<id>')
@login_required
def download_file(id):
    file = File.query.filter_by(id=id).first()
    return send_from_directory(file.path, file.name)


@main_bp.route('/error/uploads/<errors>')
@login_required
def error_uploads(errors):
    return render_template('error_uploads.html', errors=errors)



# ADMIN Pages
@auth_bp.route('/admin')
@login_required
def admin():
    return redirect(url_for('admin_files'))


@auth_bp.route('/admin/files')
@login_required
def admin_files():
    files = File.query.all()
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_files.html', files=files, tag_groups=tag_groups)


@auth_bp.route('/admin/files/add', methods=['POST', 'GET'])
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

        return redirect(url_for('admin_files'))

    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_add.html', tag_groups=tag_groups, tag_hash=tag_hash)


@auth_bp.route('/admin/files/edit/<id>', methods=['POST', 'GET'])
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

            return redirect(url_for('admin_files'))

    file = File.query.filter_by(id=id).first()
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.tag_id] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(tag_id=groups.tag_id).first()).order_by(Tag.weight).all()
    return render_template('admin_files_edit.html', file=file, tag_groups=tag_groups, tag_hash=tag_hash)


@auth_bp.route('/admin/files/delete/<id>', methods=['POST', 'GET'])
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


@auth_bp.route('/admin/apis')
@roles_required('admin')
def admin_apis():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_apis.html', tag_groups=tag_groups)


@auth_bp.route('/admin/tags')
@roles_required('admin')
def admin_tags_all():
    return redirect(url_for('admin_tags', tag_group_tag='all'))


@auth_bp.route('/admin/tags/<tag_group_tag>')
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


@auth_bp.route('/admin/tags/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tags_add():
    if 'submit-add' in request.form:
        tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
        db.session.add(Tag(name=request.form['name'], tag_id=request.form['tag_id'], tag_group=tag_group, weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('admin_tags', tag_group_tag=tag_group.tag_id))
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_add.html', tag_groups=tag_groups)


@auth_bp.route('/admin/tags/edit/<id>', methods=['POST', 'GET'])
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


@auth_bp.route('/admin/tags/delete/<id>', methods=['POST', 'GET'])
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


@auth_bp.route('/admin/tag_groups')
@roles_required('admin')
def admin_tag_groups():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_tag_groups.html', tag_groups=tag_groups)


@auth_bp.route('/admin/tag_groups/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tag_groups_add():
    if 'submit-add' in request.form:
        db.session.add(TagGroup(name=request.form['name'], tag_id=request.form['tag_id'], weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('admin_tag_groups'))
    return render_template('admin_tag_groups_add.html')


@auth_bp.route('/admin/tag_groups/edit/<id>', methods=['POST', 'GET'])
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


@auth_bp.route('/admin/tag_groups/delete/<id>', methods=['POST', 'GET'])
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


@auth_bp.route('/admin/packages')
@roles_required('admin')
def admin_packages():
    packages = Package.query.all()
    return render_template('admin_packages.html', packages=packages)


@auth_bp.route('/admin/packages/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_packages_add():
    if 'submit-add' in request.form:
        # Update Metadata
        user_name = request.form.get('user_name')
        user_email = request.form.get("user_email")
        file_ids = request.form.getlist("files")

        package = Package(uuid=str(uuid.uuid4()), user_name=user_name, user_email=user_email)
        db.session.add(package)
        db.session.commit()

        package.package_status_id = 1
        package.notification_status_id = 1
        package.name = package.uuid + ".zip"
        package.path = app.config['TEMP_FOLDER']
        package.link = app.config['DOWNLOAD_PROTOCOL'] + '://' + app.config['DOWNLOAD_DOMAIN'] + url_for(
            'download_package', uuid=package.uuid)
        db.session.commit()

        # Add Files
        for item in file_ids:
            #print item
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                package.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if request.form.get("notify"):
            send_notification(package.uuid)

        return redirect(url_for('admin_packages'))
    files = File.query.all()
    return render_template('admin_packages_add.html', files=files)


@auth_bp.route('/admin/packages/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_packages_delete(id):
    package = Package.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if package:
            db.session.delete(package)
            db.session.commit()
            return redirect(url_for('admin_packages'))
    return render_template('admin_packages_delete.html', package=package)


@auth_bp.route('/admin/message/edit', methods=['POST', 'GET'])
@roles_required('admin')
def admin_message_edit():
    message = Message.query.first()
    if 'submit-edit' in request.form and message:
        message.subject = request.form.get('subject')
        message.message = request.form.get('message')
        db.session.commit()
        return redirect(url_for('admin_message_edit', message=message))
    return render_template('admin_message_edit.html', message=message)


@auth_bp.route('/admin/users')
@roles_required('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@auth_bp.route('/admin/users/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_users_add():
    if 'submit-add' in request.form:
        encrypted_password = utils.hash_password(request.form['password'])
        user_datastore.create_user(username=request.form['username'], password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user(request.form['username'], request.form['role'])
        db.session.commit()
        return redirect(url_for('admin_users'))
    roles = Role.query.all()
    return render_template('admin_users_add.html', roles=roles)


@auth_bp.route('/admin/users/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_users_edit(id):
    if 'submit-edit' in request.form:
        exists = user_datastore.get_user(id)
        if exists:
            user = user_datastore.get_user(id)
            user_datastore.remove_role_from_user(user.username, 'admin')
            user_datastore.remove_role_from_user(user.username, 'end-user')
            user_datastore.add_role_to_user(user.username, request.form['role'])
            user.email = request.form['email']
            user.phone = request.form['phone']
            db.session.commit()
        return redirect(url_for('admin_users'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    return render_template('admin_users_edit.html', user=user, roles=roles)


@auth_bp.route('/admin/users/delete/<id>', methods=['POST', 'GET'])
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


@auth_bp.route('/admin/profiles')
@roles_required('admin')
def admin_profiles():
    profiles = Profile.query.all()
    return render_template('admin_profiles.html', profiles=profiles)


@auth_bp.route('/admin/profiles/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_profiles_add():
    if 'submit-add' in request.form:
        user_id = request.form['user_id']
        user = User.query.filter_by(id=user_id).first()
        profile = Profile(
            username=request.form['username'],
            bio=request.form['bio'],
            name=request.form['name'],
            address1=request.form['address1'],
            address2=request.form['address2'],
            city=request.form['city'],
            state=request.form['state'],
            zip=request.form['zip'],
            phone=request.form['phone'],
            user_id=user_id)
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for('admin_profiles'))
    users = User.query.all()
    return render_template('admin_profiles_add.html', users=users)


@auth_bp.route('/admin/profiles/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_profiles_edit(id):
    profile = Profile.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        user_id = request.form['user_id']
        user = User.query.filter_by(id=user_id).first()
        if profile:
            profile.username = request.form.get('username')
            profile.bio = request.form.get('bio')
            profile.name = request.form.get('name')
            profile.address1 = request.form.get('address1')
            profile.address2 = request.form.get('address2')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.zip = request.form.get('zip')
            profile.phone = request.form.get('phone')
            profile.user_id = user_id
            db.session.commit()
        return redirect(url_for('admin_profiles'))
    users = User.query.all()
    return render_template('admin_profiles_edit.html', profile=profile, users=users)


@auth_bp.route('/admin/profiles/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_profiles_delete(id):
    profile = Profile.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if profile:
            db.session.delete(profile)
            db.session.commit()
        return redirect(url_for('admin_profiles'))
    users = User.query.all()
    return render_template('admin_profiles_delete.html', profile=profile, users=users)




@auth_bp.route('/profile')
@login_required
def profile():
    user_id = current_user.get_id()
    user = User.query.filter_by(id=user_id).first()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        return render_template('profile.html', user=user, profile=profile)
    else:
        return render_template('profile.html', user=user)


@auth_bp.route('/profile/<id>')
@login_required
def get_profile(id):
    profile = Profile.query.filter_by(id=id).first()
    return render_template('profile.html', profile=profile)


@auth_bp.route('/profile/add', methods=['POST', 'GET'])
@login_required
def profile_add():
    if 'submit-add' in request.form:
        user_id = current_user.get_id()
        profile = Profile(
            username=request.form['username'],
            bio=request.form['bio'],
            name=request.form['name'],
            address1=request.form['address1'],
            address2=request.form['address2'],
            city=request.form['city'],
            state=request.form['state'],
            zip=request.form['zip'],
            phone=request.form['phone'],
            user_id=user_id)
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for('profile'))
    users = User.query.all()
    return render_template('profile_add.html')


@auth_bp.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def profile_edit():
    user_id = current_user.get_id()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if 'submit-edit' in request.form:
        if profile:
            profile.username = request.form.get('username')
            profile.bio = request.form.get('bio')
            profile.name = request.form.get('name')
            profile.address1 = request.form.get('address1')
            profile.address2 = request.form.get('address2')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.zip = request.form.get('zip')
            profile.phone = request.form.get('phone')
            db.session.commit()
        return redirect(url_for('profile'))
    users = User.query.all()
    return render_template('profile_edit.html', profile=profile)


@auth_bp.route('/profile/delete', methods=['POST', 'GET'])
@login_required
def profile_delete():
    user_id = current_user.get_id()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if 'submit-delete' in request.form:
        if profile:
            db.session.delete(profile)
            db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile_delete.html', profile=profile)
