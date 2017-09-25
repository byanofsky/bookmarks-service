import datetime

from sqlalchemy import (Column, Integer, String, Text, ForeignKey, DateTime)
from sqlalchemy.orm import relationship

from bookmarks_service.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    email = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(60), nullable=False)

    bookmarks = relationship("Bookmark", back_populates="user")

    api_keys = relationship("API_Key", back_populates="user")

    def __init__(self, name, email, password_hash):
        self.name = name
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return '<User %r>' % (self.name)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


class API_Key(Base):
    __tablename__ = 'api_keys'
    id = Column(String(24), primary_key=True, unique=True, nullable=False)
    secret = Column(String(60), nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="api_keys")

    def __init__(self, id, secret, user_id):
        self.id = id
        self.secret = secret
        self.user_id = user_id

    def __repr__(self):
        return '<API_Key %r>' % (self.id)

    def json(self):
        return {
            'id': self.id,
            'secret': self.secret,
            'user_id': self.user_id
        }


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(String(6), primary_key=True, unique=True, nullable=False)
    url = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="bookmarks")

    requests = relationship("Request", back_populates="bookmark")

    def __init__(self, id, url, user_id):
        self.id = id
        self.url = url
        self.user_id = user_id

    def __repr__(self):
        return '<Bookmark %r>' % (self.id)

    def json(self):
        return {
            'id': self.id,
            'url': self.url,
            'user_id': self.user_id
        }


class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ip = Column(String(45))
    date = Column(DateTime)

    bookmark_id = Column(String(6), ForeignKey('bookmarks.id'))
    bookmark = relationship("Bookmark", back_populates="requests")

    def __init__(self, ip, date, bookmark_id):
        self.ip = ip
        self.date = datetime.datetime.now()
        self.bookmark_id = bookmark_id

    def __repr__(self):
        return '<Request %r>' % (self.id)
