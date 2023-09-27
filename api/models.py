# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

DATABASE_URL = "mysql+mysqlconnector://root@localhost/db_python"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CapturedImage(Base):
    __tablename__ = 'captured_images'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(length=255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=50), unique=True, index=True)
    hashed_password = Column(String(length=60))
    role = Column(String(length=60), default="user")

Base.metadata.create_all(bind=engine)
