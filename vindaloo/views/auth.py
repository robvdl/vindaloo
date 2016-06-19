from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, forbidden_view_config

from vindaloo.forms import LoginForm


@view_config(route_name='login', renderer='login.jinja2')
@forbidden_view_config(accept='text/html', renderer='login.jinja2')
def login(request):
    form = LoginForm(request.POST)
    return_url = request.POST.get('url', request.url)
    cancel_url = request.referer or return_url

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        if request.login(username, password):
            request.session.flash('Logged in successfully.', queue='success')
        else:
            request.session.flash('Invalid username or password.', queue='error')

    return {
        'return_url': return_url,
        'cancel_url': cancel_url,
        'form': form
    }


@view_config(route_name='logout')
def logout(request):
    request.logout()
    redirect_url = '/'  # request.route_url('home')
    return HTTPFound(location=redirect_url, headers=request.response.headers)
