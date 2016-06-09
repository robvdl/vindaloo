import re

# this regex is used to convert camelcase model names to table or api names
RE_CAMELCASE = re.compile(r'([A-Z]+)(?=[a-z0-9])')


def field_name(text, separator='_'):
    def _join(match):
        word = match.group()
        if len(word) > 1:
            return '{}{}{}{}'.format(separator, word[:-1], separator, word[-1]).lower()
        return separator + word.lower()

    return RE_CAMELCASE.sub(_join, text).lstrip(separator)
