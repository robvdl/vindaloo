import json

from pyramid.httpexceptions import HTTPUnsupportedMediaType, HTTPBadRequest
from pyramid_jinja2 import renderer_factory

from vindaloo.bundle import Bundle
from vindaloo.core.utils import get_output_format


class ApiRenderer:
    """
    Renders API responses to either JSON or HTML based on request headers.
    """

    def __init__(self, info):
        self.info = info

    def __call__(self, value, system):
        request = system.get('request')

        # If we receive a dict, for example from a service, we can
        # still convert it into a bundle to allow html rendering.
        if type(value) is Bundle:
            bundle = value
        elif type(value) is dict:
            bundle = Bundle(data=value, template='api/obj_detail.jinja2')
        elif type(value) is list:
            bundle = Bundle(items=value, template='api/obj_list.jinja2')
        else:
            raise HTTPBadRequest(explanation='Invalid data type for API renderer.')

        if request is not None:
            output_format = get_output_format(request)

            if output_format == 'json':
                response = request.response
                response.content_type = 'application/json'
                return json.dumps(bundle.data, sort_keys=True)
            elif output_format == 'html':
                # Set template to use with pyramid_jinja2 renderer.
                self.info.name = bundle.template

                # Format JSON nicely for display and attach to bundle.
                bundle.json = json.dumps(bundle.data, sort_keys=True, indent=4)

                # Now delegate the rest to pyramid_jinja2.
                renderer = renderer_factory(self.info)
                return renderer({'bundle': bundle}, system)
            else:
                msg = 'Invalid output format: "{}".'.format(output_format)
                raise HTTPUnsupportedMediaType(explanation=msg)
