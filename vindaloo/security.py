import os
import binascii

import passlib.hash
from pyramid.security import Allow, remember, forget, ALL_PERMISSIONS

from .models import User, Group, Permission


def groupfinder(username, request):
    """
    The groupfinder callback is called by Pyramid, it should return a
    list of groups (which must be strings), that the user has access to.

    Note that username parameter is not used because as we can already
    get to the current user through the request.user @reify property.
    """
    # Groups start with "group:" so we can have a special group "superuser".
    groups = ['group:' + group.name for group in request.user.groups]
    if request.user.is_superuser:
        groups.append('superuser')

    return groups


def get_authenticated_user(request):
    """
    Provides the request.user @reify property. If logged in this returns
    a User object, otherwise it returns None.

    :param request: Pyramid request object.
    :return: User object or None.
    """
    username = request.unauthenticated_userid
    if username:
        return User.get(request.dbsession, username=username)


def verify_password(user, password):
    """
    Validate password against hashed password in database.
    """
    try:
        hashalg = user.password.split('$')[1].replace('-', '_')
        password_module = getattr(passlib.hash, hashalg)
    except (AttributeError, IndexError):
        return False

    return password_module.verify(password, user.password)


def encrypt_password(settings, password):
    """
    Encrypts the password using passlib, hashalg has to be supported by
    passlib, ideally it should be pbkdf2_sha256, pbkdf2_sha512 or bcrypt.
    Passing in rounds is optional and if left out, will use passlib defaults.

    :param settings: Pyramid settings dict.
    :param password: Plain text password
    :return: Encrypted password
    """
    hashalg = settings['vindaloo.auth.hashalg']
    rounds = settings.get('vindaloo.auth.rounds')
    password_module = getattr(passlib.hash, hashalg)
    return password_module.encrypt(password, rounds=rounds)


def login_user(request, username, password):
    """
    Logs in a user by username and password.

    Available as a method on the request object:

    request.login(username, password)

    :param request: Pyramid request object.
    :param username: username string
    :param password: password string
    :return: True if the login was successful.
    """
    user = User.get(request.dbsession, username=username)

    if user and verify_password(user, password):
        # Login the user and set headers.
        headers = remember(request, username)
        request.response.headerlist.extend(headers)

        # Always refresh csrf_token on login for some extra security.
        request.session.new_csrf_token()

        # Login was successful.
        return True
    else:
        return False


def logout_user(request):
    """
    Logs the current user out.

    Available as a method on the request object:

    request.logout()

    :param request: Pyramid request object.
    """
    headers = forget(request)
    request.response.headerlist.extend(headers)


def generate_secret_key(length):
    """
    Generate a new secret key using length given.
    """
    return binascii.hexlify(os.urandom(length)).decode('utf-8')


class RootFactory:
    """
    The RootFactory class is where the list of ACLs is generated
    for each request.

    It is also an entry point for traversal-based applications.
    """

    def __init__(self, request):
        """
        The RootFactory constructor runs for every request so we don't
        want to do too much work here.

        :param request: Pyramid request object
        """
        # There is no point doing this for static requests.
        if request.matched_route and request.matched_route.name == '__/static/':
            return

        # To start with, superusers get access to everything.
        self.__acl__ = [(Allow, 'superuser', ALL_PERMISSIONS)]

        # Add ACLs from database to the list.
        perms = request.dbsession.query(Permission, Group).join(Group.permissions)
        self.__acl__.extend([(Allow, 'group:' + grp.name, perm.name) for perm, grp in perms])
