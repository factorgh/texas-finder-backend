from database import Base
from sqlalchemy import  Column, Integer, String, ForeignKey,Boolean
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
    lease_number = Column(String(100), nullable=True)  
    lease_name = Column(String(255), nullable=True)
    operator_name = Column(String(255), nullable=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=True)
    county = relationship("County", back_populates="leases")

    
class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_name = Column(String(255), nullable=True) 
    operator_number = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True) 
    leases_number = Column(String(255), nullable=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=True)
    county = relationship("County", back_populates="operators")
    
class Permit(Base):
    __tablename__ = "permits"

    id = Column(Integer, primary_key=True, index=True)
    api = Column(String(255), nullable=True)
    well = Column(String(255),  nullable=True)
    operator = Column(String(255),  nullable=True)
    application_type = Column(String(255),  nullable=True)
    drill_type = Column(String(255),  nullable=True)
    submitted = Column(String(255),  nullable=True)
    approved = Column(String(255),  nullable=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=True)
    county = relationship("County", back_populates="permits")
    


# User and Subscription section



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    contact = Column(String(255), nullable=True)
    services = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    is_subscribed = Column(Boolean, default=False)
    subscription_status = Column(String(50), default="inactive")  # ✅ Track status

    subscriptions = relationship("Subscription", back_populates="user", uselist=False)  # ✅ One-to-one

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # ✅ One subscription per user
    stripe_subscription_id = Column(String(255), nullable=True)  # Nullable because it's not always available at checkout
    checkout_session_id = Column(String(255),nullable=False)  # ✅ Store checkout session ID
    status = Column(String(255), default="inactive")

    user = relationship("User", back_populates="subscriptions")



