import passlib.hash
from pyramid.security import remember, forget

from .models import User


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
