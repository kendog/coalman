"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, Package



# Blueprint Configuration
packages_bp = Blueprint('packages_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)


@packages_bp.route('/packages/<uuid>')
def download_package(uuid):
    package = Package.query.filter_by(uuid=uuid).first()
    # check for package first...
    if not os.path.isfile(package.path + package.name):
        # File does not exist...  Create Package
        package_files(package.uuid)
    package.downloads += 1
    db.session.commit()
    return send_from_directory(package.path, package.name)


@packages_bp.route('/packages')
@login_required
def packages():
    packages = Package.query.all()
    return render_template('admin_packages.html', packages=packages)


@packages_bp.route('/packages/add', methods=['POST', 'GET'])
@login_required
def packages_add():
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

        return redirect(url_for('packages_bp.admin_packages'))
    files = File.query.all()
    return render_template('admin_packages_add.html', files=files)


@packages_bp.route('/packages/delete/<id>', methods=['POST', 'GET'])
@login_required
def packages_delete(id):
    package = Package.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if package:
            db.session.delete(package)
            db.session.commit()
            return redirect(url_for('packages_bp.admin_packages'))
    return render_template('admin_packages_delete.html', package=package)


@packages_bp.route('/admin/packages')
@roles_required('admin')
def admin_packages():
    packages = Package.query.all()
    return render_template('admin_packages.html', packages=packages)


@packages_bp.route('/admin/packages/add', methods=['POST', 'GET'])
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

        return redirect(url_for('packages_bp.admin_packages'))
    files = File.query.all()
    return render_template('admin_packages_add.html', files=files)


@packages_bp.route('/admin/packages/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_packages_delete(id):
    package = Package.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if package:
            db.session.delete(package)
            db.session.commit()
            return redirect(url_for('packages_bp.admin_packages'))
    return render_template('admin_packages_delete.html', package=package)
