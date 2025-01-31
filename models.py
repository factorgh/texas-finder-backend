from database import Base
from sqlalchemy import  Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
# ✅ Fix: Add String(length) for MySQL
class County(Base):
    __tablename__ = "counties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)  # ✅ Added length

    leases = relationship("Lease", back_populates="county")
    operators = relationship("Operator", back_populates="county")
    permits = relationship("Permit",back_populates="county")
    
class Lease(Base):
    __tablename__ = "leases"
    
    id = Column(Integer, primary_key=True, index=True)
    lease_number = Column(String(100), nullable=False)  
    lease_name = Column(String(255), nullable=False)
    operator_name = Column(String(255), nullable=False)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    county = relationship("County", back_populates="leases")

    
class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_name = Column(String(255), nullable=False) 
    operator_number = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False) 
    leases_number = Column(String(255), nullable=False)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    county = relationship("County", back_populates="operators")
    
class Permit(Base):
    __tablename__ = "permits"

    id = Column(Integer, primary_key=True, index=True)
    api = Column(String(255), nullable=False)
    well = Column(String(255),  nullable=False)
    operator = Column(String(255),  nullable=False)
    application_type = Column(String(255),  nullable=False)
    drill_type = Column(String(255),  nullable=False)
    submitted = Column(String(255),  nullable=False)
    approved = Column(String(255),  nullable=False)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    county = relationship("County", back_populates="permits")
    


