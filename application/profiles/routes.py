"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import User, Profile



# Blueprint Configuration
profiles_bp = Blueprint('profiles_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@profiles_bp.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(name='',bio='',address1='',address2='',city='',state='',zip='',phone='',account_id=current_user.account_id, user_id=current_user.id,creator_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
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
            db.session.commit()
    return render_template('/profiles/profile.html', profile=profile)


"""
@profiles_bp.route('/profile/<id>', methods=['POST', 'GET'])
@login_required
def profile_view(id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(name='',bio='',address1='',address2='',city='',state='',zip='',phone='',user_id=current_user.id,creator_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
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
            db.session.commit()
    return render_template('/profiles/profile.html', profile=profile)
"""


@profiles_bp.route('/profiles')
@roles_accepted('admin','super-admin')
def profiles():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_profiles_bp.profiles'))

    profiles = Profile.query.filter(Profile.account_id == current_user.account_id).all()

    return render_template('/profiles/list.html', profiles=profiles)


@profiles_bp.route('/profile/add', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def profile_add():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_profiles_bp.profiles_add'))

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
            account_id=current_user.account_id,
            creator_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for('profiles_bp.profiles'))
    users = User.query.filter(User.account_id == current_user.account_id).all()
    profile = []
    return render_template('/profiles/form.html', template_mode='add', profile=profile, users=users)


@profiles_bp.route('/profile/edit/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def profile_edit(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_profiles_bp.profiles_edit',id=id))

    profile = Profile.query.filter(Profile.id == id, Profile.account_id == current_user.account_id).first()

    if not profile:
        return redirect(url_for('profiles_bp.profiles'))

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
            profile.account_id = current_user.account_id
            db.session.commit()
            return redirect(url_for('profiles_bp.profiles'))
    users = User.query.filter(User.account_id == current_user.account_id).all()
    return render_template('/profiles/form.html', template_mode='edit', profile=profile, users=users)


@profiles_bp.route('/profile/delete/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def profile_delete(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_profiles_bp.profiles_delete',id=id))

    profile = Profile.query.filter(Profile.id == id, Profile.account_id == current_user.account_id).first()


    if not profile:
        return redirect(url_for('profiles_bp.profiles'))

    if 'submit-delete' in request.form:
        if profile:
            db.session.delete(profile)
            db.session.commit()
            return redirect(url_for('profiles_bp.profiles'))
    users = User.query.filter(User.account_id == current_user.account_id).all()
    return render_template('/profiles/form.html', template_mode='delete', profile=profile, users=users)
