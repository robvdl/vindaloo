def view(**kwargs):
    """
    The @view decorator is used in resource and service classes.

    Simply stores the kwargs in a list on the function itself,
    func.__views__, which then gets used later when registering
    routes and views at application startup, this happens in the
    setup_routes function of resources and services.
    """
    def wrapper(func):
        return add_view(func, **kwargs)

    return wrapper


def schema_view(view, info):
    """
    This is a "custom view deriver" function, added in Pyramid 1.7,
    it allows a custom keyword argument (schema=) to be registered
    with Pyramid and affects all views in the application, this
    then allows the schema= argument to be used with @view decorators.

    Although this may look fairly complex, what it does is actually
    very simple, all it does is store the schema from the schema= argument
    on the request object so that the view has access to when called.
    """
    schema = info.options.get('schema')
    if schema:
        def wrapper_view(context, request):
            request.schema = schema
            return view(context, request)
        return wrapper_view
    return view

schema_view.options = ('schema',)


def add_view(func, **kwargs):
    """
    Method to store view arguments when defining a resource or service.

    This is more commonly used through the @view decorator.

    :param func: The method being decorated.
    :param kwargs: View kwargs.
    :return: Return original function.
    """
    views = getattr(func, '__views__', None)

    if views is None:
        views = []
        setattr(func, '__views__', views)

    views.append(kwargs)
    return func
