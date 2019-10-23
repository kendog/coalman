"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, MessageTemplate, Account



# Blueprint Configuration
messages_bp = Blueprint('messages_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@messages_bp.route('/messages')
@roles_required('super-admin')
def messages():
    messages = MessageTemplate.query.all()
    return render_template('messages/list.html', messages=messages)


@messages_bp.route('/messages/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def messages_add():
    if 'submit-add' in request.form:
        message = MessageTemplate(name=request.form['name'],subject=request.form['subject'], message=request.form['message'], account_id=request.form['account_id'])
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('messages_bp.messages'))
    accounts = Account.query.all()
    return render_template('messages/form.html', template_mode='add', accounts=accounts)


@messages_bp.route('/messages/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def messages_edit(id):
    message = MessageTemplate.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if message:
            message.name = request.form['name']
            message.account_id = request.form['account_id']
            db.session.commit()
        return redirect(url_for('messages_bp.messages'))
    accounts = Account.query.all()
    return render_template('messages/form.html', template_mode='edit', message=message, accounts=accounts)


@messages_bp.route('/messages/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def messages_delete(id):
    message = MessageTemplate.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if message:
            db.session.delete(message)
            db.session.commit()
        return redirect(url_for('messages_bp.messages'))
    accounts = Account.query.all()
    return render_template('messages/form.html', template_mode='delete', message=message, accounts=accounts)
