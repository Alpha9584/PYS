from sqlalchemy.orm import  declarative_base
from sqlalchemy import Column, Integer, String, UUID, DateTime, text
from datetime import datetime
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    fname = Column(String)
    lname = Column(String)
    survived_count = Column(Integer, default=0)
    dead_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now())