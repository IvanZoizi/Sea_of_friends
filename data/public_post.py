import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class PublicPost(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'public_post'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creater = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    content = sqlalchemy.Column(sqlalchemy.String)

    user = orm.relation('User')