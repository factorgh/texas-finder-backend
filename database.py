from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Optional
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
load_dotenv()


password_env = os.environ["REMOTE_PASS"]
user= os.environ["REMOTE_USER"]
host= os.environ["REMOTE_HOST"]

# # SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://databases_aziz:{password}@databases.adroit360.com/databases_texas"

# # Database connection
# DATABASE_URL = f"mysql+mysqlconnector://root:{password}@localhost:3306/databases_texas"
# # Encode password safely
password = quote_plus(password_env)

# ✅ Correct database URL (Remove https://)
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/databases_texas"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
try:
    with engine.connect() as connection:
        print("✅ Successfully connected to the remote database!")
except Exception as e:
    print("❌ Failed to connect:", str(e))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
