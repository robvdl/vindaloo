from marshmallow import Schema, fields
from pyramid.httpexceptions import HTTPUnauthorized

from vindaloo.service import Service
from vindaloo.decorators import view


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class SessionService(Service):
    """
    The SessionService is used to login and logout users.

    Keeping with good REST design, doing a POST to this service with
    a username and password in the body will login a user.

    To logout a user, just do a DELETE request to this service.
    """

    class Meta:
        name = 'session'

    @view(schema=LoginSchema, renderer='json')
    def post(self):
        username = self.request.validated['username']
        password = self.request.validated['password']

        if self.request.login(username, password):
            return {'message': 'Login successful.'}
        else:
            return HTTPUnauthorized(explanation='Invalid username or password.')

    def delete(self):
        self.request.logout()
        return {'message': 'Logout successful.'}
