"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, Account


# Blueprint Configuration
accounts_bp = Blueprint('accounts_bp', __name__,
                    template_folder='templates',
                    static_folder='static')



@accounts_bp.route('/accounts')
@roles_required('super-admin')
def accounts():
    accounts = Account.query.all()
    return render_template('accounts/list.html', accounts=accounts)



@accounts_bp.route('/accounts/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def accounts_add():
    if 'submit-add' in request.form:
        account = Account(name=request.form['name'])
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('accounts_bp.accounts'))
    return render_template('accounts/form.html', template_mode='add')


@accounts_bp.route('/accounts/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def accounts_edit(id):
    account = Account.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if account:
            account.name = request.form['name']
            db.session.commit()
        return redirect(url_for('accounts_bp.accounts'))
    return render_template('accounts/form.html', template_mode='edit', account=account)


@accounts_bp.route('/accounts/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def accounts_delete(id):
    account = Account.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if account:
            db.session.delete(account)
            db.session.commit()
        return redirect(url_for('accounts_bp.accounts'))
    return render_template('accounts/form.html', template_mode='delete', account=account)



"""
@accounts_bp.route('/account')
@roles_required('super-admin')
def account():
    if current_user.account_id:
        account = Account.query.filter_by(id=current_user.account_id).first()
    else:
        account = Account()
        db.session.add(account)
        db.session.commit()
        current_user.account_id = account.id
        db.session.commit()
    return redirect(url_for('accounts_bp.account_edit',id=current_user.account_id))


@accounts_bp.route('/account/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def account_edit(id):
    account = False
    if current_user.has_role('super-admin'):
        account = Account.query.filter_by(id=id).first()
    else:
        account = Account.query.filter_by(id=current_user.account_id).first()

    if 'submit-edit' in request.form:
        if account:
            account.name = request.form.get('name')
            db.session.commit()
        if current_user.has_role('super-admin'):
            return redirect(url_for('accounts_bp.accounts_list'))
        return redirect(url_for('accounts_bp.account'))
    return render_template('accounts/account.html', account=account)
"""
