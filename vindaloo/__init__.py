from .config import add_api


def includeme(config):
    config.add_directive('add_api', add_api)
