import datetime

from sqlalchemy import (Column, Integer, String, Text, ForeignKey, DateTime)
from sqlalchemy.orm import relationship

from bookmarks_service.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    email = Column(String(256), unique=True, nullable=False)
    api_key = Column(String(24), unique=True)
    secret = Column(String(60), nullable=False)

    bookmarks = relationship("Bookmark", back_populates="users")

    def __init__(self, name, email, secret):
        self.name = name
        self.email = email
        self.secret = secret

    def __repr__(self):
        return '<User %r>' % (self.username)


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(String(6), primary_key=True, unique=True, nullable=False)
    url = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="bookmarks")

    def __init__(self, id, url, user_id):
        self.id = id
        self.link = link
        self.user_id = user_id

    def __repr__(self):
        return '<Bookmark %r>' % (self.id)


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
