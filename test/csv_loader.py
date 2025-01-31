import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mod import Base, County, Lease, Operator, Permit  # Import models
from dotenv import load_dotenv
load_dotenv()


password = os.environ["LOCAL_PASS"]
user= os.environ["LOCAL_USER"]

# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://databases_aziz:{password}@databases.adroit360.com/databases_texas"

# Database connection
DATABASE_URL = f"mysql+mysqlconnector://root:{password}@localhost:3306/databases_texas"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Ensure tables are created
Base.metadata.create_all(engine)

# Read county names from a file
with open("all_counties.csv", "r") as f:
    county_names = [line.strip() for line in f.readlines()]  # Read and clean names

# Step 2: Function to load CSV data into tables
def load_csv_to_db(file_path, model, mappings, county_id):
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}, skipping.")
        return
    df = pd.read_csv(file_path)
    records = []
    for _, row in df.iterrows():
        data = {db_col: row[csv_col] for csv_col, db_col in mappings.items()}
        data["county_id"] = county_id  # Link to county
        records.append(model(**data))
    
    session.bulk_save_objects(records)
    session.commit()
    print(f"✅ Data from {file_path} inserted successfully.")

# Mapping CSV columns to Model fields
lease_mapping = {
    "Lease Number": "lease_number",
    "Lease Name": "lease_name",
    "Operator Name": "operator_name",
}
operator_mapping = {
    "Operator Name": "operator_name",
    "Operator Number": "operator_number",
    "Location": "location",
    "Leases": "leases_number",
}
permit_mapping = {
    "api": "api",
    "well": "well",
    "operator": "operator",
    "application_type": "application_type",
    "drill_type": "drill_type",
    "submitted": "submitted",
    "approved": "approved",
}

# Process each county
for county_name in county_names:
    formatted_name = county_name.replace(" County", "")  # Remove "County" from name

    # Step 1: Create or get the County
    county = session.query(County).filter_by(name=county_name).first()
    if not county:
        county = County(name=county_name)
        session.add(county)
        session.commit()  # Commit to get an ID for relationships
    
    # Construct file paths dynamically
    lease_file = f"total_counties_leases/{county_name}-leases.csv"
    operator_file = f"total_counties_operators/{county_name}-operators.csv"
    permit_file = f"total_counties_drilling_permits/{county_name}-permit.csv"

    # Load CSVs into the database
    load_csv_to_db(lease_file, Lease, lease_mapping, county.id)
    load_csv_to_db(operator_file, Operator, operator_mapping, county.id)
    load_csv_to_db(permit_file, Permit, permit_mapping, county.id)

print("🎉 All counties processed successfully!")

# Close session
session.close()
