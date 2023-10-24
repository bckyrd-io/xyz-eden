# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


DATABASE_URL = "mysql+mysqlconnector://root@localhost/db_python"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=50), unique=True, index=True)
    email = Column(String(length=60), unique=True, index=True)
    hashed_password = Column(String(length=60))
    role = Column(String(length=60), default="user")


class CapturedImage(Base):
    __tablename__ = 'captured_images'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(length=255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ScheduleCapture(Base):
    __tablename__ = 'schedule_captures'
    id = Column(Integer, primary_key=True, index=True)
    interval = Column(Integer)
    times = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ImagePrediction(Base):
    __tablename__ = "image_predictions"
    id = Column(Integer, primary_key=True, index=True)
    plant_name = Column(String(255))  # Specify the length here
    disease = Column(String(255))  # Specify the length here
    growth_stage = Column(String(255))  # Specify the length here
    captured_image_id = Column(Integer, ForeignKey("captured_images.id"))


Base.metadata.create_all(bind=engine)
