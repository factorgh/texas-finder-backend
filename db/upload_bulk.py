import json
from pymongo import MongoClient

# Load data from the JSON file
with open('final_counties.json', 'r') as file:
    final_counties = json.load(file)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")  # Replace with your connection string
db = client.counties_database  # Replace with your database name

counties_collection = db.counties  # Collection for counties
operators_collection = db.operators  # Collection for operators

# Extract data for counties and operators
counties_data = []


for county_key, county_value in final_counties.items():
    # Extract and clean county name
    county_name = county_key.replace("-leases", "").strip()
    

    # Extract leases data
    leases = county_value.get('leases', [])
    operators = county_value.get('operators', [])
    permits = county_value.get('permits', [])
    formatted_leases = []
    formatted_operators = []
    formatted_permits = [] 
    
    for lease in leases:
        lease_number = lease.get("Lease Number")
        lease_name = lease.get("Lease Name")
        operator_name = lease.get("Operator Name")
       
        
        # Append the lease data
        formatted_leases.append({
            "lease_number": lease_number,
            "lease_name": lease_name,
            "operator_name": operator_name,
    
        })
    
    for permit in permits:
        api = lease.get("api")
        well = lease.get("well")
        operator = lease.get("operator")
        application_type = permit.get("application_type")
        drill_type = permit.get("drill_type")
        submitted = permit.get("submitted")
        approved = permit.get("approved")
       
        
        # Append the lease data
        formatted_permits.append({
            "api": api,
                "well": well,
                "operator": operator,
                "application_type": application_type,
                "drill_type": drill_type,
                "submitted": submitted,
                "approved": approved,
    
        })

    for operator in operators:
        operator_number = lease.get("Operator Number")
        operator_name = lease.get("Operator Name")
        location = lease.get("Location")
        leases = lease.get("Leases")
      
       
        
        # Append the lease data
        formatted_operators.append({
            "Operator_number":operator_number,
            "operator_name": operator_name,
            "location": location,
            "leases": leases,
    
        })

        
    
    # Add the county with its formatted leases
    counties_data.append({
        "name": county_name,
        "leases": formatted_leases,
        "operators":formatted_operators,
        "permits":formatted_permits

    })

# Alphabetically sort counties
counties_data.sort(key=lambda x: x["name"])

# # Transform operator data into a list
# operators_data_list = list(operators_data.values())

# Upload to MongoDB
try:
    # Insert counties
    counties_collection.delete_many({})  # Clear existing data
    counties_result = counties_collection.insert_many(counties_data)
    print(f"Inserted {len(counties_result.inserted_ids)} counties.")

    # # Insert operators
    # operators_collection.delete_many({})  # Clear existing data
    # operators_result = operators_collection.insert_many(operators_data_list)
    # print(f"Inserted {len(operators_result.inserted_ids)} operators.")
except Exception as e:
    print(f"Error inserting data: {e}")
