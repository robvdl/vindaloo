def validate_schema(request, schema):
    content_type = request.headers.get('Content-Type')

    if request.method == 'GET':
        request_vars = dict(request.GET)
    elif content_type == 'application/json':
        request_vars = request.json_body
    else:
        # TODO: process form data
        request_vars = {}

    # Use Marshmallow to deserialize and add to request object.
    deserialized = schema.load(request_vars)
    request.validated = deserialized.data
    request.errors = deserialized.errors
