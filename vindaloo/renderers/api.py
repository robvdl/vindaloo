import json


class ApiRenderer(object):
    """
    Renders API responses to either JSON or HTML based on request headers.
    """

    def __init__(self, info):
        self.info = info

    def __call__(self, value, system):
        request = system.get('request')
        bundle = value

        if request is not None:
            response = request.response
            response.content_type = 'application/json'

            return json.dumps(bundle.data, sort_keys=True)
