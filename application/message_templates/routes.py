"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_login import login_required
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import MessageTemplate, Account
from sqlalchemy import or_, and_



# Blueprint Configuration
message_templates_bp = Blueprint('message_templates_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@message_templates_bp.route('/message_templates')
@roles_accepted('admin','super-admin')
def message_templates():

    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_message_templates_bp.message_templates'))

    message_templates = MessageTemplate.query\
        .filter(MessageTemplate.account_id == current_user.account_id)\
        .all()

    return render_template('/message_templates/list.html', message_templates=message_templates)


@message_templates_bp.route('/message_templates/add', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def message_templates_add():
    if 'submit-add' in request.form:
        message = MessageTemplate(name=request.form['name'],subject=request.form['subject'], message=request.form['message'], creator_id=current_user.id, account_id=current_user.account_id)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('message_templates_bp.message_templates'))
    return render_template('/message_templates/form.html', template_mode='add')


@message_templates_bp.route('/message_templates/edit/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def message_templates_edit(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_message_templates_bp.message_templates_edit',id=id))

    message_template = MessageTemplate.query\
        .filter(and_(MessageTemplate.id == id, MessageTemplate.account_id == current_user.account_id))\
        .first()

    if not message_template:
        return redirect(url_for('message_templates_bp.message_templates'))

    if 'submit-edit' in request.form:
        if message_template:
            message_template.name = request.form['name']
            message_template.subject = request.form['subject']
            message_template.message = request.form['message']
            db.session.commit()
        return redirect(url_for('message_templates_bp.message_templates'))
    return render_template('/message_templates/form.html', template_mode='edit', message_template=message_template)


@message_templates_bp.route('/message_templates/delete/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def message_templates_delete(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_message_templates_bp.message_templates_edit',id=id))

    message_template = MessageTemplate.query\
        .filter(and_(MessageTemplate.id == id, MessageTemplate.account_id == current_user.account_id))\
        .first()

    if not message_template:
        return redirect(url_for('message_templates_bp.message_templates'))


    if 'submit-delete' in request.form:
        if message_template:
            db.session.delete(message_template)
            db.session.commit()
        return redirect(url_for('message_templates_bp.message_templates'))
    return render_template('/message_templates/form.html', template_mode='delete', message_template=message_template)
