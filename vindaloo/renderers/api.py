import json

from pyramid.httpexceptions import HTTPUnsupportedMediaType, HTTPBadRequest
from pyramid_jinja2 import renderer_factory

from vindaloo.bundle import Bundle


class ApiRenderer:
    """
    Browsable API renderer.

    TODO: Could be made redundant by calling jinja2 renderer directly now,
    this was not the case in the past but could well be tidied up next.
    """

    def __init__(self, info):
        self.info = info

    def __call__(self, value, system):
        request = system.get('request')

        if request is not None:
            bundle = self.get_bundle(value)

            # Set template to use with pyramid_jinja2 renderer.
            self.info.name = bundle.template

            # Format JSON nicely for display and attach to bundle.
            bundle.json = json.dumps(bundle.data, sort_keys=True, indent=4)

            # Now delegate the rest to pyramid_jinja2.
            renderer = renderer_factory(self.info)
            return renderer({'bundle': bundle}, system)

    def get_bundle(self, value):
        """
        Returns a Bundle object based on the renderer value.

        If the renderer has received a Bundle, then just return value,
        if we received a list or dict then create and return a new
        Bundle object based on the value.

        :param value: Renderer value.
        :return: API Bundle object.
        """
        if type(value) is Bundle:
            return value
        elif type(value) is dict:
            return Bundle(data=value, template='api/obj_detail.jinja2')
        elif type(value) is list:
            return Bundle(items=value, template='api/obj_list.jinja2')
        else:
            raise HTTPBadRequest(explanation='Invalid data type for API renderer.')
