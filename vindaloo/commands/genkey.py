from vindaloo.cli import BaseCommand
from vindaloo.core.utils import random_key_generator


class Command(BaseCommand):
    """
    Management command to generate a secure secret key.
    """

    def handle(self, args):
        print(random_key_generator(40))
