from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import register


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
