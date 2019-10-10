"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, Tag, TagGroup



# Blueprint Configuration
tags_bp = Blueprint('tags_bp', __name__,
                    template_folder='templates',
                    static_folder='static')



@tags_bp.route('/tags')
@login_required
def tags_all():
    return redirect(url_for('tags_bp.tags', tag_group_tag='all'))


@tags_bp.route('/tags/<tag_group_tag>')
@login_required
def tags(tag_group_tag):
    tag_groups = TagGroup.query.all()
    tag_group = None
    if tag_group_tag == 'all':
        tags = Tag.query.order_by(Tag.weight).all()
    else:
        tag_group = TagGroup.query.filter_by(tag_id=tag_group_tag).first()
        tags = Tag.query.filter_by(tag_group_id=tag_group.id).order_by(Tag.weight).all()
    return render_template('admin_tags.html', tags=tags, tag_group=tag_group, tag_groups=tag_groups)


@tags_bp.route('/tags/add', methods=['POST', 'GET'])
@login_required
def tags_add():
    if 'submit-add' in request.form:
        tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
        db.session.add(Tag(name=request.form['name'], tag_id=request.form['tag_id'], tag_group=tag_group, weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('tags_bp.tags', tag_group_tag=tag_group.tag_id))
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_add.html', tag_groups=tag_groups)


@tags_bp.route('/tags/edit/<id>', methods=['POST', 'GET'])
@login_required
def tags_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(Tag.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
            tag = Tag.query.filter_by(id=id).first()
            tag.name = request.form.get('name')
            tag.tag_id = request.form.get('tag_id')
            tag.tag_group = tag_group
            tag.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('tags_bp.tags', tag_group_tag=tag_group.tag_id))
    tag = Tag.query.filter_by(id=id).first()
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_edit.html', tag=tag, tag_groups=tag_groups)


@tags_bp.route('/tags/delete/<id>', methods=['POST', 'GET'])
@login_required
def tags_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(Tag.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
            tag = Tag.query.filter_by(id=id).first()
            db.session.delete(tag)
            db.session.commit()
            return redirect(url_for('tags_bp.tags', tag_group_tag=tag_group.tag_id))
    tag = Tag.query.filter_by(id=id).first()
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_delete.html', tag=tag, tag_groups=tag_groups)


@tags_bp.route('/tag_groups')
@login_required
def tag_groups():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_tag_groups.html', tag_groups=tag_groups)


@tags_bp.route('/tag_groups/add', methods=['POST', 'GET'])
@login_required
def tag_groups_add():
    if 'submit-add' in request.form:
        db.session.add(TagGroup(name=request.form['name'], tag_id=request.form['tag_id'], weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('tags_bp.tag_groups'))
    return render_template('admin_tag_groups_add.html')


@tags_bp.route('/tag_groups/edit/<id>', methods=['POST', 'GET'])
@login_required
def tag_groups_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(TagGroup.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=id).first()
            tag_group.name = request.form.get('name')
            tag_group.tag_id = request.form.get('tag_id')
            tag_group.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('tags_bp.tag_groups'))
    tag_group = TagGroup.query.filter_by(id=id).first()
    return render_template('admin_tag_groups_edit.html', tag_group=tag_group)


@tags_bp.route('/tag_groups/delete/<id>', methods=['POST', 'GET'])
@login_required
def tag_groups_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(TagGroup.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=id).first()
            db.session.delete(tag_group)
            db.session.commit()
            return redirect(url_for('tags_bp.tag_groups'))
    tag_group = TagGroup.query.filter_by(id=id).first()
    return render_template('admin_tag_groups_delete.html', tag_group=tag_group)

"""

@tags_bp.route('/admin/tags')
@roles_required('admin')
def admin_tags_all():
    return redirect(url_for('tags_bp.admin_tags', tag_group_tag='all'))


@tags_bp.route('/admin/tags/<tag_group_tag>')
@roles_required('admin')
def admin_tags(tag_group_tag):
    tag_groups = TagGroup.query.all()
    tag_group = None
    if tag_group_tag == 'all':
        tags = Tag.query.order_by(Tag.weight).all()
    else:
        tag_group = TagGroup.query.filter_by(tag_id=tag_group_tag).first()
        tags = Tag.query.filter_by(tag_group_id=tag_group.id).order_by(Tag.weight).all()
    return render_template('admin_tags.html', tags=tags, tag_group=tag_group, tag_groups=tag_groups)


@tags_bp.route('/admin/tags/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tags_add():
    if 'submit-add' in request.form:
        tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
        db.session.add(Tag(name=request.form['name'], tag_id=request.form['tag_id'], tag_group=tag_group, weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('tags_bp.admin_tags', tag_group_tag=tag_group.tag_id))
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_add.html', tag_groups=tag_groups)


@tags_bp.route('/admin/tags/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tags_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(Tag.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
            tag = Tag.query.filter_by(id=id).first()
            tag.name = request.form.get('name')
            tag.tag_id = request.form.get('tag_id')
            tag.tag_group = tag_group
            tag.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('tags_bp.admin_tags', tag_group_tag=tag_group.tag_id))
    tag = Tag.query.filter_by(id=id).first()
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_edit.html', tag=tag, tag_groups=tag_groups)


@tags_bp.route('/admin/tags/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tags_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(Tag.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=request.form.get('tag_group_id')).first()
            tag = Tag.query.filter_by(id=id).first()
            db.session.delete(tag)
            db.session.commit()
            return redirect(url_for('tags_bp.admin_tags', tag_group_tag=tag_group.tag_id))
    tag = Tag.query.filter_by(id=id).first()
    tag_groups = TagGroup.query.all()
    return render_template('admin_tags_delete.html', tag=tag, tag_groups=tag_groups)


@tags_bp.route('/admin/tag_groups')
@roles_required('admin')
def admin_tag_groups():
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('admin_tag_groups.html', tag_groups=tag_groups)


@tags_bp.route('/admin/tag_groups/add', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tag_groups_add():
    if 'submit-add' in request.form:
        db.session.add(TagGroup(name=request.form['name'], tag_id=request.form['tag_id'], weight=request.form['weight']))
        db.session.commit()
        return redirect(url_for('tags_bp.admin_tag_groups'))
    return render_template('admin_tag_groups_add.html')


@tags_bp.route('/admin/tag_groups/edit/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tag_groups_edit(id):
    if 'submit-edit' in request.form:
        exists = db.session.query(TagGroup.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=id).first()
            tag_group.name = request.form.get('name')
            tag_group.tag_id = request.form.get('tag_id')
            tag_group.weight = request.form.get('weight')
            db.session.commit()
            return redirect(url_for('tags_bp.admin_tag_groups'))
    tag_group = TagGroup.query.filter_by(id=id).first()
    return render_template('admin_tag_groups_edit.html', tag_group=tag_group)


@tags_bp.route('/admin/tag_groups/delete/<id>', methods=['POST', 'GET'])
@roles_required('admin')
def admin_tag_groups_delete(id):
    if 'submit-delete' in request.form:
        exists = db.session.query(TagGroup.id).filter_by(id=id).scalar()
        if exists:
            tag_group = TagGroup.query.filter_by(id=id).first()
            db.session.delete(tag_group)
            db.session.commit()
            return redirect(url_for('tags_bp.admin_tag_groups'))
    tag_group = TagGroup.query.filter_by(id=id).first()
    return render_template('admin_tag_groups_delete.html', tag_group=tag_group)
"""
