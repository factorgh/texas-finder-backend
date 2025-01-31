from sqlalchemy.orm import Session
from database import County, Lease, Operator, Permit
from sqlalchemy.exc import IntegrityError  
import database
from final_counties import final_counties

def insert_counties_operators_leases(db: Session, data: dict):
    print('---------------------------------------------------------------------Insert Counties------------------------------------------')
    print(data)
    for county_name, county_data in data.items():
        # Insert the county (skip if it already exists)
        county = db.query(County).filter(County.name == county_name).first()
        if not county:
            county = County(name=county_name)
            db.add(county)
            try:
                db.commit()
                db.refresh(county)
            except IntegrityError:
                db.rollback()  # Rollback in case of integrity issues
                continue  # Skip to the next county

        # Insert operators
        for operator_data in county_data.get('operators', []):
            operator = Operator(
                operator_name=operator_data['Operator Name'],
                operator_number=operator_data['Operator Number'],
                location=operator_data['Location'],
                leases_number=operator_data['Leases'],
                county_id=county.id,
            )
            db.add(operator)
            try:
                db.commit()
                db.refresh(operator)
            except IntegrityError:
                    db.rollback()
            continue  # Skip to next operator

        # Insert leases
        for lease_data in county_data.get('leases', []):
            lease = Lease(
                lease_number=lease_data['Lease Number'],
                lease_name=lease_data['Lease Name'],
                operator_name=lease_data['Operator Name'],
                county_id=county.id,
            )
            print('--------------------------------data before db--------------------------------')
            print(lease)
            db.add(lease)
            try:
                db.commit()
                db.refresh(lease)
            except IntegrityError:
                db.rollback()
            continue  # Skip to the next lease

        # Insert permits if they exist
        for permit_data in county_data.get('permits', []):
            permit = Permit(
                api=permit_data['api'],
                well=permit_data['well'],
                operator=permit_data['operator'],
                application_type=permit_data['application_type'],
                drill_type=permit_data['drill_type'],
                submitted=permit_data['submitted'],
                approved=permit_data['approved'],
                county_id=county.id
            )
            print('--------------------------------data before db--------------------------------')
            print(permit)
            db.add(permit)
            
            try:
                db.commit()
                db.refresh(permit)
            except IntegrityError:
                db.rollback()
                continue  # Skip to the next permit
            
    return {"status": "success"}

# Example data insertion call
data = {
    'Wise': {
        'leases': [
            {'Lease Number': '623073', 'Lease Name': '1849 ENERGY PARTNERS OPRTNG, LLC', 'Operator Name': 'Fort Worth, TX 76107', 'Lease Link': 'https://www.texas-drilling.com/operators/1849-energy-partners-oprtng-llc/623073'},
            {'Lease Number': '623082', 'Lease Name': '1849 ENERGY PARTNERS, LLC', 'Operator Name': 'Fort Worth, TX 76107', 'Lease Link': 'https://www.texas-drilling.com/operators/1849-energy-partners-llc/623082'},
        ],
        'operators': [
            {'Operator Number': '035430', 'Operator Name': 'ASPEN OPERATING COMPANY, L.L.C.', 'Location': 'Fort Worth, TX 76116', 'Leases': '3'},
            {'Operator Number': '034380', 'Operator Name': 'ASHFORD OIL & GAS COMPANY', 'Location': 'Houston, TX 77282', 'Leases': ''},
        ],
        'permits': [
            {'api': '42-317-46279', 'well': 'BUTCH CASSIDY 43-7 UNIT 1 113JM', 'operator': 'ENDEAVOR ENERGY RESOURCES L.P.', 'application_type': 'New Drill', 'drill_type': 'Horizontal', 'submitted': '2024-10-08', 'approved': '2024-10-11'}, 
            {'api': '42-317-46281', 'well': 'BUTCH CASSIDY 43-7 UNIT 1 122LS', 'operator': 'ENDEAVOR ENERGY RESOURCES L.P.', 'application_type': 'New Drill', 'drill_type': 'Horizontal', 'submitted': '2024-10-08', 'approved': '2024-10-11'}, 
        ]
    }
}

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = next(get_db())

# db is your SQLAlchemy session

for county_name, county_info in final_counties.items(): 
    insert_counties_operators_leases(db, {county_name: county_info}) 

    

