"""Routes for logged-in application."""
from flask import Blueprint, jsonify, render_template
from flask_login import current_user
from flask import current_app as app
from ..schemas import TagSchema, TagGroupSchema
from ..models import File, Tag, TagGroup
from flask_security import login_required
from ..import auth
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims)


# Blueprint Configuration
tags_apis_bp = Blueprint('tags_apis_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/api/v1')


# Tags APIs
@tags_apis_bp.route('/tags', methods=['GET'])
@jwt_required
def v1_tags_all():
    results = TagSchema(many=True).dump(Tag.query.order_by(Tag.tag_group_id, Tag.weight).all())
    return jsonify({'tags': results})


@tags_apis_bp.route('/tags/<tag_group_tag>', methods=['GET'])
@jwt_required
def v1_tags(tag_group_tag):
    tag_group = TagGroup.query.filter_by(tag_id=tag_group_tag).first()
    results = TagSchema(many=True).dump(Tag.query.filter_by(tag_group=tag_group).order_by(Tag.weight).all())
    return jsonify({'tags': results})


@tags_apis_bp.route('/tag_groups', methods=['GET'])
@jwt_required
def v1_tag_groups():
    results = TagGroupSchema(many=True).dump(TagGroup.query.order_by(TagGroup.weight).all())
    return jsonify({'tag_groups': results})
