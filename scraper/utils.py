# import csv
#
# def read_and_process_csv(input_filename, output_filename):
#     counties_list = []
#
#     # Read the data from the input CSV file
#     with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
#         reader = csv.reader(infile)
#         for row in reader:
#             county = row[0].strip()  # Get the county name from the first column
#             if county:  # Make sure it's not empty
#                 # Process the county name: lowercase and replace spaces with dashes
#                 formatted_county = county.lower().replace(' ', '-')
#                 counties_list.append(formatted_county)
#
#     # Optionally, write the processed counties into a new CSV or a text file
#     with open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
#         writer = csv.writer(outfile)
#         for county in counties_list:
#             writer.writerow([county])  # Write each formatted county name on a new line
#
#     return counties_list  # Return the list of counties
#
# # Specify the input and output file names
# input_filename = 'counties.csv'  # Name of your input CSV file
# output_filename = 'processed_counties.csv'  # Name of your output CSV file
#
# # Call the function
# formatted_counties = read_and_process_csv(input_filename, output_filename)
#
# # Print the formatted counties (optional)
# for county in formatted_counties:
#     print(county)


# Function to create a dynamic URL based on county name
def create_dynamic_url(county_name_dynamic):
    # Format the county name to lowercase and replace spaces with dashes
    formatted_county_name = county_name_dynamic.lower().replace(" ", "-")
    # Create the URL with the formatted county name
    url = f"https://www.texas-drilling.com/{formatted_county_name}/drilling-permits"
    return url


