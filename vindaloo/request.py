import logging

from zope.interface import implementer
from pyramid.decorator import reify
from pyramid.interfaces import IRequest
from pyramid.request import Request as BaseRequest

log = logging.getLogger(__name__)


@implementer(IRequest)
class Request(BaseRequest):

    @reify
    def user(self):
        """
        Returns the current logged in User or None if not authenticated.

        :return: Current User object or None if not logged in.
        """
        username = self.unauthenticated_userid
        if username and self.ems_db:
            # TODO
            User = None
            return self.db_session.query(User).get(self.session['user']['id'])

    @reify
    def db_session(self):
        """
        Creates a new db_session instance that should be used throughout
        the request lifecycle, SQLAlchemy will do the connection pooling.

        :return: DBSession instance.
        """
        # TODO
        return None
