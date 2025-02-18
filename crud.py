from sqlalchemy.orm import Session,noload,load_only
from schemas import CountyCreate, LeaseCreate, OperatorCreate
from models import County, Lease, Operator,Permit
from sqlalchemy.orm import selectinload
from sqlalchemy import func,or_
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


def get_counties(db: Session):
    return db.query(County).options(
        noload(County.leases),
        noload(County.operators),
        noload(County.permits),
        load_only(County.id, County.name)
    ).all()
def get_operators(db: Session):
    return db.query(Operator).all()


def get_leases(db: Session, county_id: int, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(Lease).filter(Lease.county_id == county_id)

    if search:
        query = query.filter(
            or_(
                Lease.lease_name.ilike(f"%{search}%"),  # ✅ Case-insensitive search in lease name
                Lease.operator_name.ilike(f"%{search}%")  # ✅ Also search in operator name
            )
        )

    total = query.count()
    leases = query.offset(skip).limit(limit).all()

    return {"total": total, "leases": leases}

def get_operators(db: Session, county_id: int, skip: int = 0, limit: int = 10,search: str = None):
    query = db.query(Operator).filter(Operator.county_id == county_id) # ✅ Count total records

    if search:
        query = query.filter(Operator.operator_name.ilike(f"%{search}%"))  # ✅ Case-insensitive search

    total = query.count()  # ✅ Count total records after filtering
    operators = query.offset(skip).limit(limit).all()  # ✅ Get operators count

    return { "operators": operators}



def get_permits(db: Session, county_id: int, skip: int = 0, limit: int = 50, search: str = None):
    query = db.query(Permit).filter(Permit.county_id == county_id)

    if search:
        query = query.filter(Permit.operator.ilike(f"%{search}%"))  # Adjust field as needed

    total = query.count()  # ✅ Get total permits count
    permits = query.offset(skip).limit(limit).all()

    return {"total": total, "permits": permits}  # ✅ Return total & data


# Get by ID functions
def get_county_by_id(db: Session, county_id: int):
    return db.query(County).filter(County.id == county_id).first()

def get_operator_by_id(db: Session, operator_id: int):
    return db.query(Operator).filter(Operator.id == operator_id).first()

def get_lease_by_id(db: Session, lease_id: int):
    return db.query(Lease).filter(Lease.id == lease_id).first()

# Function to get the top 10 counties by number of operators
def get_top_counties_by_operators(db: Session):
    result = (
        db.query(County.id, County.name, func.count(Operator.id).label("operator_count"))
        .join(Operator, Operator.county_id == County.id)
        .group_by(County.id, County.name)
        .order_by(func.count(Operator.id).desc())
        .limit(10)
        .all()
    )

    # Convert the result to a list of dictionaries to make it JSON serializable
    return [
        {"county_id": county_id, "county_name": county_name, "operator_count": operator_count}
        for county_id, county_name, operator_count in result
    ]


# Function to get the top 10 counties by number of leases
def get_top_counties_by_leases(db: Session):
    result = (
        db.query(County.id, County.name, func.count(Lease.id).label("lease_count"))
        .join(Lease, Lease.county_id == County.id)
        .group_by(County.id, County.name)
        .order_by(func.count(Lease.id).desc())
        .limit(10)
        .all()
    )

    # Convert the result to a list of dictionaries to make it JSON serializable
    return [
        {"county_id": county_id, "county_name": county_name, "lease_count": lease_count}
        for county_id, county_name, lease_count in result
    ]

# Function to get the top 10 counties by number of permits
def get_top_counties_by_permits(db: Session):
    result = (
        db.query(County.id, County.name, func.count(Permit.id).label("permit_count"))
        .join(Permit, Permit.county_id == County.id)
        .group_by(County.id, County.name)
        .order_by(func.count(Permit.id).desc())
        .limit(10)
        .all()
    )

    # Convert the result to a list of dictionaries to make it JSON serializable
    return [
        {"county_id": county_id, "county_name": county_name, "permit_count": permit_count}
        for county_id, county_name, permit_count in result
    ]
