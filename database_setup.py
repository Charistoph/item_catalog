# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Advert(Base):
    __tablename__ = 'advert'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    location = Column(String(250))
    address = Column(String(250))
    meal_type = Column(String(250))
    meal_time = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    creator = Column(String(250))
    attendee = Column(String(250))
    accept_attendee = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'address': self.address,
            'meal_type': self.meal_type,
            'meal_time' : self.meal_time,
        }


engine = create_engine('postgresql://catalog:password@localhost/catalog')


Base.metadata.create_all(engine)
