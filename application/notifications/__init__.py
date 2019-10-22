from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import notifications_bp
from .apis import notifications_apis_bp
from ..models import db, Message, Archive

app.register_blueprint(notifications_bp)
app.register_blueprint(notifications_apis_bp)

def send_notification(user_id, message_id):

    notification = Notification(user_id=user_id, message_id=message_id, notification_status_id=0)
    db.session.add(notification)
    db.session.commit()

    # Build the Mail
    user = Message.query.filter_by(id=user_id).first()
    message_template = Message.query.filter_by(id=message_id).first()

    header = 'From: %s\n' % app.config['SMTP_USERNAME']
    header += 'To: %s\n' % user.email
    header += 'Subject: %s\n\n' % message.subject
    message = header + message_template.message;
    # Send the Mail
    server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
    results = server.sendmail(app.config['SMTP_USERNAME'], user.email, message)

    server.quit()

    notification.notification_status_id = 1
    db.session.commit()
    return results
