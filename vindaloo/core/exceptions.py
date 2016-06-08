def format_json_exception(exception, status, body, title, environ):
    """
    Since Pyramid 1.7, any HTTP Exceptions that are either raised by
    the application or returned as a response can be automatically
    rendered to JSON if the correct headers are sent to the server.

    This is great feature, however the message isn't formatted very
    nicely by default, because the body text is multiline and contains
    newline characters in it.

    We fix this by monkey-patching the HTTPException._json_formatter
    method to point to this one, the message and description get
    separated out into individual fields rather than munged into one.
    """
    # Tidies up \n\n\n and whitespace put into the body field by Pyramid.
    lines = [line.strip() for line in body.splitlines() if line]

    if lines:
        message = lines[0]
        description = str(exception)
    else:
        message = title
        description = title

    json_data = {
        'message': message,
        'code': status,
        'title': title
    }

    # An additional description was provided with the exception.
    if description != message:
        json_data['description'] = description

    return json_data


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
