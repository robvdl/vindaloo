from marshmallow import Schema, fields
from pyramid.httpexceptions import HTTPUnauthorized

from vindaloo.service import Service


class AuthSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class AuthService(Service):

    class Meta:
        name = 'auth'
        schema = AuthSchema

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
