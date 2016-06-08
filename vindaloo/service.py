from marshmallow import Schema
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPMethodNotAllowed

from .validation import validate_schema


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
        meta = getattr(new_class, 'Meta', None)
        new_class._meta = ServiceMeta(meta)

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

    @reify
    def schema(self):
        if self.request.method == 'DELETE':
            # Don't use the metaclass schema for DELETE.
            return Schema()
        else:
            # For everything else use the schema from the metaclass.
            return self._meta.schema() or Schema()

    @classmethod
    def get_path(cls, api):
        return '{}/{}'.format(api.path, cls._meta.path or cls._meta.name)

    @classmethod
    def setup_routes(cls, config, api):
        route = '{}-{}'.format(api.name, cls._meta.name)
        config.add_view(cls, attr='dispatch', route_name=route, renderer='json')
        config.add_route(route, cls.get_path(api))

    def validation_errors(self):
        self.request.response.status_code = 400
        return {'errors': self.request.errors}

    def dispatch(self):
        handler = getattr(self, self.request.method.lower(), None)
        if handler and callable(handler):
            # Did schema validation produce any errors?
            validate_schema(self.request, self.schema)
            if self.request.errors:
                return self.validation_errors()
            else:
                # Did the handler itself produce any errors?
                response = handler()
                if self.request.errors:
                    return self.validation_errors()
                else:
                    return response
        else:
            raise HTTPMethodNotAllowed()
