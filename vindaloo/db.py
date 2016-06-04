from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import register


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


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker(autoflush=False)
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def get_dbsession(request):
    """
    This method becomes a @reify property on the request, request.dbsession.

    It will return a new dbsession based on the dbsession_factory in the
    application registry.

    :param request: Pyramid request object
    :return: SQLAlchemy session
    """
    return get_tm_session(request.registry['dbsession_factory'], request.tm)


class BaseModel:
    """
    Provides a base class for all models.

    Do not inherit your models of this class directly, this gets handled
    when initializing the declarative base factory.

    Instead just inherit all models of Model.
    """

    def __repr__(self):
        description = str(self)
        if description:
            return '<{} {}>'.format(self.__class__.__name__, description)
        else:
            return '<{}>'.format(self.__class__.__name__)


Model = declarative_base(metadata=metadata, cls=BaseModel)
