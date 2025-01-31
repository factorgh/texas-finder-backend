from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Optional
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
load_dotenv()


password_env = os.environ["LOCAL_PASS"]
user= os.environ["LOCAL_USER"]

# # SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://databases_aziz:{password}@databases.adroit360.com/databases_texas"

# # Database connection
# DATABASE_URL = f"mysql+mysqlconnector://root:{password}@localhost:3306/databases_texas"
# # Encode password safely
password = quote_plus(password_env)

# ✅ Correct database URL (Remove https://)
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@localhost:3306/databases_texas"

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

# # ✅ Fix: Add String(length) for MySQL
# class County(Base):
#     __tablename__ = "counties"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), unique=True, index=True, nullable=False)  # ✅ Added length

#     leases = relationship("Lease", back_populates="county")
#     operators = relationship("Operator", back_populates="county")
#     permits = relationship("Permit",back_populates="county")
    
# class Lease(Base):
#     __tablename__ = "leases"
    
#     id = Column(Integer, primary_key=True, index=True)
#     lease_number = Column(String(100), nullable=False)  
#     lease_name = Column(String(255), nullable=False)
#     operator_name = Column(String(255), nullable=False)
#     county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
#     county = relationship("County", back_populates="leases")

    
# class Operator(Base):
#     __tablename__ = "operators"
    
#     id = Column(Integer, primary_key=True, index=True)
#     operator_name = Column(String(255), nullable=False)  # Removed `unique=True`
#     operator_number = Column(String(255), nullable=False)  # Removed `unique=True`
#     location = Column(String(255), nullable=False) 
#     leases_number = Column(String(255), nullable=False)
#     county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
#     county = relationship("County", back_populates="operators")
    
# class Permit(Base):
#     __tablename__ = "permits"

#     id = Column(Integer, primary_key=True, index=True)
#     api = Column(String(255), nullable=False)
#     well = Column(String(255),  nullable=False)
#     operator = Column(String(255),  nullable=False)
#     application_type = Column(String(255),  nullable=False)
#     drill_type = Column(String(255),  nullable=False)
#     submitted = Column(String(255),  nullable=False)
#     approved = Column(String(255),  nullable=False)
#     county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
#     county = relationship("County", back_populates="permits")
    
# # ✅ Fix: Create tables properly
# Base.metadata.create_all(bind=engine)
