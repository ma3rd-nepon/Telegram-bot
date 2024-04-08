from datetime import datetime

import sqlalchemy

from sqlalchemy.util.preloaded import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'site_users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modify_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.now)
    special_api = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def dict(self):
        data = {
            "id": self.id,
            "surname": self.surname,
            "name": self.name,
            "position": self.position,
            "email": self.email,
            "modify_date": self.modify_date,
            "telegram_id": self.telegram_id
        }
        return data

    def fullname(self):
        return f'{self.surname} {self.name}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
