from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response
from marshmallow import Schema, fields

from vindaloo.api import Api
from vindaloo.resource import Resource
from vindaloo.service import Service
from vindaloo.request import Request


class UserSchema(Schema):
    username = fields.Str()
    password = fields.Str()


class AuthSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserResource(Resource):

    class Meta:
        name = 'user'
        schema = UserSchema

    def get_list(self):
        return Response('OK')


class AuthService(Service):

    class Meta:
        name = 'auth'
        schema = AuthSchema

    def get(self):
        return {'response': 'OK'}

    def post(self):
        return {'response': 'OK'}


if __name__ == '__main__':
    config = Configurator(request_factory=Request)
    config.include('vindaloo')

    apiv1 = Api('v1', path='/api/v1')
    apiv1.add(AuthService)
    apiv1.add(UserResource)

    apiv2 = Api('v2', path='/api/v2')
    apiv2.add(AuthService)
    apiv2.add(UserResource)

    config.add_api(apiv1)
    config.add_api(apiv2)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8000, app)
    server.serve_forever()
