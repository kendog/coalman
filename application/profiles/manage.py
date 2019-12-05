"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import User, Profile, Account



# Blueprint Configuration
manage_profiles_bp = Blueprint('manage_profiles_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/manage')


@manage_profiles_bp.route('/profiles')
@roles_required('super-admin')
def profiles():
    profiles = Profile.query.all()
    return render_template('/profiles/manage/list.html', profiles=profiles)


@manage_profiles_bp.route('/profile/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def profile_add():
    if 'submit-add' in request.form:
        profile = Profile(
            name=request.form['name'],
            bio=request.form['bio'],
            address1=request.form['address1'],
            address2=request.form['address2'],
            city=request.form['city'],
            state=request.form['state'],
            zip=request.form['zip'],
            phone=request.form['phone'],
            user_id=request.form['user_id'],
            account_id=request.form['account_id'],
            creator_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for('manage_profiles_bp.profiles'))
    accounts = Account.query.all()
    users = User.query.all()
    profile = []
    return render_template('/profiles/manage/form.html', template_mode='add', profile=profile, accounts=accounts, users=users)


@manage_profiles_bp.route('/profile/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def profile_edit(id):
    profile = Profile.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if profile:
            profile.name = request.form.get('name')
            profile.bio = request.form.get('bio')
            profile.address1 = request.form.get('address1')
            profile.address2 = request.form.get('address2')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.zip = request.form.get('zip')
            profile.phone = request.form.get('phone')
            profile.user_id = request.form.get('user_id')
            profile.account_id = request.form.get('account_id')
            db.session.commit()
            return redirect(url_for('manage_profiles_bp.profiles'))
    accounts = Account.query.all()
    users = User.query.all()
    return render_template('/profiles/manage/form.html', template_mode='edit', profile=profile, accounts=accounts, users=users)


@manage_profiles_bp.route('/profile/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def profile_delete(id):
    profile = Profile.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if profile:
            db.session.delete(profile)
            db.session.commit()
            return redirect(url_for('manage_profiles_bp.profiles'))
    accounts = Account.query.all()
    users = User.query.all()
    return render_template('/profiles/manage/form.html', template_mode='delete', profile=profile, accounts=accounts, users=users)
