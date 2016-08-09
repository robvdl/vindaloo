def view(**kwargs):
    """
    The @view decorator is used in resource and service classes.

    Simply stores the kwargs in a list on the function itself,
    func.__views__, which then gets used later when registering
    routes and views at application startup, this happens in the
    setup_routes function of resources and services.
    """

    def wrapper(func):
        views = getattr(func, '__views__', None)

        if views is None:
            views = []
            setattr(func, '__views__', views)

        views.append(kwargs)
        return func

    return wrapper
