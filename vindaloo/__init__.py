from .config import add_api
from .db import get_engine, get_session_factory, get_dbsession
from .security import get_authenticated_user, login_user, logout_user


def includeme(config):
    """
    The includeme() function gets called by Pyramid when executing::

        config.include('vindaloo')

    This will initialize and configure the library with the Pyramid framework.

    :param config: Pyramid Configurator object
    """
    settings = config.get_settings()
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.scan('.models')

    # Store the dbsession_factory in the application registry.
    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # Configures the passlib hash algorithm and settings to use.
    # The password algorithm, either pbkdf2_sha256, pbkdf2_sha512 or bcrypt.
    settings['vindaloo.auth.hashalg'] = settings.get('vindaloo.auth.hashalg', 'pbkdf2_sha256')
    if 'vindaloo.auth.rounds' in settings:
        settings['vindaloo.auth.rounds'] = int(settings['vindaloo.auth.rounds'])

    # Adds the config.add_api() method to the Configurator.
    config.add_directive('add_api', add_api)

    # Make request.dbsession @reify property available for use.
    config.add_request_method(get_dbsession, 'dbsession', reify=True)

    # Also add the request.user @reify property in the same way.
    config.add_request_method(get_authenticated_user, 'user', reify=True)

    # Add methods for logging users in and out.
    config.add_request_method(login_user, 'login')
    config.add_request_method(logout_user, 'logout')
