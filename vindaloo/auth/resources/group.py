from vindaloo.resource import ModelResource
from vindaloo.models import Group


class GroupResource(ModelResource):

    class Meta:
        model = Group
