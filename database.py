from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Optional

# Setup SQLAlchemy engine and session for MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/mydatabase"  # Replace with your MySQL DB URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define models (County, Lease, Operator)
class County(Base):
    __tablename__ = "counties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    leases = relationship("Lease", back_populates="county")
    
class Lease(Base):
    __tablename__ = "leases"
    
    id = Column(Integer, primary_key=True, index=True)
    lease_number = Column(String)
    lease_name = Column(String)
    lease_link = Column(String)
    operator_name = Column(String, ForeignKey("operators.name"))
    
    county_id = Column(Integer, ForeignKey("counties.id"))
    county = relationship("County", back_populates="leases")
    
class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    
    leases = relationship("Lease", back_populates="operator")

# Create the tables if they don't exist
Base.metadata.create_all(bind=engine)
