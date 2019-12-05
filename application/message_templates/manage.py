"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_login import login_required
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import MessageTemplate, Account



# Blueprint Configuration
manage_message_templates_bp = Blueprint('manage_message_templates_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/manage')


@manage_message_templates_bp.route('/message_templates')
@roles_required('super-admin')
def message_templates():
    message_templates = MessageTemplate.query.all()
    return render_template('/message_templates/manage/list.html', message_templates=message_templates)


@manage_message_templates_bp.route('/message_templates/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def message_templates_add():
    if 'submit-add' in request.form:
        message = MessageTemplate(name=request.form['name'],subject=request.form['subject'], message=request.form['message'], creator_id=current_user.id, account_id=request.form['account_id'])
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('manage_message_templates_bp.message_templates'))
    accounts = Account.query.all()
    return render_template('/message_templates/manage/form.html', template_mode='add', accounts=accounts)


@manage_message_templates_bp.route('/message_templates/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def message_templates_edit(id):
    message_template = MessageTemplate.query.filter_by(id=id).first()

    if 'submit-edit' in request.form:
        if message_template:
            message_template.name = request.form['name']
            message_template.subject = request.form['subject']
            message_template.message = request.form['message']
            message_template.account_id = request.form['account_id']
            db.session.commit()
        return redirect(url_for('manage_message_templates_bp.message_templates'))
    accounts = Account.query.all()
    return render_template('/message_templates/manage/form.html', template_mode='edit', message_template=message_template, accounts=accounts)


@manage_message_templates_bp.route('/message_templates/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def message_templates_delete(id):
    message_template = MessageTemplate.query.filter_by(id=id).first()

    if 'submit-delete' in request.form:
        if message_template:
            db.session.delete(message_template)
            db.session.commit()
        return redirect(url_for('manage_message_templates_bp.message_templates'))
    accounts = Account.query.all()
    return render_template('/message_templates/manage/form.html', template_mode='delete', message_template=message_template, accounts=accounts)
