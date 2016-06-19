from vindaloo.cli import BaseCommand
from vindaloo.db import Model
from vindaloo.api.resources import UserResource, GroupResource, PermissionResource


class Command(BaseCommand):
    """
    Creates database tables and permissions.
    """

    def handle(self, args):
        Model.metadata.create_all(self.dbsession.bind)

        # Creates permissions for the auth resources only for now.
        for resource in (UserResource, GroupResource, PermissionResource):
            resource.create_permissions(self.dbsession)
