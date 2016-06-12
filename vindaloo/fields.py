from marshmallow.fields import Nested

from .core.utils import import_class


class ToMany(Nested):

    def __init__(self, resource, schema=None, **kwargs):
        """
        The ToMany field is used to link to nested resources through
        their resource class rather than through a schema class,
        which is what the marshmallow.fields.Nested field uses.

        This can be handled in the constructor, where we can get the
        schema from the resource and pass it to the super constructor.

        :param resource: Nested resource to link to.
        :param schema: Optionally, override the resource schema.
        :param kwargs: Additional arguments passed to super constructor.
        """
        # Imports resource at app startup, can avoid import loops.
        # There is no runtime penalty as this happens at app startup.
        if type(resource) is str:
            self.resource = import_class(resource)
        else:
            self.resource = resource

        # Optionally override schema rather than use the resource schema.
        schema = schema or self.resource._meta.schema

        super().__init__(schema, many=True, **kwargs)


class ToOne(Nested):

    def __init__(self, resource, schema=None, **kwargs):
        """
        The ToOne field is used to link to nested resources through
        their resource class rather than through a schema class,
        which is what the marshmallow.fields.Nested field uses.

        This can be handled in the constructor, where we can get the
        schema from the resource and pass it to the super constructor.

        :param resource: Nested resource to link to.
        :param schema: Optionally, override the resource schema.
        :param kwargs: Additional arguments passed to super constructor.
        """
        # Imports resource at app startup, can avoid import loops.
        # There is no runtime penalty as this happens at app startup.
        if type(resource) is str:
            self.resource = import_class(resource)
        else:
            self.resource = resource

        # Optionally override schema rather than use the resource schema.
        schema = schema or self.resource._meta.schema

        super().__init__(schema, **kwargs)
