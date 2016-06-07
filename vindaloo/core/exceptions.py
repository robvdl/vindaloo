def format_json_exception(exception, status, body, title, environ):
    """
    Since Pyramid 1.7, any HTTP Exceptions that are either raised by
    the application or returned as a response can be automatically
    rendered to JSON if the correct headers are sent to the server.

    This is great feature, however the message isn't formatted very
    nicely by default because the body is multiline and contains
    newline characters in it.

    We fix this globally by monkey-patching the HTTPException._json_formatter
    method to point to this one.
    """
    # Tidies up \n\n\n put into the body field by Pyramid.
    lines = list(filter(None, body.splitlines()))

    return {
        'message': lines[0],  # We only care about the first line for JSON.
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
