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

@users_bp.route('/users')
#@roles_required('admin')
def users():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@users_bp.route('/users/add', methods=['POST', 'GET'])
#@roles_required('admin')
def users_add():
    if 'submit-add' in request.form:
        encrypted_password = utils.hash_password(request.form['password'])
        user_datastore.create_user(email=request.form['username'], password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user(request.form['username'], request.form['role'])
        db.session.commit()
        return redirect(url_for('users_bp.users'))
    roles = Role.query.all()
    return render_template('users/form.html', template_mode='add', roles=roles)


@users_bp.route('/users/edit/<id>', methods=['POST', 'GET'])
#@roles_required('admin')
def users_edit(id):
    if 'submit-edit' in request.form:
        exists = user_datastore.get_user(id)
        if exists:
            user = user_datastore.get_user(id)
            user.email = request.form['username']
            user.password = utils.hash_password(request.form['password'])
            user_datastore.remove_role_from_user(user.email, 'admin')
            user_datastore.remove_role_from_user(user.email, 'end-user')
            user_datastore.add_role_to_user(user.email, request.form['role'])
            db.session.commit()
        return redirect(url_for('users_bp.users'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    return render_template('users/form.html', template_mode='edit', user=user, roles=roles)


@users_bp.route('/users/delete/<id>', methods=['POST', 'GET'])
#@roles_required('admin')
def users_delete(id):
    if 'submit-delete' in request.form:
        exists = user_datastore.get_user(id)
        if exists:
            user = user_datastore.get_user(id)
            db.session.delete(user)
            db.session.commit()
        return redirect(url_for('users_bp.users'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    return render_template('users/form.html', template_mode='delete', user=user, roles=roles)
