from vindaloo.resource import ModelResource
from vindaloo.models import Group
from vindaloo.auth.schemas.group import GroupSchema


class GroupResource(ModelResource):

    class Meta:
        model = Group
        schema = GroupSchema
