from .config import add_api
from .db import get_engine, get_session_factory, get_tm_session
from .security import get_authenticated_user


def includeme(config):
    settings = config.get_settings()
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')

    # Store the dbsession_factory in the application registry, unless one
    # has already been setup earlier, in which case we should use that.
    if 'session_factory' in config.registry:
        session_factory = config.registry['dbsession_factory']
    else:
        session_factory = get_session_factory(get_engine(settings))
        config.registry['dbsession_factory'] = session_factory

    # Adds the config.add_api() method to the Configurator.
    config.add_directive('add_api', add_api)

    # Make request.dbsession @reify property available for use.
    config.add_request_method(
        lambda request: get_tm_session(session_factory, request.tm),
        'dbsession', reify=True
    )

    # Also add the request.user @reify property in the same way.
    config.add_request_method(get_authenticated_user, 'user', reify=True)
