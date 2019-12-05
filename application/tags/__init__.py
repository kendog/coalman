"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .manage import manage_tags_bp
from .apis import tags_apis_bp
from ..models import TagGroup, Tag

app.register_blueprint(manage_tags_bp)
app.register_blueprint(tags_apis_bp)

@app.context_processor
def inject_projects():
    tag_groups = []
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return dict(current_tag_groups=tag_groups)


@app.context_processor
def inject_projects():
    tag_hash = {}
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    for groups in tag_groups:
        tag_hash[groups.name] = Tag.query.filter_by(tag_group=TagGroup.query.filter_by(name=groups.name).first()).order_by(Tag.weight).all()

    return dict(current_tag_hash=tag_hash)
