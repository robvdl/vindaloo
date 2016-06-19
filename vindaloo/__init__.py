from pyramid.httpexceptions import HTTPException
from pyramid.settings import asbool

from .config import add_api
from .db import get_engine, get_session_factory, get_dbsession
from .security import get_authenticated_user, login_user, logout_user
from .core.exceptions import format_json_exception
from .views.auth import login, logout


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
    config.scan('.views')

    # Configure pyramid_jinja2 settings.
    config.add_jinja2_search_path('vindaloo:templates')
    config.add_jinja2_extension('jinja2.ext.with_')

    # Store the dbsession_factory in the application registry.
    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # Debug only really controls whether to send minified assets for now.
    settings['vindaloo.debug'] = asbool(settings.get('vindaloo.debug', 'false'))

    # Redirect URL for after login and logout.
    settings['vindaloo.login_redirect_url'] = settings.get('vindaloo.login_redirect_url', '/')
    settings['vindaloo.logout_redirect_url'] = settings.get('vindaloo.logout_redirect_url', '/')

    # Configures the passlib hash algorithm and settings to use.
    # The password algorithm, either pbkdf2_sha256, pbkdf2_sha512 or bcrypt.
    hashalg = settings.get('vindaloo.auth.hashalg', 'pbkdf2_sha256')
    settings['vindaloo.auth.hashalg'] = hashalg
    if 'vindaloo.auth.rounds' in settings:
        settings['vindaloo.auth.rounds'] = int(settings['vindaloo.auth.rounds'])

    # Adds the config.add_api() method to the Configurator.
    config.add_directive('add_api', add_api)

    # Renders API responses to either JSON or HTML based on request headers.
    config.add_renderer('api', 'vindaloo.renderers.ApiRenderer')

    # Make request.dbsession @reify property available for use.
    config.add_request_method(get_dbsession, 'dbsession', reify=True)

    # Also add the request.user @reify property in the same way.
    config.add_request_method(get_authenticated_user, 'user', reify=True)

    # Add methods for logging users in and out.
    config.add_request_method(login_user, 'login')
    config.add_request_method(logout_user, 'logout')

    # Adds a request.debug property, useful for use in templates.
    config.add_request_method(lambda r: settings['vindaloo.debug'], 'debug', reify=True)

    # Add the login and logout routes.
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    # Browsable HTML API views require serving of static files.
    static_url = settings.get('vindaloo.static_url', 'static')
    config.add_static_view(name=static_url, path='vindaloo:static')

    # Provide better JSON formatting for exceptions.
    HTTPException._json_formatter = format_json_exception
