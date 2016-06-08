import logging

from .resource import Resource
from .service import Service

log = logging.getLogger(__name__)


class Api:

    def __init__(self, name, path):
        """
        Creates a new Api instance, which is used to register Resource
        and Service classes with.

        :param name: The name is used as a route prefix
        :param path: The path is a url prefix for services and resources
        """
        self.name = name
        self.path = path
        self.resources = []
        self.services = []
        self.__name__ = name

    def add(self, *items):
        """
        Adds one or more Resource or Services to this Api object.

        :param items: List of one or more resources or services to add.
        """
        for item in items:
            if issubclass(item, Resource):
                log.debug('Adding resource: {}'.format(item))
                self.resources.append(item)
            elif issubclass(item, Service):
                log.debug('Adding service: {}'.format(item))
                self.services.append(item)
            else:
                raise ValueError('Can only add classes of type Resource or Service.')

    def register(self, config):
        """
        The register method adds routes and views to the Pyramid
        configurator object (config) for all services and resources
        added to the api. The api index view and route are also added.

        The usual way to call this is through the config.add_api(api)
        method, as that will then make use of Pyramids conflict resolution
        system to avoid adding the same api object twice.

        It is possible to call this method directly, but you would just
        be bypassing the conflict resolution so it's best not to.
        """
        # Add routes and views for the api index page to the configurator.
        # Note that if you register a view on an instance method like this,
        # that method will then get a request object as it's first argument.
        # This is different to other views found in services and resources.
        index_route = '{}-api-index'.format(self.name)
        config.add_route(index_route, self.path)
        config.add_view(self.index, route_name=index_route, renderer='json')

        # Add routes and views for services.
        for service in self.services:
            service.setup_routes(config, self)

        # Add routes and views for resources.
        for resource in self.resources:
            resource.setup_routes(config, self)

    def index(self, request):
        """
        API index view.
        """
        return {
            'resources': [resource.get_path(self) for resource in self.resources],
            'services': [service.get_path(self) for service in self.services]
        }
