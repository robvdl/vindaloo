from marshmallow import Schema, fields

from .permission import PermissionSchema


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    permissions = fields.Nested(PermissionSchema, many=True)
