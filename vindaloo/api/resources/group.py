from sqlalchemy.orm import joinedload

from vindaloo.resource import ModelResource
from vindaloo.models import Group
from vindaloo.api.schemas.group import GroupSchema


class GroupResource(ModelResource):

    class Meta:
        model = Group
        schema = GroupSchema

    def build_query(self):
        return super().build_query().options(
            joinedload('permissions')
        )
