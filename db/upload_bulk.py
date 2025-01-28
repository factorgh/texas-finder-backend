from db import final_counties  

from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")  # Replace with your connection string
db = client.counties_database  # Replace with your database name

counties_collection = db.counties  # Collection for counties

# Prepare data for MongoDB
counties_data = []
for county_key, county_value in final_counties.items():
    # Extract and clean county name
    county_name = county_key.replace("-leases", "").strip()

    # Extract leases, operators, and permits
    leases = county_value.get('leases', [])
    operators = county_value.get('operators', [])
    permits = county_value.get('permits', [])

    formatted_leases = [
        {
            "lease_number": lease.get("Lease Number"),
            "lease_name": lease.get("Lease Name"),
            "operator_name": lease.get("Operator Name"),
            "lease_link": lease.get("Lease Link"),
        }
        for lease in leases
    ]

    formatted_operators = [
        {
            "operator_number": operator.get("Operator Number"),
            "operator_name": operator.get("Operator Name"),
            "location": operator.get("Location"),
            "leases": operator.get("Leases"),
        }
        for operator in operators
    ]

    formatted_permits = [
        {
            "api": permit.get("api"),
            "well": permit.get("well"),
            "operator": permit.get("operator"),
            "application_type": permit.get("application_type"),
            "drill_type": permit.get("drill_type"),
            "submitted": permit.get("submitted"),
            "approved": permit.get("approved"),
        }
        for permit in permits
    ]

    counties_data.append({
        "name": county_name,
        "leases": formatted_leases,
        "operators": formatted_operators,
        "permits": formatted_permits,
    })

# Insert data into MongoDB
try:
    counties_collection.delete_many({})  # Clear existing data
    result = counties_collection.insert_many(counties_data)
    print(f"Inserted {len(result.inserted_ids)} counties.")
except Exception as e:
    print(f"Error inserting data: {e}")
