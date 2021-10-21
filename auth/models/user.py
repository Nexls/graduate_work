import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, PrimaryKeyConstraint, UniqueConstraint, \
    Enum as saENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import TypeDecorator
from db.db import Base
import datetime
from utils.utils import generate_random_email
from enum import Enum


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    email = Column(Text, nullable=False, unique=True, default=generate_random_email)
    password = Column(String, nullable=False)

    def __init__(self, login, password, email):
        self.login = login
        self.password = password
        self.email = email

    def __repr__(self):
        return f'<User {self.login}>'


class Permissions(Enum):
    USER = 1
    PAYING_USER = 2
    ADMIN = 3


class EnumAsInteger(TypeDecorator):
    impl = Integer

    def __init__(self, enum_type):
        super(EnumAsInteger, self).__init__()
        self.enum_type = enum_type

    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enum_type):
            return value.value
        raise ValueError('expected %s value, got %s'
                         % (self.enum_type.__name__, value.__class__.__name__))

    def process_result_value(self, value, dialect):
        return self.enum_type(value)

    def copy(self, **kwargs):
        return EnumAsInteger(self.enum_type)


class Roles(Base):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    permissions = Column(EnumAsInteger(Permissions), nullable=False)


class SocialAccount(Base):
    __tablename__ = 'social_account'
    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship(User, backref=backref('social_accounts', lazy=True))

    social_id = Column(Text, nullable=False)
    social_name = Column(Text, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "users_sign_in" FOR VALUES IN ('web')"""
    )


class UserSignIn(Base):
    __tablename__ = 'users_sign_in'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        })

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    logined_by = Column(DateTime, default=datetime.datetime.utcnow)
    user_agent = Column(Text)
    user_device_type = Column(Text)

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>'
