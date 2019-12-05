"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_security import roles_required, roles_accepted, Security, SQLAlchemyUserDatastore, utils
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import User, Role, Account, Project
from flask_login import login_required, current_user
from .. import user_datastore
from sqlalchemy import or_, and_

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)

#user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)


# Blueprint Configuration
users_bp = Blueprint('users_bp', __name__,
                    template_folder='templates',
                    static_folder='static')



@users_bp.route('/users')
@roles_accepted('admin','super-admin')
def users():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_users_bp.users'))

    users = User.query.filter_by(account_id=current_user.account_id).all()
    return render_template('/users/list.html', users=users)


@users_bp.route('/users/add', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def users_add():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_users_bp.users_add'))

    if 'submit-add' in request.form:
        encrypted_password = utils.hash_password(request.form['password'])
        is_active = request.form.get('active') == "on"

        user_datastore.create_user(email=request.form['email'], password=encrypted_password, active=is_active)
        db.session.commit()
        role = request.form.get('role')
        user_datastore.add_role_to_user(request.form['email'], role)
        db.session.commit()

        user = user_datastore.get_user(request.form['email'])
        user.account_id = request.form['account_id']
        user.active = request.form.get('active') == "on"
        db.session.commit()

        #user.accounts[:] = []
        account_ids = request.form.getlist("account_ids")
        for account_id in account_ids:
            exists = db.session.query(Account.id).filter_by(id=account_id).scalar()
            if exists:
                user.accounts.append(Account.query.filter_by(id=account_id).first())
                db.session.commit()
        return redirect(url_for('users_bp.users'))

    return render_template('/users/form.html', template_mode='add')


@users_bp.route('/users/edit/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def users_edit(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_users_bp.users_edit',id=id))

    user = user_datastore.get_user(id)
    if user.account_id != current_user.account_id:
        return redirect(url_for('users_bp.users'))

    if 'submit-edit' in request.form:
        if user:
            user.account_id = request.form['account_id']
            user.active = request.form.get('active') == "on"
            db.session.commit()

            roles = Role.query.all()
            for role in roles:
                user_datastore.remove_role_from_user(user.email, role)
            role = request.form.get('role')
            user_datastore.add_role_to_user(user.email, role)
            db.session.commit()

            user.accounts[:] = []
            account_ids = request.form.getlist("account_ids")
            for account_id in account_ids:
                exists = db.session.query(Account.id).filter_by(id=account_id).scalar()
                if exists:
                    user.accounts.append(Account.query.filter_by(id=account_id).first())
                    db.session.commit()
            return redirect(url_for('users_bp.users'))

    return render_template('/users/form.html', template_mode='edit', user=user)


@users_bp.route('/users/delete/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def users_delete(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_users_bp.users_delete',id=id))

    user = user_datastore.get_user(id)
    if user.account_id != current_user.account_id:
        return redirect(url_for('users_bp.users'))

    if 'submit-delete' in request.form:
        if user:
            user = user_datastore.get_user(id)
            db.session.delete(user)
            db.session.commit()
        return redirect(url_for('users_bp.users'))
    roles = Role.query.all()
    return render_template('/users/form.html', template_mode='delete', user=user)
