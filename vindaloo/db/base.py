class BaseModel:
    """
    Provides a base class for all models.

    Do not inherit your models of this class directly, this gets handled
    when initializing the declarative base factory.

    Instead just inherit all models of vindaloo.db.Model.
    """

    def __repr__(self):
        description = str(self)
        if description:
            return '<{} {}>'.format(self.__class__.__name__, description)
        else:
            return '<{}>'.format(self.__class__.__name__)

    @classmethod
    def get(cls, dbsession, **kwargs):
        """
        Returns model instance by kwargs, for example::

            admin_group = Group.get(dbsession, name='Administrator')

        :param dbsession: SQLAlchemy  database session.
        :param kwargs: Keyword arguments
        :return: Model instance or None if not found.
        """
        return dbsession.query(cls).filter_by(**kwargs).first()
