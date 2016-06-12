class Bundle:

    def __init__(self, obj=None, items=None, data=None, schema=None, template=None):
        self.obj = obj
        self.items = items or []
        self.data = data or {}
        self.schema = schema
        self.template = template
