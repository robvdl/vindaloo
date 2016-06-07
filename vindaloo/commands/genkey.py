from vindaloo.cli import BaseCommand
from vindaloo.security import generate_secret_key


class Command(BaseCommand):
    """
    Management command to generate a secure secret key.
    """

    def handle(self, args):
        print(generate_secret_key(40))
