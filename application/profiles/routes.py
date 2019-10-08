"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, User, Profile



# Blueprint Configuration
profiles_bp = Blueprint('profiles_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@profiles_bp.route('/profile')
@login_required
def profile():
    user_id = current_user.get_id()
    user = User.query.filter_by(id=user_id).first()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        return render_template('profile.html', user=user, profile=profile)
    else:
        return render_template('profile.html', user=user)


@profiles_bp.route('/profile/<id>')
@login_required
def get_profile(id):
    profile = Profile.query.filter_by(id=id).first()
    return render_template('profile.html', profile=profile)


@profiles_bp.route('/profile/add', methods=['POST', 'GET'])
@login_required
def profile_add():
    if 'submit-add' in request.form:
        user_id = current_user.get_id()
        profile = Profile(
            username=request.form['username'],
            bio=request.form['bio'],
            name=request.form['name'],
            address1=request.form['address1'],
            address2=request.form['address2'],
            city=request.form['city'],
            state=request.form['state'],
            zip=request.form['zip'],
            phone=request.form['phone'],
            user_id=user_id)
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for('profiles_bp.profile'))
    users = User.query.all()
    return render_template('profile_add.html')


@profiles_bp.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def profile_edit():
    user_id = current_user.get_id()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if 'submit-edit' in request.form:
        if profile:
            profile.username = request.form.get('username')
            profile.bio = request.form.get('bio')
            profile.name = request.form.get('name')
            profile.address1 = request.form.get('address1')
            profile.address2 = request.form.get('address2')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.zip = request.form.get('zip')
            profile.phone = request.form.get('phone')
            db.session.commit()
        return redirect(url_for('profiles_bp.profile'))
    users = User.query.all()
    return render_template('profile_edit.html', profile=profile)


@profiles_bp.route('/profile/delete', methods=['POST', 'GET'])
@login_required
def profile_delete():
    user_id = current_user.get_id()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if 'submit-delete' in request.form:
        if profile:
            db.session.delete(profile)
            db.session.commit()
        return redirect(url_for('profiles_bp.profile'))
    return render_template('profile_delete.html', profile=profile)


@app.route('/admin/profiles')
@roles_required('admin')
def admin_profiles():
    profiles = Profile.query.all()
    return render_template('admin_profiles.html', profiles=profiles)


@app.route('/admin/profiles/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_profiles_add():
    if 'submit-add' in request.form:
        user_id = request.form['user_id']
        user = User.query.filter_by(id=user_id).first()
        profile = Profile(
            username=request.form['username'],
            bio=request.form['bio'],
            name=request.form['name'],
            address1=request.form['address1'],
            address2=request.form['address2'],
            city=request.form['city'],
            state=request.form['state'],
            zip=request.form['zip'],
            phone=request.form['phone'],
            user_id=user_id)
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for('profiles_bp.admin_profiles'))
    users = User.query.all()
    return render_template('admin_profiles_add.html', users=users)


@app.route('/admin/profiles/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_profiles_edit(id):
    profile = Profile.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        user_id = request.form['user_id']
        user = User.query.filter_by(id=user_id).first()
        if profile:
            profile.username = request.form.get('username')
            profile.bio = request.form.get('bio')
            profile.name = request.form.get('name')
            profile.address1 = request.form.get('address1')
            profile.address2 = request.form.get('address2')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.zip = request.form.get('zip')
            profile.phone = request.form.get('phone')
            profile.user_id = user_id
            db.session.commit()
        return redirect(url_for('profiles_bp.admin_profiles'))
    users = User.query.all()
    return render_template('admin_profiles_edit.html', profile=profile, users=users)


@app.route('/admin/profiles/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_profiles_delete(id):
    profile = Profile.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if profile:
            db.session.delete(profile)
            db.session.commit()
        return redirect(url_for('profiles_bp.admin_profiles'))
    users = User.query.all()
    return render_template('admin_profiles_delete.html', profile=profile, users=users)
