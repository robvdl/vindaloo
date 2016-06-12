class Bundle:

    def __init__(self, obj=None, items=None, data=None, schema=None, template=None):
        self.obj = obj
        self.items = items or []
        self.data = data or {}
        self.schema = schema
        self.template = template

    def __repr__(self):
        if self.obj is not None:
            return '<Bundle obj={} data={}>'.format(self.obj, self.data)
        else:
            return '<Bundle items={} data={}>'.format(list(self.items), self.data)
