"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_security import roles_required, Security, SQLAlchemyUserDatastore, utils
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, User, Role


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Blueprint Configuration
users_bp = Blueprint('users_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@app.before_first_request
def before_first_request():
    if not user_datastore.get_user(app.config['SITE_ADMIN_EMAIL']):
        encrypted_password = utils.hash_password(app.config['SITE_ADMIN_PASSWORD'])
        user_datastore.create_user(email=app.config['SITE_ADMIN_EMAIL'],password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user(app.config['SITE_ADMIN_EMAIL'], 'admin')
        db.session.commit()


@users_bp.route('/admin/users')
@roles_required('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@users_bp.route('/admin/users/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_users_add():
    if 'submit-add' in request.form:
        encrypted_password = utils.hash_password(request.form['password'])
        user_datastore.create_user(email=request.form['username'], password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user(request.form['username'], request.form['role'])
        db.session.commit()
        return redirect(url_for('users_bp.admin_users'))
    roles = Role.query.all()
    return render_template('admin_users_add.html', roles=roles)


@users_bp.route('/admin/users/edit/<id>', methods=['POST', 'GET'])
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
        return redirect(url_for('users_bp.admin_users'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    return render_template('admin_users_edit.html', user=user, roles=roles)


@users_bp.route('/admin/users/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_users_delete(id):
    if 'submit-delete' in request.form:
        exists = user_datastore.get_user(id)
        if exists:
            user = user_datastore.get_user(id)
            db.session.delete(user)
            db.session.commit()
        return redirect(url_for('users_bp.admin_users'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    return render_template('admin_users_delete.html', user=user, roles=roles)
