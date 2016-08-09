from marshmallow import Schema
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPUnsupportedMediaType

from .validation import validate_schema
from .decorator import view


class ServiceMeta:
    """
    A configuration class for ``Service``.

    Provides sane defaults and the logic needed to augment these settings with
    the internal ``class Meta`` used on ``Service`` subclasses.
    """
    name = None
    path = None
    schema = None

    def __new__(cls, meta=None):
        overrides = {}

        # Handle overrides.
        if meta:
            for override_name in dir(meta):
                # No internals please.
                if not override_name.startswith('_'):
                    overrides[override_name] = getattr(meta, override_name)

        return object.__new__(type('ServiceMeta', (cls,), overrides))


class ServiceMetaLoader(type):
    """
    Loads the ServiceMeta class for the current service and mixes in the
    fields from the service Meta class.
    """

    def __new__(mcs, name, bases, attrs):
        new_class = super(ServiceMetaLoader, mcs).__new__(mcs, name, bases, attrs)

        # If Meta is None, don't do anything as there is no Meta class.
        meta = getattr(new_class, 'Meta', None)
        if meta:
            new_class._meta = ServiceMeta(meta)

            # Do this now so we don't have to at runtime.
            new_class._meta.allowed_methods = []
            for method in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
                if getattr(new_class, method.lower(), None):
                    new_class._meta.allowed_methods.append(method)

        return new_class


class Service(metaclass=ServiceMetaLoader):
    """
    Services are simple API endpoints when using a resource is too much.

    A good usage example for a service can be an authentication service.

    Services have Meta classes, but have much less options than resources,
    they can also use schemas like resources can.
    """

    def __init__(self, request):
        self.request = request
        self.request.errors = {}
        self.response = self.request.response

        # Set Allowed response header based on Meta class.
        allowed = self.allowed_methods + ['HEAD', 'OPTIONS']
        self.response.headers['Allowed'] = ', '.join(allowed)
        self.response.headers['Vary'] = 'Accept-Encoding'

        if self.request.method not in self.allowed_methods:
            raise HTTPMethodNotAllowed()

    @reify
    def schema(self):
        return self._meta.schema or Schema

    @reify
    def allowed_methods(self):
        return self._meta.allowed_methods

    @classmethod
    def get_path(cls, api):
        return '{}/{}'.format(api.path, cls._meta.path or cls._meta.name)

    @classmethod
    def setup_routes(cls, config, api):
        route = '{}-{}'.format(api.name, cls._meta.name)
        config.add_route(route, cls.get_path(api))

        # Setup views on the dispatch method.
        for view_kwargs in cls.dispatch.__views__:
            config.add_view(cls, attr='dispatch', route_name=route, **view_kwargs)

        # Setup fallbacks for unsupported accept header or Pyramid returns 404.
        config.add_view(lambda r: HTTPUnsupportedMediaType(), route_name=route)

    def validate_request(self):
        # Never do schema validation for DELETE requests.
        if not self.request.method == 'DELETE':
            validate_schema(self.request, self.schema())

    def validation_errors(self):
        self.response.status_code = 400
        return {'errors': self.request.errors}

    @view(accept='text/html', renderer='api')
    @view(accept='application/json', renderer='json')
    def dispatch(self):
        self.validate_request()
        if self.request.errors:
            return self.validation_errors()

        handler = getattr(self, self.request.method.lower())
        if handler and callable(handler):
            response = handler()
            if self.request.errors:
                return self.validation_errors()

            return response
