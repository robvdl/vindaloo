from vindaloo.cli import BaseCommand
from vindaloo.db import Model


class Command(BaseCommand):
    """
    Management command to create database tables.
    """

    def handle(self, args):
        Model.metadata.create_all(self.dbsession.bind)
