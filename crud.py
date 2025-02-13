from sqlalchemy.orm import Session,noload,load_only
from schemas import CountyCreate, LeaseCreate, OperatorCreate
from models import County, Lease, Operator
from sqlalchemy.orm import selectinload
# Create functions
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

# Get all functions@app.get("/counties")


def get_counties(db: Session):
    return db.query(County).options(
        noload(County.leases),
        noload(County.operators),
        noload(County.permits),
        load_only(County.id, County.name)
    ).all()
def get_operators(db: Session):
    return db.query(Operator).all()



def get_leases(db: Session, county_id: int, operator_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(Lease)
        .filter(Lease.county_id == county_id, Lease.operator_id == operator_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# Get by ID functions
def get_county_by_id(db: Session, county_id: int):
    return db.query(County).filter(County.id == county_id).first()

def get_operator_by_id(db: Session, operator_id: int):
    return db.query(Operator).filter(Operator.id == operator_id).first()

def get_lease_by_id(db: Session, lease_id: int):
    return db.query(Lease).filter(Lease.id == lease_id).first()
