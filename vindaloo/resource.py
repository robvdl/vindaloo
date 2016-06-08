import logging

from marshmallow import Schema
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotImplemented, HTTPMethodNotAllowed

from .core.paginator import Paginator
from .validation import validate_schema

log = logging.getLogger(__name__)


class ResourceMeta:
    """
    A configuration class for ``Resource``.

    Provides sane defaults and the logic needed to augment these settings with
    the internal ``class Meta`` used on ``Resource`` subclasses.
    """
    name = None
    path = None
    paginator_class = Paginator
    allowed_methods = ['get', 'post', 'put', 'delete']
    list_allowed_methods = None
    detail_allowed_methods = None
    limit = 0
    max_limit = 1000
    model = None
    schema = None
    filters = None

    def __new__(cls, meta=None):
        overrides = {}

        # Handle overrides.
        if meta:
            for override_name in dir(meta):
                # No internals please.
                if not override_name.startswith('_'):
                    overrides[override_name] = getattr(meta, override_name)

        allowed_methods = overrides.get('allowed_methods',
                                        ['get', 'post', 'put', 'delete'])

        if overrides.get('list_allowed_methods') is None:
            overrides['list_allowed_methods'] = allowed_methods

        if overrides.get('detail_allowed_methods') is None:
            overrides['detail_allowed_methods'] = allowed_methods

        # Ensure all verbs are lowercase for consistency.
        overrides['list_allowed_methods'] = \
            [verb.lower() for verb in overrides['list_allowed_methods']]
        overrides['detail_allowed_methods'] = \
            [verb.lower() for verb in overrides['detail_allowed_methods']]

        return object.__new__(type('ResourceMeta', (cls,), overrides))


class ResourceMetaLoader(type):
    """
    Loads the ResourceMeta class for the current resource and mixes in the
    fields from the resource Meta class.
    """

    def __new__(mcs, name, bases, attrs):
        new_class = super(ResourceMetaLoader, mcs).__new__(mcs, name, bases, attrs)
        meta = getattr(new_class, 'Meta', None)
        new_class._meta = ResourceMeta(meta)

        return new_class


class Resource(metaclass=ResourceMetaLoader):
    """
    The base class for all resources.

    Resources are similar to TastyPie by design, however the implementation
    of some methods like collection put, collection delete is different.

    Also the patch method is not implemented, the one in TastyPie is far
    too complicated and not really necessary.
    """

    def __init__(self, request):
        self.request = request

    @reify
    def schema(self):
        # Don't use a schema for DELETE.
        if self.request.method == 'DELETE':
            schema = None
        elif self.request.method == 'GET' and self.is_list_route:
            schema = self._meta.filters
        else:
            schema = self._meta.schema

        return schema or Schema

    @reify
    def is_list_route(self):
        return self.request.matched_route.name.endswith('-list')

    @reify
    def is_detail_route(self):
        return self.request.matched_route.name.endswith('-detail')

    @classmethod
    def get_path(cls, api):
        return '{}/{}'.format(api.path, cls._meta.path or cls._meta.name)

    @classmethod
    def setup_routes(cls, config, api):
        list_path = cls.get_path(api)
        list_route = '{}-{}-list'.format(api.name, cls._meta.name)
        config.add_view(cls, attr='dispatch', route_name=list_route, renderer='json')
        config.add_route(list_route, list_path)

        detail_path = list_path + '/{id}'
        detail_route = '{}-{}-detail'.format(api.name, cls._meta.name)
        config.add_view(cls, attr='dispatch', route_name=detail_route, renderer='json')
        config.add_route(detail_route, detail_path)

    def validation_errors(self):
        self.request.response.status_code = 400
        return {'errors': self.request.errors}

    def dispatch(self):
        method = self.request.method.lower()

        if self.is_list_route:
            handler = getattr(self, method + '_list', None)
            allowed_methods = self._meta.list_allowed_methods
        else:
            handler = getattr(self, method + '_detail', None)
            allowed_methods = self._meta.detail_allowed_methods

        if handler and callable(handler) and method in allowed_methods:
            validate_schema(self.request, self.schema())

            # Did schema validation produce any errors?
            if self.request.errors:
                return self.validation_errors()
            else:
                response = handler()

                # Did the handler itself produce any errors?
                if self.request.errors:
                    return self.validation_errors()
                else:
                    return response
        else:
            raise HTTPMethodNotAllowed()

    # Views.

    def get_list(self):
        """
        Returns a serialized list of resources.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        raise HTTPNotImplemented()

    def get_detail(self):
        """
        Returns a single serialized resource.

        Calls ``obj_get`` to provide the data, then handles that result set
        and serializes it.

        Should return a HttpResponse (200 OK).
        """
        raise HTTPNotImplemented()

    def post_list(self):
        """
        Creates a new resource/object with the provided data.

        Calls ``obj_create`` with the provided data and returns a response
        with the new resource's location.

        If a new resource is created, return ``HttpCreated`` (201 Created).
        If ``Meta.always_return_data = True``, there will be a populated body
        of serialized data.
        """
        raise HTTPNotImplemented()

    def post_detail(self):
        """
        In some APIs this creates a new subcollection of the resource.

        It is not implemented by default because most people's data models
        aren't self-referential.
        """
        raise HTTPNotImplemented()

    def put_list(self):
        """
        Updates a list of existing resources with data from the request.

        Note that the implementation is quite different from what TastyPie
        does here, TastyPie deletes and replaces the entire list, however that
        considered far too dangerous so we don't do that.

        Instead we update any records in the list that have an ID specified,
        while creating new records where the ID is missing, this is the same
        behaviour as nested list fields that have full=True.

        Return ``HttpNoContent`` (204 No Content) if
        ``Meta.always_return_data = False`` (default).

        Return ``HttpAccepted`` (200 OK) if
        ``Meta.always_return_data = True``.
        """
        raise HTTPNotImplemented()

    def put_detail(self):
        """
        Updates an existing resource with data from the request.

        Unlike TastyPie, the object will not be created automatically
        if it does not exist, instead a 404 will be returned.

        Calls ``obj_update`` with the provided data.

        If an existing resource is modified and
        ``Meta.always_return_data = False`` (default), return ``HttpNoContent``
        (204 No Content).

        If an existing resource is modified and
        ``Meta.always_return_data = True``, return ``HttpAccepted`` (200
        OK).
        """
        raise HTTPNotImplemented()

    def delete_list(self):
        """
        Destroys a collection of resources/objects.

        Unlike TastyPie, this does not delete all objects in the collection,
        but rather a list of IDs must be passed in the request body which is
        much safer.

        Calls ``obj_delete_list``.

        If the resources are deleted, return ``HttpNoContent`` (204 No Content).
        """
        raise HTTPNotImplemented()

    def delete_detail(self):
        """
        Destroys a single resource/object.

        Calls ``obj_delete``.

        If the resource is deleted, return ``HttpNoContent`` (204 No Content).

        If the resource did not exist, return ``Http404`` (404 Not Found).
        """
        raise HTTPNotImplemented()


class ModelResource(Resource):
    pass
