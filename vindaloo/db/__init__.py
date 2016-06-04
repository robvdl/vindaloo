from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base

from .base import BaseModel
from .session import get_engine, get_session_factory, get_tm_session, get_dbsession


# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.readthedocs.org/en/latest/naming.html
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

Model = declarative_base(metadata=metadata, cls=BaseModel)

__all__ = [
    'NAMING_CONVENTION',
    'metadata',
    'Model',
    'get_engine',
    'get_session_factory',
    'get_tm_session',
    'get_dbsession'
]
