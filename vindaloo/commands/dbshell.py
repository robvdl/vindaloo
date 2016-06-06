import os
import shlex
import signal
from subprocess import call

from vindaloo.db import parse_db_url
from vindaloo.cli import BaseCommand
from vindaloo.core.exceptions import CommandError


class Command(BaseCommand):
    """
    Management command to open a database shell.

    At the moment only PostgreSQL, MySQL and SQLite are supported.
    """

    def load_dbms_shell(self, connection):
        is_mysql = connection['dbms'].startswith('mysql')
        is_postgresql = connection['dbms'].startswith('postgres')
        is_sqlite = connection['dbms'].startswith('sqlite')

        if is_mysql:
            # lowercase -p means prompt for password in mysql
            # if you leave it out, it will try to login without password
            command = 'mysql -u {username} -h {host} -D {database} -p'.format(**connection)
        elif is_postgresql:
            command = 'psql -U {username} -h {host} -d {database}'.format(**connection)
        elif is_sqlite:
            command = 'sqlite3 ' + connection['database']
        else:
            raise CommandError('Unsupported DBMS ' + connection['dbms'])

        if connection['port']:
            if is_mysql:
                command += ' -P ' + connection['port']
            elif is_postgresql:
                command += ' -p ' + connection['port']
            else:
                raise CommandError("SQLite doesn't support a port")

        try:
            call(shlex.split(command))
        except KeyboardInterrupt:
            # ctrl+c was pressed on dbshell password prompt so cleanup
            os.kill(os.getpid(), signal.SIGTERM)

    def handle(self, args):
        connection = parse_db_url(self.settings['sqlalchemy.url'])
        if connection['host'] is None:
            connection['host'] = 'localhost'
        self.load_dbms_shell(connection)
