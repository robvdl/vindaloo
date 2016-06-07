def format_json_exception(exception, status, body, title, environ):
    """
    Since Pyramid 1.7, any HTTP Exceptions that are either raised by
    the application or returned as a response can be automatically
    rendered to JSON if the correct request headers are sent to the server.

    This is great feature, however the description isn't formatted
    very nicely because it is multiline and contains \n\n characters in it.

    We fix this globally by monkey-patching the HTTPException._json_formatter
    method to point to this one, it may not be the most elegant way,
    but I don't know of any Pyramid API to do this globally otherwise.
    """
    # Tidies up \n\n\n put into the description by Pyramid.
    lines = [l for l in body.split('\n') if l]

    # We only care about the last line if there is a custom description.
    return {
        'message': lines[-1],  # Normally Pyramid sets this to body.
        'code': status,
        'title': title
    }


class InvalidPage(Exception):
    """
    The InvalidPage exception is raised by the Paginator class.
    """
    pass


class PageNotAnInteger(Exception):
    """
    The PageNotAnInteger exception is raised by the Paginator class.
    """
    pass


class CommandError(Exception):
    """
    CommandError is an exception used by commands.
    """
    pass
