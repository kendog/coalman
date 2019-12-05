#from flask_marshmallow import Marshmallow, fields
from marshmallow import Schema, fields

from .models import TagGroup, Tag, File, Project

#ma = Marshmallow()

# Define Schemas
class TagGroupSchema(Schema):
    class Meta:
        model = TagGroup
        # Fields to expose
        fields = ('name', 'tag_id')


class TagSchema(Schema):
    #tag_group = Nested(TagGroupSchema)

    class Meta:
        model = Tag
        # Fields to expose
        fields = ('name', 'tag_id', 'tag_group')


class FileSchema(Schema):
    #tags = Nested(TagGroupSchema, many=True)

    class Meta:
        model = File
        # Fields to expose
        fields = ('id', 'name', 'title', 'desc', 'tags')

class ProjectSchema(Schema):
    title = fields.String(attribute="name")
    start = fields.DateTime(attribute="duedate")

    class Meta:
        model = Project
        # Fields to expose
        fields = ('id', 'title', 'start')
