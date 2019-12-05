"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import accounts_bp
from .manage import manage_accounts_bp
from ..models import Project, Account
from sqlalchemy import or_, and_

app.register_blueprint(accounts_bp)
app.register_blueprint(manage_accounts_bp)


#@app.context_processor
#def inject_account():
#    account = []
#    if current_user.account:
#        account = current_user.account
#    else:
#        current_user.account_id = current_user.accounts[0].id
#        account = current_user.account
#    return dict(current_account=account)


@app.context_processor
def inject_accounts():
    accounts = []
    if current_user.has_role('super-admin'):
        accounts = Account.query.all()
    elif current_user.is_authenticated:
        accounts = current_user.accounts

    return dict(current_accounts=accounts)
