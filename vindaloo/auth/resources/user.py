from sqlalchemy.orm import joinedload

from vindaloo.resource import ModelResource
from vindaloo.models import User
from vindaloo.auth.schemas.user import UserSchema


class UserResource(ModelResource):

    class Meta:
        model = User
        schema = UserSchema

    def build_query(self):
        return super().build_query().options(
            joinedload('groups'),
            joinedload('groups.permissions')
        )
