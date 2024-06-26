from datetime import datetime

import sqlalchemy

from sqlalchemy.util.preloaded import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class BotUser(SqlAlchemyBase, UserMixin):
    __tablename__ = 'bot_users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, default='user')
    modify_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.now)
    registered = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    skey = sqlalchemy.Column(sqlalchemy.String, default="None")
    language = sqlalchemy.Column(sqlalchemy.String, default='ru')

    def promote_to(self, role):
        self.status = role

    def dict(self):
        data = {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "name": self.name,
            "status": self.status,
            "registered": self.registered,
            "language": self.language
        }
        return data