import json

from pyramid.httpexceptions import HTTPUnsupportedMediaType, HTTPBadRequest
from pyramid_jinja2 import renderer_factory

from vindaloo.bundle import Bundle


class ApiRenderer:
    """
    Renders API responses to either JSON or HTML based on request headers.
    """

    def __init__(self, info):
        self.info = info

    def __call__(self, value, system):
        request = system.get('request')

        if request is not None:
            request.response.headers['Vary'] = 'Accept'
            bundle = self.get_bundle(value)

            # Ensure we check text/html first, the order matters.
            if 'text/html' in request.accept:
                # Set template to use with pyramid_jinja2 renderer.
                self.info.name = bundle.template

                # Format JSON nicely for display and attach to bundle.
                bundle.json = json.dumps(bundle.data, sort_keys=True, indent=4)

                # Now delegate the rest to pyramid_jinja2.
                renderer = renderer_factory(self.info)
                return renderer({'bundle': bundle}, system)
            elif 'application/json' in request.accept:
                response = request.response
                response.content_type = 'application/json'
                return json.dumps(bundle.data, sort_keys=True)
            else:
                raise HTTPUnsupportedMediaType(explanation='Invalid output format.')

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
