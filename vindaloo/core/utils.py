import re
import importlib

# this regex is used to convert camelcase model names to table or api names
RE_CAMELCASE = re.compile(r'([A-Z]+)(?=[a-z0-9])')


def generate_name_from_class(obj_class, separator='_'):
    """
    Generates a field name from a class name.

    For Example a model called BlogPost would become blog_post.

    You can change the separator from "_" to "-" when required.

    :param obj_class: Model or other class.
    :param separator: Separator character to use (default "_").
    :return: Generated field name.
    """
    def _join(match):
        word = match.group()
        if len(word) > 1:
            return '{}{}{}{}'.format(separator, word[:-1], separator, word[-1]).lower()
        return separator + word.lower()

    return RE_CAMELCASE.sub(_join, obj_class.__name__).lstrip(separator)


def import_class(class_name):
    """
    Imports a class by name.

    Will raise ImportError if the module does not exist,
    or will raise AttributeError if the class does not exist.

    :param class_name: Name of class to import.
    :return: Imported class
    """
    parts = class_name.split('.')
    module_name = '.'.join(parts[:-1])
    class_name = parts[-1]
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
