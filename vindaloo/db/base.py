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
