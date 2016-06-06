import getpass

from vindaloo.validation import RE_VALID_EMAIL
from vindaloo.cli import BaseCommand
from vindaloo.models import User


class Command(BaseCommand):
    """
    Creates a superuser, prompting the user for input.
    """

    def get_superuser_details(self):
        """
        Prompts for username, password and email. If no username is
        given then uses system user as default. Password must validate.
        Email can be blank.

        :return: a dict containing username, password and email
        """
        username = input("Username (default '" + getpass.getuser() + "'): ")
        if username == '':
            username = getpass.getuser()

        valid_password = False
        password = ''
        while not valid_password:
            password = getpass.getpass('Password: ')
            confirm_password = getpass.getpass('Repeat password: ')
            if password == '' or confirm_password == '':
                print('Error: Password can not be blank.')
            elif password != confirm_password:
                print('Error: Passwords do not match.')
            else:
                valid_password = True

        valid_email = False
        email = ''
        while not valid_email:
            email = input('Email: ')
            match = RE_VALID_EMAIL.search(email)
            if match or email == '':
                valid_email = True
            else:
                print('Error: Enter a valid email address.')

        return {
            'username': username,
            'password': password,
            'email': email
        }

    def create_superuser(self, superuser_details):
        """
        Creates a superuser in the database according to the parameters
        given in superuser_details.

        :param superuser_details: a dict containing username, password, email
        """
        user = User(username=superuser_details['username'],
                    email=superuser_details['email'],
                    is_superuser=True)
        user.set_password(self.settings, superuser_details['password'])
        self.dbsession.add(user)
        print('Superuser created successfully')

    def handle(self, args):
        superuser_details = self.get_superuser_details()
        self.create_superuser(superuser_details)
