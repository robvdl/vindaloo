from marshmallow import Schema, fields

from vindaloo.fields import ToMany


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    permissions = ToMany('vindaloo.auth.resources.permission.PermissionResource')
