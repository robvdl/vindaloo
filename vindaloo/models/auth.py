from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean, Table, DateTime
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256

from vindaloo.db import Model

# bridge tables
group_permission_table = Table(
    'group_permission', Model.metadata,
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permission.id'), primary_key=True)
)

user_group_table = Table(
    'user_group', Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True)
)


class Permission(Model):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    description = Column(Text)

    def __str__(self):
        return self.name


class Group(Model):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    permissions = relationship('Permission', secondary=group_permission_table)

    def __str__(self):
        return self.name


class User(Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False, unique=True)
    password = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    email = Column(Text)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    date_joined = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    groups = relationship('Group', secondary=user_group_table, backref='users')

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    def check_password(self, password):
        """
        Validate password against hashed password in database.
        """
        return pbkdf2_sha256.verify(password, self.password)

    def set_password(self, password):
        """
        Change the password for this user.
        """
        self.password = pbkdf2_sha256.encrypt(password, rounds=10000)
