from vindaloo.resource import ModelResource
from vindaloo.models import User
from vindaloo.auth.schemas.user import UserSchema


class UserResource(ModelResource):

    class Meta:
        model = User
        schema = UserSchema
