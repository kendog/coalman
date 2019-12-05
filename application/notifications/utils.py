from flask import current_app as app
from ..models import User, MessageTemplate, Notification, Status
from flask_security import current_user
from ..db import db
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory
from flask_mail import Message
from .. import mail

def create_notification(user_id, project_id, message_template_id, send_email, send_sms):
    notification = Notification(user_id=user_id, message_template_id=message_template_id, status_name="created", project_id=project_id, creator_id=current_user.id)

    db.session.add(notification)
    db.session.commit()
    #send email/sms
    if send_email:
        send_email_notification(notification.id)
    if send_sms:
        send_sms_notification(notification.id)
    #return redirect(url_for('manage_notifications_bp.notifications'))


def send_email_notification(notification_id):

    notification = Notification.query.filter_by(id=notification_id).first()

    # Build the Mail
    #user = User.query.filter_by(id=notification.user_id).first()
    message_template = MessageTemplate.query.filter_by(id=notification.message_id).first()


    #msg = Message(message_template.subject, sender=app.config['MAIL_USERNAME'], recipients=[user.email])
    msg = Message(message_template.subject, sender=app.config['MAIL_USERNAME'], recipients=["kendog@gmail.com"])
    msg.body = message_template.message
    mail.send(msg)

    notification.status_name = "sent"
    db.session.commit()


def send_sms_notification(notification_id):
    notification = Notification.query.filter_by(id=notification_id).first()
    notification.status_name = "sent"
    db.session.commit()
