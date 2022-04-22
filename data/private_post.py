import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class PrivatePost(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'private_post'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creater = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    content = sqlalchemy.Column(sqlalchemy.String)
    group = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('communities.id'))

    user = orm.relation('User')
    communities = orm.relation('Communities')