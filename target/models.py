import hashlib
import random
import datetime
from calendar import timegm

import jwt
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Product(Base):

    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    def __init__(self, email, first_name, last_name, password):
        self.email = email
        self.password = self.get_hashed_password(password)
        self.first_name = first_name
        self.last_name = last_name

    def encode_token(self):
        from target.settings import app
        try:
            payload = dict()
            now = datetime.datetime.utcnow()
            token_expiry = now + datetime.timedelta(days=5)
            payload['exp'] = timegm(token_expiry.utctimetuple())
            payload['iat'] = timegm(now.utctimetuple())
            payload['sub'] = self.id
            return jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        except Exception as ex:
            return ex

    @staticmethod
    def decode_token(auth_token):
        from target.settings import app
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithm='HS256')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Token expired. Log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Log in again.'

    def get_hashed_password(self, password):
        from target.settings import bcrypt, app
        return bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')).decode()

    @property
    def serialize(self):
        return {'user_id': self.id, 'email': self.email, 'first_name': self.first_name,
                'last_name': self.last_name}


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    created_by = Column(String(255), nullable=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {'id': int(self.id), 'product_id': self.product_id, 'description': self.description, 'created_by': int(self.created_by) if self.created_by else None}


def create_models():
    from target.settings.backend import DBBackend
    metadata = Base.metadata
    metadata.create_all(DBBackend().get_engine())


def create_first_revision():
    from alembic.config import Config
    from alembic import command
    import os
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'alembic.ini'))
    command.stamp(alembic_cfg, "head")


def main():
    create_models()
    create_first_revision()


if __name__ == "__main__":
    main()
