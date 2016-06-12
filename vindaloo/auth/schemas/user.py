from marshmallow import Schema, fields

from vindaloo.fields import ToMany


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    is_active = fields.Bool(default=True)
    is_superuser = fields.Bool(default=False)
    created_at = fields.DateTime()
    last_login = fields.DateTime()
    groups = ToMany('vindaloo.auth.resources.group.GroupResource')
