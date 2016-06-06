import re

# Regex to decompose a SQL Alchemy connection URL into it's base components
RE_DB_URL = re.compile(r'''
    ^(?P<dbms>[^:]+)                                # dbms
    ://                                             # ://
    (?P<username>[^:/@]+)?:?(?P<password>[^:/@]+)?  # username:password
    @?                                              # @
    (?P<host>[^:/]+)?:?(?P<port>\d+)?               # host:port
    /                                               # /
    (?P<database>.+)$                               # database
''', re.VERBOSE)


def parse_db_url(db_url):
    """
    Decomposes an SQLAlchemy connection URL and return a dictionary
    of the connection components.

    :param db_url: SQLAlchemy connection URL.
    :return: Dictionary of connection components or ValueError.
    """
    match = RE_DB_URL.match(db_url)
    if match:
        return match.groupdict()
    else:
        raise ValueError('Failed to parse DB connection URL')
