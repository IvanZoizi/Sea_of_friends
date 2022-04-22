import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class PrivateComments(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'private_comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creater = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    content = sqlalchemy.Column(sqlalchemy.String)
    private_post = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('private_post.id'))

    user = orm.relation('User')
    posted = orm.relation('PrivatePost')
