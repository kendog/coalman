"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required, current_user
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import Account, User
from .. import user_datastore


# Blueprint Configuration
accounts_bp = Blueprint('accounts_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@accounts_bp.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    if current_user.has_role('super-admin'):
        if 'submit-edit' in request.form:
            account = Account.query.filter_by(id=current_user.account_id).first()
            if account.name != "ROOT":
                account.name = request.form['name']
                db.session.commit()
        return render_template('/accounts/form.html')
        #return redirect(url_for('manage_accounts_bp.accounts'))
    elif current_user.has_role('admin'):
        if 'submit-edit' in request.form:
            account = Account.query.filter_by(id=current_user.account_id).first()
            if account.name != "ROOT":
                account.name = request.form['name']
                db.session.commit()
        return render_template('/accounts/form.html')
    else:
        account = Account.query.filter_by(id=current_user.account_id).first()
        return render_template('/accounts/form.html')
        #return redirect(url_for('pages_bp.index'))


@accounts_bp.route('/account/<id>', methods=['POST', 'GET'])
@login_required
def switch_account(id):
    for account in current_user.accounts:
        if account.id == int(id):
            user = User.query.filter_by(email=current_user.email).first()
            user.account_id = int(id)
            db.session.commit()
    return redirect(url_for('accounts_bp.account'))
