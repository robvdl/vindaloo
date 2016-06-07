from marshmallow import Schema, fields
from pyramid.httpexceptions import HTTPForbidden

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
            # TODO: find a better way to deal with the default body template.
            return HTTPForbidden('Invalid username or password.',
                                 body_template='${detail}')

    def delete(self):
        self.request.logout()
        return {'message': 'Logout successful.'}
