"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import users_bp
from .manage import manage_users_bp
from ..models import Role, User, Account
from sqlalchemy import or_, and_

app.register_blueprint(users_bp)
app.register_blueprint(manage_users_bp)

@app.context_processor
def inject_roles():
    roles = []
    if current_user.has_role('super-admin'):
        roles = Role.query.all()
    elif current_user.is_authenticated:
        roles = Role.query.filter(Role.name != "super-admin").all()
    return dict(current_roles=roles)

@app.context_processor
def inject_users():
    users = []
    if current_user.has_role('super-admin'):
        users = User.query.all()
    elif current_user.is_authenticated:
        users = User.query\
            .join(Account)\
            .filter(and_(Account.id == User.account_id, Account.id == current_user.account_id))\
            .all()
    return dict(current_users=users)
