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


def add_view(func, **kwargs):
    """
    Method to store view arguments when defining a resource or service.

    This is more commonly used through the @view decorator rather than
    directly, though it can be if needed.

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
