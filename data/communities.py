import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Communities(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'communities'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creater = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    collaborators = sqlalchemy.Column(sqlalchemy.String)
    posts = sqlalchemy.Column(sqlalchemy.String)

    user = orm.relation('User')
