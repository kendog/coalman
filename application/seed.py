from flask import current_app as app
from .db import db
from .models import User, Role, Account, NotificationStatus, ArchiveStatus
from . import user_datastore

@app.before_first_request
def before_first_request():
    roles = Role.query.first()
    if roles is None:
        db.session.add(Role(name="super-admin", description="Super Admin"))
        db.session.add(Role(name="admin", description="Admin"))
        db.session.add(Role(name="end-user", description="End User"))
        db.session.commit()
    user = User.query.first()
    if user is None:
        encrypted_password = utils.hash_password(app.config['SUPER_ADMIN_PASSWORD'])
        user_datastore.create_user(email=app.config['SUPER_ADMIN_EMAIL'],password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user(app.config['SUPER_ADMIN_EMAIL'], 'super-admin')
        db.session.commit()
    notification_status = NotificationStatus.query.first()
    if notification_status is None:
        db.session.add(NotificationStatus(id=0, name="Created", tag_id="created"))
        db.session.add(NotificationStatus(id=1, name="Sent", tag_id="sent"))
        db.session.add(NotificationStatus(id=2, name="Received", tag_id="received"))
        db.session.add(NotificationStatus(id=3, name="Approved", tag_id="approved"))
        db.session.add(NotificationStatus(id=4, name="Rejected", tag_id="rejected"))
        db.session.commit()
    archive_status = ArchiveStatus.query.first()
    if archive_status is None:
        db.session.add(ArchiveStatus(id=0, name="Created", tag_id="created"))
        db.session.add(ArchiveStatus(id=1, name="Waiting", tag_id="Waiting"))
        db.session.add(ArchiveStatus(id=2, name="In Progress", tag_id="In Progress"))
        db.session.add(ArchiveStatus(id=3, name="Complete", tag_id="Complete"))
        db.session.add(ArchiveStatus(id=4, name="Error", tag_id="Error"))
        db.session.commit()
