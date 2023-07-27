from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship, backref

from connect import Base, engine


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    surname = Column(String(150), index=True)
    phone = Column(String(16), unique=True, index=True)
    email = Column(String(150), unique=True, index=True)


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    surname = Column(String(150), index=True)
    birthday = Column(Date, index=True)
    description = Column(String(250), nullable=True)
    phone = Column(String(16), unique=True, index=True)
    email = Column(String(150), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User, backref="contacts")


Base.metadata.create_all(bind=engine)
