"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import Account


# Blueprint Configuration
manage_accounts_bp = Blueprint('manage_accounts_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/manage')


@manage_accounts_bp.route('/accounts')
@roles_required('super-admin')
def accounts():
    accounts = Account.query.filter(Account.name != "ROOT").all()
    return render_template('/accounts/manage/list.html', accounts=accounts)


@manage_accounts_bp.route('/accounts/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def accounts_add():
    if 'submit-add' in request.form:
        account = Account(name=request.form['name'])
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('manage_accounts_bp.accounts'))
    return render_template('/accounts/manage/form.html', template_mode='add')


@manage_accounts_bp.route('/accounts/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def accounts_edit(id):
    account = Account.query.filter_by(id=id).first()
    if account.name == "ROOT":
        return redirect(url_for('manage_accounts_bp.accounts'))
    if 'submit-edit' in request.form:
        if account:
            account.name = request.form['name']
            db.session.commit()
        return redirect(url_for('manage_accounts_bp.accounts'))
    return render_template('/accounts/manage/form.html', template_mode='edit', account=account)


@manage_accounts_bp.route('/accounts/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def accounts_delete(id):
    account = Account.query.filter_by(id=id).first()
    if account.name == "ROOT":
        return redirect(url_for('manage_accounts_bp.accounts'))
    if 'submit-delete' in request.form:
        if account:
            db.session.delete(account)
            db.session.commit()
        return redirect(url_for('manage_accounts_bp.accounts'))
    return render_template('/accounts/manage/form.html', template_mode='delete', account=account)
