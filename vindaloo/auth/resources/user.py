from vindaloo.resource import ModelResource
from vindaloo.models import User


class UserResource(ModelResource):

    class Meta:
        name = 'user'
        model = User
