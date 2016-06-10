class Bundle:

    def __init__(self, obj=None, items=None, data=None, template=None):
        self.obj = obj
        self.items = items or []
        self.data = data or {}
        self.template = template
