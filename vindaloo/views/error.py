import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError

log = logging.getLogger(__name__)


@view_config(context=Exception)
def server_error(context, request):
    """
    This view handles any uncaught exceptions, except HTTP exceptions.

    The exception that was raised and traceback can be logged here.

    Respond with a HTTPInternalServerError response so Pyramid can choose
    whether to serve up HTML or JSON depending on the request headers.

    :param context: The exception raised.
    :param request: Pyramid request object.
    :return: HTTP Response.
    """
    log.error('Caught an unexpected exception.', exc_info=True)
    return HTTPInternalServerError(explanation='The server was unable to complete the response.')
