from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, forbidden_view_config

from vindaloo.forms import LoginForm


@forbidden_view_config()
def redirect_to_login(request):
    """
    The forbidden view config will redirect the user to the login
    form when browsing the API using with web browser and the API
    returns a HTTPForbidden exception or response.

    If the accept headers are for application/json then we return
    the JSON exception un-altered.

    :param request: Pyramid request object.
    """
    # Prefer JSON over html, ignore ['*/*'] or we end up matching text/html.
    if list(request.accept) != ['*/*']:
        if 'text/html' in request.accept:
            redirect_url = request.route_url('login')
            redirect_url += '?return_url=' + request.path
            return HTTPFound(location=redirect_url)

    # For JSON responses pass through original exception.
    return request.exception


@view_config(route_name='login', renderer='login.jinja2')
def login(request):
    """
    The login form view, handles both POST and GET.

    :param request: Pyramid request object.
    """
    form = LoginForm(request.POST)
    redirect_url = request.registry.settings['vindaloo.login_redirect_url']
    return_url = request.POST.get('return_url', request.GET.get('return_url', redirect_url))

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        if request.login(username, password):
            request.session.flash('Logged in successfully.', queue='success')
            return HTTPFound(location=return_url, headers=request.response.headers)
        else:
            request.session.flash('Invalid username or password.', queue='error')

    return {
        'return_url': return_url,
        'form': form
    }


@view_config(route_name='logout')
def logout(request):
    """
    The logout view, logs the user out and redirects to the home page.

    :param request: Pyramid request object.
    """
    request.logout()
    redirect_url = request.registry.settings['vindaloo.logout_redirect_url']
    return HTTPFound(location=redirect_url, headers=request.response.headers)
