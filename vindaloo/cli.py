import os
import sys
import glob
import argparse
import importlib

import transaction
from pyramid.paster import get_appsettings, setup_logging

from .core.exceptions import CommandError
from .config import setup_configurator
from .db import get_engine, get_session_factory, get_tm_session


class BaseCommand:

    def __init__(self, app, command, config):
        self.app = app
        self.command = command
        self.parser = argparse.ArgumentParser(prog='{} {}'.format(app, command))
        self.config = config
        self.settings = config.get_settings()
        self.dbsession = None

    def run(self, *args):
        """
        Run the management command.

        This calls parser.parse_args() then calls the handle() method
        which should be implemented by the command itself.

        :param args: a list of arguments following the command
        """
        engine = get_engine(self.settings)
        session_factory = get_session_factory(engine)
        command_args = self.parser.parse_args(args)

        # Each command will run in one transaction by default.
        with transaction.manager:
            self.dbsession = get_tm_session(session_factory, transaction.manager)
            self.handle(command_args)

    def help(self):
        """
        Print help for this command.
        """
        self.parser.print_help()

    def setup_args(self, parser):
        """
        Override this to setup command-specific arguments, by default
        this method does nothing.

        :param parser: argparse parser object.
        """
        pass

    def handle(self, args):
        """
        The handle method is the entry point of the command, override
        this code to implement your command.

        :param args: Parsed command arguments.
        """
        pass

    def call_command(self, command, args=None):
        """
        Can be used to load and call another command from within
        a command, but without having to start up another process.

        :param command: Command to run
        :param args: Command arguments list
        """
        run_command(self.app, command, args or [], self.config)


def load_command(app, command, config):
    """
    Given the command name as string, try to load it the module
    from 'vindaloo.commands.<command>' and if that was successful,
    instantiate and return a new instance of that command class.

    :param app: Command line executable
    :param command: Command to load
    :param config: Pyramid Configurator object.
    :returns: instance of loaded Command class
    """
    try:
        module = importlib.import_module('vindaloo.commands.' + command)
    except ImportError:
        raise CommandError('"{} {}" command does not exist.'.format(app, command))

    return module.Command(app, command, config)


def run_command(app, command, command_args, config):
    """
    First loads then runs the given command, unless the command is
    help, in which case we display command-specific help instead.

    :param app: Command line executable
    :param command: Command to run
    :param command_args: Command argument list
    :param config: Pyramid Configurator object.
    """
    if command == 'help':
        cmd = load_command(app, command_args[0], config)
        cmd.help()
    else:
        cmd = load_command(app, command, config)
        cmd.run(*command_args)


def get_command_list():
    """
    Returns a list of available commands.
    """
    pattern = os.path.join(os.path.dirname(__file__), 'commands/*.py')
    commands = [os.path.basename(f[:-3]) for f in glob.glob(pattern)]
    commands.remove('__init__')
    return commands


def show_general_help(parser):
    """
    Show general help.

    :param parser: :obj:`argparse.ArgumentParser` instance.
    """
    parser.print_help()
    command_list = '\n  '.join(get_command_list())
    print('\navailable commands:\n  {}\n'.format(command_list))


def main(argv=sys.argv):
    # "app" is the name of the cli executable.
    app = os.path.basename(argv[0])

    # Main parser object, we then create another one for the command itself.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        dest='config_uri', type=str,
        help='The PasteDeploy .ini file to use for configuration.'
    )
    parser.add_argument(
        'command', type=str,
        help='The command to run (see available commands below).'
    )
    parser.add_argument(
        'command_args', type=str, nargs=argparse.REMAINDER,
        help='Optional command arguments (see: "{} help <command>").'.format(app)
    )

    if len(argv) < 2:
        show_general_help(parser)
    else:
        # Help commands don't require an .ini file, do this without argparse.
        if argv[1] == 'help':
            if len(argv) == 3:
                # Shows command-specific help.
                run_command(app, 'help', argv[2:], setup_configurator())
            else:
                show_general_help(parser)
        else:
            # Use argparse for all other commands.
            args = parser.parse_args(argv[1:])

            try:
                setup_logging(args.config_uri)
                settings = get_appsettings(args.config_uri)
            except FileNotFoundError:
                raise CommandError('Failed to open .ini file "{}".'.format(args.config_uri))

            config = setup_configurator(settings)
            config.include('vindaloo')
            run_command(app, args.command, args.command_args, config)
