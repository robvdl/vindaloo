from vindaloo.resource import ModelResource
from vindaloo.models import Permission


class PermissionResource(ModelResource):

    class Meta:
        name = 'permission'
        model = Permission
