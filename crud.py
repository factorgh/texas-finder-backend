from sqlalchemy.orm import Session
from .models import County, Lease, Operator
from .crud import CountyCreate, LeaseCreate, OperatorCreate

def create_county(db: Session, county: CountyCreate):
    db_county = County(name=county.name)
    db.add(db_county)
    db.commit()
    db.refresh(db_county)
    return db_county

def create_operator(db: Session, operator: OperatorCreate):
    db_operator = Operator(name=operator.name)
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator

def create_lease(db: Session, lease: LeaseCreate, county_id: int, operator_id: int):
    db_lease = Lease(
        lease_number=lease.lease_number,
        lease_name=lease.lease_name,
        lease_link=lease.lease_link,
        operator_name=lease.operator_name,
        county_id=county_id,
        operator_id=operator_id
    )
    db.add(db_lease)
    db.commit()
    db.refresh(db_lease)
    return db_lease

def get_counties(db: Session):
    return db.query(County).all()

def get_operators(db: Session):
    return db.query(Operator).all()

def get_leases(db: Session):
    return db.query(Lease).all()
