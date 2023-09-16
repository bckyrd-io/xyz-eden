# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define your MySQL database URL without a password (assuming no password)
# Replace the placeholders with your MySQL database credentials and database name
DATABASE_URL = "mysql+mysqlconnector://root@localhost/db_python"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
