import csv
import os

# Specify the directory containing the CSV files
input_folder_path = "total_counties_drilling_permits_copy"

# Derive the output Python file name
output_file_path = os.path.join(input_folder_path, "permits.py")

# Initialize a dictionary to store data, with filenames as keys
all_data = {}

# Initialize a dictionary to store the count of entries for each file
file_counts = {}

# Iterate through all files in the folder
for file_name in os.listdir(input_folder_path):
    if file_name.endswith(".csv"):  # Process only CSV files
        file_path = os.path.join(input_folder_path, file_name)
        file_key = os.path.splitext(file_name)[0]  # Use filename without extension as key

        print(f"Processing {file_name}...")  # Debugging: confirm file is being processed

        try:
            # Read data from the current CSV file
            with open(file_path, mode="r") as file:
                csv_reader = csv.DictReader(file)
                file_data = [row for row in csv_reader]  # List of rows from this file

                if file_data:
                    all_data[file_key] = file_data  # Add to dictionary with the file name as key
                    file_counts[file_key] = len(file_data)  # Store count of rows in this file
                    print(f"Added data from {file_name} ({len(file_data)} entries)")  # Debugging: show count
                else:
                    print(f"No data found in {file_name}")  # Debugging: handle empty files
                    file_counts[file_key] = 0  # Assign zero if no data
        except Exception as e:
            print(f"Error reading {file_name}: {e}")  # Error handling for issues reading files

# Write the dictionary data to the Python file
if all_data:
    with open(output_file_path, mode="w") as py_file:
        # Add a comment at the top for clarity
        py_file.write("# This file contains combined data from CSV files in the folder\n\n")
        # Write the dictionary in Python format
        py_file.write(f"data = {all_data}\n")
        py_file.write(f"\n# File data counts: {file_counts}")  # Add the file counts to the output file
    print(f"Combined dictionary data has been written to {output_file_path}")
    print("File counts:", len(file_counts))  # Print file counts to the console for debugging
else:
    print("No data to write or folder is empty.")
