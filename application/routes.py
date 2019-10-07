"""Routes for logged-in application."""
from flask import Blueprint, render_template, session, send_from_directory
from flask_login import current_user
from flask import current_app as app
#from .assets import compile_auth_assets
#from flask_login import login_required

# Blueprint Configuration
main_bp = Blueprint('main_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)


# Public Frontend
@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/download/package/<uuid>')
def download_package(uuid):
    package = Package.query.filter_by(uuid=uuid).first()
    # check for package first...
    if not os.path.isfile(package.path + package.name):
        # File does not exist...  Create Package
        package_files(package.uuid)
    package.downloads += 1
    db.session.commit()
    return send_from_directory(package.path, package.name)
