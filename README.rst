Vindaloo
========

Vindaloo is a new API library for the Pyramid web framework, using
SQLAlchemy as the ORM and Marshmallow for it's schemas, it is currently
under development.  Vindaloo only supports Python 3, Python 2 support
will not be added to keep the codebase tidy.

The project was created from the work that was done in the
PyramidCMS API, which has been abandoned since, but a lot was
learned from making this API which has gone into Vindaloo.

Vindaloo has been created from the ground up rather than starting
off as a fork, Colander has been replaced by Marshmallow and
Vindaloo no longer requires Cornice but just uses Pyramid directly.
