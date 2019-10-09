from flask_marshmallow import Marshmallow
from .models import TagGroup, Tag, File

ma = Marshmallow()

# Define Schemas
class TagGroupSchema(ma.Schema):
    class Meta:
        model = TagGroup
        # Fields to expose
        fields = ('name', 'tag_id')


class TagSchema(ma.Schema):
    tag_group = ma.Nested(TagGroupSchema)

    class Meta:
        model = Tag
        # Fields to expose
        fields = ('name', 'tag_id', 'tag_group')


class FileSchema(ma.Schema):
    tags = ma.Nested(TagGroupSchema, many=True)

    class Meta:
        model = File
        # Fields to expose
        fields = ('id', 'name', 'title', 'desc', 'tags')
