import re

from pyramid.httpexceptions import HTTPBadRequest

RE_VALID_EMAIL = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b')


def validate_schema(request, schema):
    content_type = request.headers.get('Content-Type')

    # GET and DELETE should use query parameters instead of the body.
    # Having DELETE with a body doesn't really make sense anyway.
    if request.method in ('GET', 'DELETE'):
        request_vars = dict(request.GET)
    elif content_type == 'application/json':
        # Avoid a bad request if there is no body.
        if request.body:
            try:
                request_vars = request.json_body
            except ValueError:
                raise HTTPBadRequest(explanation='Failed to parse JSON request.')
        else:
            request_vars = {}
    else:
        # TODO: process form data
        request_vars = {}

    # Use Marshmallow to deserialize and add to request object.
    deserialized = schema.load(request_vars)
    request.validated = deserialized.data
    request.errors.update(deserialized.errors)
