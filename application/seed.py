from flask import current_app as app
from .db import db
from .models import User, Role, Account, Project, File, Status, MessageTemplate, TagGroup, Tag
from . import user_datastore
from flask_security import utils
import uuid

@app.before_first_request
def before_first_request():
    roles = Role.query.first()
    if roles is None:
        db.session.add(Role(name="super-admin", description="Super Admin"))
        db.session.add(Role(name="admin", description="Admin"))
        db.session.add(Role(name="end-user", description="End User"))
        db.session.add(Role(name="contractor", description="Contractor"))
        db.session.commit()
    user = User.query.first()
    if user is None:
        default_account = Account(name="ROOT")
        db.session.add(default_account)
        db.session.flush()
        db.session.commit()
        encrypted_password = utils.hash_password(app.config['SUPER_ADMIN_PASSWORD'])
        user_datastore.create_user(email=app.config['SUPER_ADMIN_EMAIL'],password=encrypted_password, account_id=default_account.id)
        db.session.commit()
        user_datastore.add_role_to_user(app.config['SUPER_ADMIN_EMAIL'], 'super-admin')
        db.session.commit()

    status = Status.query.first()
    if status is None:
        db.session.add(Status(name="created", description="Created"))
        db.session.add(Status(name="processing", description="Processing"))
        db.session.add(Status(name="complete", description="Complete"))
        db.session.add(Status(name="error", description="Error"))
        db.session.add(Status(name="sent", description="Sent"))
        db.session.add(Status(name="received", description="Recieved"))
        db.session.add(Status(name="approved", description="Approved"))
        db.session.add(Status(name="rejected", description="Rejected"))
        db.session.commit()
