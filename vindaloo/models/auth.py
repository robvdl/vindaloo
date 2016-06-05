from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean, Table, DateTime
from sqlalchemy.orm import relationship

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
    date_joined = Column(DateTime)
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

    def set_password(self, password):
        """
        Change the password for this user.
        """
        from vindaloo.security import encrypt_password
        self.password = encrypt_password(password)
