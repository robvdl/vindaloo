import re

from pyramid.config import Configurator
from pyramid.settings import asbool
from pyramid.session import SignedCookieSessionFactory
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

from .security import groupfinder, RootFactory


# Regex to decompose a SQL Alchemy connection URL into it's base components
RE_DB_URL = re.compile(r'''
    ^(?P<dbms>[^:]+)                                # dbms
    ://                                             # ://
    (?P<username>[^:/@]+)?:?(?P<password>[^:/@]+)?  # username:password
    @?                                              # @
    (?P<host>[^:/]+)?:?(?P<port>\d+)?               # host:port
    /                                               # /
    (?P<database>.+)$                               # database
''', re.VERBOSE)


def setup_configurator(settings, session_class=SignedCookieSessionFactory):
    """
    A helpful function that takes care of some of the session initialisation
    code so that the application doesn't need to.

    :param settings: Pyramid settings dict.
    :param session_class: The class used to construct the session factory.
    :return: Pyramid Configurator object.
    """
    # The secret key comes from the PasteDeploy .ini file and is required.
    secret_key = settings['session.secret']
    cookie_httponly = asbool(settings.get('session.cookie_httponly', True))
    cookie_secure = asbool(settings.get('session.cookie_secure', False))

    # Setup security policies.
    authn_policy = AuthTktAuthenticationPolicy(
        secret_key,
        http_only=cookie_httponly,
        secure=cookie_secure,
        callback=groupfinder,
        hashalg='sha512'
    )

    session_factory = session_class(
        secret_key,
        httponly=cookie_httponly,
        secure=cookie_secure,
    )

    return Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=ACLAuthorizationPolicy(),
        root_factory=RootFactory,
        session_factory=session_factory
    )


def add_api(config, api):
    """
    Adds an Api instance to the Pyramid Configurator, therefore adding
    routes and views for resources and services registered with that Api.

    :param config: Pyramid Configurator object.
    :param api: Api instance.
    """
    def callback():
        api.register(config)
        config.commit()

    # multiple Api objects can be added, so include it in the discriminator
    discriminator = ('add_api', api)
    config.action(discriminator, callable=callback)


def parse_db_url(db_url):
    """
    Decomposes an SQLAlchemy connection URL from the PasteDeploy .ini file
    and return a dictionary of the individual connection components.

    :param db_url: SQLAlchemy connection URL.
    :return: Dictionary of connection components or ValueError.
    """
    match = RE_DB_URL.match(db_url)
    if match:
        return match.groupdict()
    else:
        raise ValueError('Failed to parse DB connection URL')
