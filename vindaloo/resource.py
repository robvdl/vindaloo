import logging

from marshmallow import Schema, fields
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotImplemented, HTTPMethodNotAllowed,\
    HTTPNotFound, HTTPUnsupportedMediaType

from .core.paginator import Paginator
from .core.utils import generate_name_from_class
from .validation import validate_schema
from .bundle import Bundle
from .fields import ToMany, ToOne
from .models import Permission
from .decorator import view

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
    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
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
                                        ['GET', 'POST', 'PUT', 'DELETE'])

        if overrides.get('list_allowed_methods') is None:
            overrides['list_allowed_methods'] = allowed_methods

        if overrides.get('detail_allowed_methods') is None:
            overrides['detail_allowed_methods'] = allowed_methods

        # Ensure all verbs are lowercase for consistency.
        overrides['list_allowed_methods'] = \
            [verb.upper() for verb in overrides['list_allowed_methods']]
        overrides['detail_allowed_methods'] = \
            [verb.upper() for verb in overrides['detail_allowed_methods']]

        # If name is missing we can determine it from the model class name.
        # This only works for resources however, not services.
        name = overrides.get('name')
        if name is None:
            model = overrides.get('model')
            if model:
                overrides['name'] = generate_name_from_class(model, separator='-')

        return object.__new__(type('ResourceMeta', (cls,), overrides))


