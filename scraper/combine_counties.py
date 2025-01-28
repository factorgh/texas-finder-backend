import os
import pickle  # for reading .py files (if the files are Python files)

# Specify the directory containing the dictionaries
input_folder_path = "county_dictionaries"  # This folder contains "permits", "operators", "leases"
output_file_path = "final_counties.py"

# Initialize a dictionary to store the final data with county names as keys
final_counties = {}

# Iterate through all files in the counties_dictionary folder
for file_name in os.listdir(input_folder_path):
    file_path = os.path.join(input_folder_path, file_name)

    # Check if file ends with '.py' (Python file) indicating it contains a dictionary
    if file_name.endswith(".py"):
        print(f"Processing {file_name}...")

        # Use pickle to load the dictionary data from the .py file
        try:
            with open(file_path, mode="r") as py_file:
                # Read the content of the Python file, assuming it contains a dictionary in the 'data' variable
                file_data = py_file.read()  # Read the raw content
                exec(file_data)  # Executes the file content (loads 'data' into memory)

                # Add data to final_counties, mapping it to the appropriate file key ('permits', 'operators', etc.)
                if 'data' in globals():
                    content_type = os.path.splitext(file_name)[0]  # This is 'permits', 'operators', 'leases', etc.
                    for county, details in data.items():
                        if county not in final_counties:
                            final_counties[county] = {}
                        final_counties[county][content_type] = details
                    print(f"Added data from {file_name}")
                else:
                    print(f"No data found in {file_name}")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

# Write the combined dictionary data to the output file
if final_counties:
    with open(output_file_path, mode="w") as py_file:
        # Add a comment at the top for clarity
        py_file.write("# This file contains the final combined dictionary for counties\n\n")
        # Write the dictionary in Python format
        py_file.write(f"final_counties = {final_counties}\n")
    print(f"Final dictionary has been written to {output_file_path}")
else:
    print("No data to write, the folder might be empty or something went wrong.")
