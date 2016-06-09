from sqlalchemy.ext.declarative import declared_attr

from vindaloo.core.utils import generate_name_from_class


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

    @declared_attr
    def __tablename__(cls):
        """
        This gives a default table name which is just the model class
        name as lower case, can still be overridden however.

        The default is to lowercase the model name and use underscores
        between words rather than camelcase.
        """
        return generate_name_from_class(cls)

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
