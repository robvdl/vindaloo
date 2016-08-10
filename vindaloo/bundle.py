import json

from pyramid.decorator import reify


class Bundle:

    def __init__(self, obj=None, items=None, data=None, model=None, schema=None):
        self.obj = obj
        self.items = items or []
        self.data = data or {}
        self.model = model
        self.schema = schema

    def __repr__(self):
        if self.obj is not None:
            return '<Bundle obj={} data={}>'.format(self.obj, self.data)
        else:
            return '<Bundle items={} data={}>'.format(list(self.items), self.data)

    @reify
    def json(self):
        """
        Format JSON nicely for display, used by HTML renderer.

        :return: Rendered JSON string.
        """
        # Possibly move this somewhere later, but is OK here for now.
        return json.dumps(self.data, sort_keys=True, indent=4)

    def __json__(self, request):
        """
        The __json__ method will be called by the built-in Pyramid
        'json' renderer if a Bundle object is passed to the renderer.

        The built-in 'json' renderer will automatically call this method,
        which must return a dict that can then be serialized to JSON.

        :param request: Pyramid request object.
        :return: dict
        """
        return self.data

    def __iter__(self):
        """
        The __iter__ method is used by the pyramid_jinja2 renderer.
        If we send a Bundle object to the renderer, then we can adapt
        this Bundle object into a dictionary, which is needed because
        pyramid_jinja2 doesn't normally support an object to be passed
        to the renderer.

        If we implement the __iter__ method and yield ('bundle', self),
        then that would be the same as the pyramid_jinja2 renderer
        being passed the dict {'bundle': bundle_obj}.

        :return: generator
        """
        yield ('bundle', self)
