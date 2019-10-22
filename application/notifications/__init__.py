from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import notifications_bp
from .apis import notifications_apis_bp
from ..models import db, Message, Archive

app.register_blueprint(notifications_bp)
app.register_blueprint(notifications_apis_bp)

def send_notification(uuid):
    archive = Archive.query.filter_by(uuid=uuid).first()
    archive.notification_status_id = 2
    db.session.commit()
    # Build the Mail
    message = Message.query.first()
    header = 'From: %s\n' % app.config['SMTP_USERNAME']
    header += 'To: %s\n' % archive.user_email
    header += 'Subject: %s\n\n' % message.subject
    message = header + message.message + '\n\n' + archive.link;
    # Send the Mail
    server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
    results = server.sendmail(app.config['SMTP_USERNAME'], archive.user_email, message)

    server.quit()
    #print "results", results
    archive.notification_status_id = 3
    db.session.commit()
    return results