class ResourceMetaLoader(type):
    """
    Loads the ResourceMeta class for the current resource and mixes in the
    fields from the resource Meta class.
    """

    def __new__(mcs, name, bases, attrs):
        new_class = super(ResourceMetaLoader, mcs).__new__(mcs, name, bases, attrs)

        # If Meta is None, don't do anything as there is no Meta class.
        meta = getattr(new_class, 'Meta', None)
        if meta:
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
        self.request.errors = getattr(self.request, 'errors', {})
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
    def filters(self):
        return self._meta.filters or Schema

    @reify
    def allowed_methods(self):
        if self.is_list_route:
            return self._meta.list_allowed_methods
        else:
            return self._meta.detail_allowed_methods

    @reify
    def is_list_route(self):
        return self.request.matched_route.name.endswith('-list')

    @reify
    def is_detail_route(self):
        return self.request.matched_route.name.endswith('-detail')

    @reify
    def model(self):
        return self._meta.model

    @classmethod
    def get_path(cls, api):
        return '{}/{}'.format(api.path, cls._meta.path or cls._meta.name)

    @classmethod
    def setup_routes(cls, config, api):
        """
        The static method setup_routes is called when an Api object is
        added to the Pyramid Configurator, using config.add_api().

        At this point, all of the resources and services registered
        with that Api will have the setup_routes() method called.

        :param config: Pyramid Configurator object.
        :param api: Api object.
        """
        # Create the list route.
        list_path = cls.get_path(api)
        list_route = '{}-{}-list'.format(api.name, cls._meta.name)
        config.add_route(list_route, list_path)

        # Create the detail route.
        detail_path = list_path + '/{id}'
        detail_route = '{}-{}-detail'.format(api.name, cls._meta.name)
        config.add_route(detail_route, detail_path)

        # Setup views for both the list and detail routes.
        # If the @view decorator is missing, create a default json view.
        for verb in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
            list_handler = getattr(cls, verb.lower() + '_list', None)
            detail_handler = getattr(cls, verb.lower() + '_detail', None)

            if callable(list_handler):
                views = getattr(list_handler, '__views__', [{'renderer': 'json'}])
                for view_kwargs in views:
                    config.add_view(
                        cls,
                        attr='dispatch',
                        route_name=list_route,
                        request_method=verb,
                        **view_kwargs
                    )

            if callable(detail_handler):
                views = getattr(detail_handler, '__views__', [{'renderer': 'json'}])
                for view_kwargs in views:
                    config.add_view(
                        cls,
                        attr='dispatch',
                        route_name=detail_route,
                        request_method=verb,
                        **view_kwargs
                    )

        # Setup fallbacks for unsupported accept header or Pyramid returns 404.
        config.add_view(cls, attr='fallback_view', route_name=list_route)
        config.add_view(cls, attr='fallback_view', route_name=detail_route)

    @classmethod
    def create_permissions(cls, dbsession):
        """
        Creates the 4 required permissions for the current resource class,
        create, read, update & delete.

        :param dbsession: SQLAlchemy database session.
        """
        for action in ('create', 'read', 'update', 'delete'):
            name = cls._meta.name
            perm = Permission(name='{}-{}'.format(name, action),
                              description='Able to {} {}.'.format(action, name))
            dbsession.add(perm)

    def validation_errors(self):
        """
        Sets status code to 400 and returns dict with list of errors.

        This is called if request.errors is not empty.
        """
        self.response.status_code = 400
        return {'errors': self.request.errors}

    def validate_request(self):
        """
        The validate_request method should run schema validation for the
        current request. This method can be overridden if needed and will
        often use different schemas based on the route or request method.
        """
        method = self.request.method
        is_list = self.is_list_route
        is_detail = self.is_detail_route

        # Only do schema validation for specific cases that use it.
        # This still needs to handle POST and PUT list cases when supported.
        if method == 'POST' and is_list or method == 'PUT' and is_detail:
            validate_schema(self.request, self.schema())

    def dispatch(self):
        """
        The dispatch method is called before the list or detail view,
        is called, e.g. before get_list or get_detail is called.

        The purpose of the dispatch method is to run the schema
        validation before the view (self.handler) is called.

        After that, the view (self.handler) is either called or the
        request is aborted and a list of errors is returned instead.

        :return: Response from handler, or list of errors.
        """
        self.validate_request()
        if self.request.errors:
            return self.validation_errors()

        method = self.request.method.lower()
        if self.is_list_route:
            handler = getattr(self, method + '_list')
        else:
            handler = getattr(self, method + '_detail')

        if callable(handler):
            response = handler()
            if self.request.errors:
                return self.validation_errors()

            return response

    def build_relationship_map(self, schema_fields, prefix=''):
        """
        This method uses recursion to find all relationship type
        fields (ToOne and ToMany) in a schema and then constructs a
        lookup table keyed by dotted field name and resource name
        as the values.

        :param schema_fields: List of fields starting from the toplevel schema.
        :param prefix: Prefix used for dotted field names.
        :return: Dict with dotted field names as key and resource as value.
        """
        relationships = {}

        for name, field in schema_fields.items():
            node_path = name + '.'
            node_name = prefix + name

            if issubclass(field.__class__, ToOne):
                nested_fields = field.nested._declared_fields
                relationships[node_name] = field.resource._meta.name
                relationships.update(self.build_relationship_map(nested_fields, node_path))

            if issubclass(field.__class__, ToMany):
                nested_fields = field.nested._declared_fields
                relationships[node_name] = field.resource._meta.name
                relationships.update(self.build_relationship_map(nested_fields, node_path))

            elif issubclass(field.__class__, fields.Nested):
                # We need to have access to the resource class, which ToOne()
                # and ToMany() both provide, you cannot use Nested() directly.
                raise ValueError('Must use provided ToOne and ToMany classes.')

        return relationships

    def extract_nested_resources(self, data, path):
        """
        This method uses recursion to find all nested resources in
        the dictionary called "data" that match the dotted path found
        in the "path" argument.

        The dotted path is split into segments and we traverse these
        segments until we reach the last segment where we are expecting
        to find the nested resources that need to be extracted,
        these are then collected and returned at the end of the function.

        Since we can expect to find either serialized ToOne and ToMany
        fields, we can expect either list or dictionary types.

        Note that the original data will be modified once a nested
        resource is extracted, it will be replaced simply by it's id.

        :param data: Dictionary containing serialized data.
        :param path: Dotted path to nested records to extract.
        :return: List of resources found.
        """
        # List of nested resources found so far.
        resources = []

        segments = path.split('.')
        new_path = '.'.join(segments[1:])
        value = data[segments[0]]

        # Was this a ToOne or ToMany type?
        if type(value) is list:
            if len(segments) > 1:
                for item in value:
                    resources.extend(self.extract_nested_resources(item, new_path))
            else:
                resources.extend(value)
                data[segments[0]] = [v['id'] for v in value]
        else:
            if len(segments) > 1:
                resources.extend(self.extract_nested_resources(value, new_path))
            else:
                resources.append(value)
                data[segments[0]] = value['id']

        return resources

    def build_response(self, schema, result):
        """
        Given the serialized result coming from Marshmallow,
        we now optimize the response size by moving nested records
        at the end of the response rather than embedding them.

        :param schema: Schema instance.
        :param result: Marshmallow result.
        :return: Optimised response dictionary.
        """
        # Builds a map of all ToOne and ToMany fields in dotted form.
        # We then order these starting with the outermost nodes.
        relationships = self.build_relationship_map(schema.fields)
        sorted_relationships = sorted(relationships.keys(),
                                      key=lambda p: p.count('.'), reverse=True)

        # List of additional resources used by the main resource.
        # These are placed at the end rather than embedding them,
        # which keeps response sizes small for repeated records.
        extra = {resource: {} for path, resource in relationships.items()}
        meta = {}

        # Is this a list response or detail response?
        if type(result.data) is list:
            data = result.data
        else:
            data = [result.data]

        # Loop through nodes in the schema, relationship nodes only.
        # Note that extracting the nested resources also modifies
        # the original data structure, this is explained in detail in
        # the docstring for the Resource.extract_nested_resources() method.
        for node_data in data:
            for path in sorted_relationships:
                resource_name = relationships[path]
                for nested_item in self.extract_nested_resources(node_data, path):
                    item_id = nested_item['id']
                    if item_id not in extra[resource_name]:
                        extra[resource_name][item_id] = nested_item

        return {
            'data': data,
            'extra': extra,
            'meta': meta
        }

    def obj_get(self, obj_id):
        return None

    def obj_get_list(self):
        return []

    # Views.

    @view(accept='text/html', renderer='api/obj_list.jinja2')
    @view(accept='application/json', renderer='json')
    def get_list(self):
        """
        Returns a serialized list of resources.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        items = self.obj_get_list()
        schema = self.schema(many=True)
        result = schema.dump(items)

        return Bundle(
            items=items,
            data=self.build_response(schema, result),
            model=self._meta.model,
            schema=schema
        )

    @view(accept='text/html', renderer='api/obj_detail.jinja2')
    @view(accept='application/json', renderer='json')
    def get_detail(self):
        """
        Returns a single serialized resource.

        Calls ``obj_get`` to provide the data, then handles that result set
        and serializes it.

        Should return a HttpResponse (200 OK).
        """
        obj = self.obj_get(self.request.matchdict['id'])

        if obj:
            schema = self.schema()
            result = schema.dump(obj)

            return Bundle(
                obj=obj,
                data=self.build_response(schema, result),
                model=self._meta.model,
                schema=schema
            )
        else:
            return HTTPNotFound(explanation='Object not found.')

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
        In some APIs this creates a new sub collection of the resource.

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

    def fallback_view(self):
        """
        The fallback view will be called if no view can be matched,
        which happens either if the request method if not allowed
        for this Resource, or if the accept header contains an
        unsupported media type.

        Without the fallback view, Pyramid will just send a 404.

        :return: HTTP 405 or 415.
        """
        if self.request.method not in self.allowed_methods:
            raise HTTPMethodNotAllowed()
        else:
            raise HTTPUnsupportedMediaType()


class ModelResource(Resource):

    @reify
    def dbsession(self):
        return self.request.dbsession

    def build_query(self):
        return self.dbsession.query(self.model)

    def apply_filters(self, query):
        return query

    def obj_get(self, obj_id):
        return self.build_query().get(obj_id)

    def obj_get_list(self):
        return self.apply_filters(self.build_query())
