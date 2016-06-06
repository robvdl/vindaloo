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
