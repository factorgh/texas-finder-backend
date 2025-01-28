import mysql.connector
from final_counties import final_counties

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",  # Your host, e.g., "localhost"
    user="your_user",  # Your MySQL username
    password="your_password",  # Your MySQL password
    database="counties_database"  # The database you want to use
)

cursor = db.cursor()

# Prepare the database (Ensure tables exist first, or create them)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS counties (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        leases JSON,
        operators JSON,
        permits JSON
    );
""")

# Function to prepare the lease, operator, and permit data
def format_lease_data(leases):
    return [
        (
            lease.get("Lease Number"),
            lease.get("Lease Name"),
            lease.get("Operator Name"),
            lease.get("Lease Link"),
        )
        for lease in leases
    ]

def format_operator_data(operators):
    return [
        (
            operator.get("Operator Number"),
            operator.get("Operator Name"),
            operator.get("Location"),
            operator.get("Leases"),
        )
        for operator in operators
    ]

def format_permit_data(permits):
    return [
        (
            permit.get("api"),
            permit.get("well"),
            permit.get("operator"),
            permit.get("application_type"),
            permit.get("drill_type"),
            permit.get("submitted"),
            permit.get("approved"),
        )
        for permit in permits
    ]

# Clear existing data
cursor.execute("DELETE FROM counties")

# Loop through the counties and insert data
for county_key, county_value in final_counties.final_counties.items():
    county_name = county_key.replace("-leases", "").strip()
    leases = county_value.get('leases', [])
    operators = county_value.get('operators', [])
    permits = county_value.get('permits', [])

    formatted_leases = format_lease_data(leases)
    formatted_operators = format_operator_data(operators)
    formatted_permits = format_permit_data(permits)

    # Insert the county data into MySQL
    try:
        cursor.execute("""
            INSERT INTO counties (name, leases, operators, permits)
            VALUES (%s, %s, %s, %s);
        """, (county_name, str(formatted_leases), str(formatted_operators), str(formatted_permits)))
        db.commit()
    except Exception as e:
        print(f"Error inserting data for {county_name}: {e}")

# Close the connection
cursor.close()
db.close()
print("Data insertion complete.")
