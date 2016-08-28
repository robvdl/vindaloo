from marshmallow import Schema
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPUnsupportedMediaType

from .validation import validate_schema


class ServiceMeta:
    """
    A configuration class for ``Service``.

    Provides sane defaults and the logic needed to augment these settings with
    the internal ``class Meta`` used on ``Service`` subclasses.
    """
    name = None
    path = None

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
            for verb in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
                if getattr(new_class, verb.lower(), None):
                    new_class._meta.allowed_methods.append(verb)

        return new_class


class Service(metaclass=ServiceMetaLoader):
    """
    Services are simple API endpoints when using a resource is too much.

    A good usage example for a service can be an authentication service.

    Services have Meta classes, but have much less options than resources.
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
        # request.schema is only there if the @view decorator has a schema
        return getattr(self.request, 'schema', Schema)

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
        # If the @view decorator is missing, create a default json view.
        for verb in cls._meta.allowed_methods:
            handler = getattr(cls, verb.lower(), None)
            views = getattr(handler, '__views__', [{'renderer': 'json'}])

            for view_kwargs in views:
                config.add_view(
                    cls,
                    attr='dispatch',
                    route_name=route,
                    request_method=verb,
                    **view_kwargs
                )

        # The fallback view is needed to send 405 or 415 or Pyramid sends 404.
        config.add_view(cls, attr='fallback_view', route_name=route)

    def validation_errors(self):
        self.response.status_code = 400
        return {'errors': self.request.errors}

    def dispatch(self):
        validate_schema(self.request, self.schema())
        if self.request.errors:
            return self.validation_errors()

        method = self.request.method.lower()
        handler = getattr(self, method)

        if callable(handler):
            response = handler()
            if self.request.errors:
                return self.validation_errors()

            return response

    # Views.

    def fallback_view(self):
        """
        The fallback view will be called if no view can be matched,
        which happens either if the request method if not allowed
        for this Service, or if the accept header contains an
        unsupported media type.

        Without the fallback view, Pyramid will just send a 404.

        :return: HTTP 405 or 415.
        """
        if self.request.method not in self.allowed_methods:
            raise HTTPMethodNotAllowed()
        else:
            raise HTTPUnsupportedMediaType()
