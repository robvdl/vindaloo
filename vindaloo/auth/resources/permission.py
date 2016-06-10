from vindaloo.resource import ModelResource
from vindaloo.models import Permission
from vindaloo.auth.schemas.permission import PermissionSchema


class PermissionResource(ModelResource):

    class Meta:
        model = Permission
        schema = PermissionSchema
