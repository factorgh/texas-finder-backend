
import requests
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from utils import create_dynamic_url  # Assuming this function exists in your utils



def login_to_site(driver, login_url, email, password):
    """
    Log in to the website before scraping.
    """
    driver.get(login_url)  # Open login page
    time.sleep(2)  # Wait for the page to load

    # Wait for the email input field to be visible
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'email'))
    )

    # Find the username and password input fields and enter the credentials
    email_field = driver.find_element(By.ID, 'email')  # Update with actual selector
    password_field = driver.find_element(By.ID, 'password')  # Update with actual selector

    email_field.send_keys(email)
    password_field.send_keys(password)

    # Find and click the login button
    login_button = driver.find_element(By.CSS_SELECTOR, '.btn_a')  # Update with actual selector
    driver.execute_script("arguments[0].click();", login_button)

    time.sleep(3)  # Wait for login to process


def setup_driver():
    """
    Configure and return a Selenium WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('detach', False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def navigate_to_url(driver, url):
    """
    Navigate the driver to the specified URL.
    """
    driver.get(url)
    time.sleep(2)  # Wait for the page to load

def get_pagination_links(driver):
    """
    Retrieve all pagination links on the page.
    """
    try:
        pagination = driver.find_element(By.ID, 'content_table_paginate')
        pagination_buttons = pagination.find_elements(By.TAG_NAME, 'a')
        page_href = [button.get_attribute('href') for button in pagination_buttons]
        return page_href
    except Exception as e:
        print(f"Error in retrieving pagination links: {e}")
        return []  # Return an empty list if pagination is not found

def scrape_table_data(page_source):

    """
    Parse the page source and extract data from specified tables.
    """
    soup = BeautifulSoup(page_source, 'html.parser')

    table = soup.find('table', class_='table_a smpl_tbl')

    #
    if table:  # Ensure the table exists
        data = []  # To hold the extracted rows

        # Find all table rows (<tr>)
        for row in table.find('tbody').find_all('tr'):
            # Extract data from each cell (<td>)
            cells = row.find_all('td')
            api_number = cells[0].get_text(strip=True)
            well_name = cells[1].get_text(strip=True)
            well_type = cells[2].get_text(strip=True)
            completion_date = cells[3].get_text(strip=True)
            status = cells[4].get_text(strip=True)
           
            data.append([api_number, well_name,well_type,completion_date,status ])

        return data



def save_to_csv(data, county_name, folder_name):
    """
    Save the extracted data to a CSV file inside the specified folder.
    """
    # Create a dynamic filename using the county name
    csv_filename = os.path.join(folder_name, f"{county_name}-permit.csv")
    print(csv_filename)

    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['api_number', 'well_name','well_type','completion_date','status'])  # Header
        writer.writerows(data)  # Write the extracted rows

    print(f"Data for {county_name} saved to {csv_filename}")

def create_folder(folder_name):
    """
    Create a folder if it doesn't already exist.
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def read_and_process_csv(input_filename):
    leases_list = []
    # Read the data from the input CSV file
    with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            county = row[0].strip()  # Get the county name from the first column
            if county:  # Make sure it's not empty
                # Process the county name: lowercase and replace spaces with dashes
                formatted_county = county.lower().replace(' ', '-')
                leases_list.append(formatted_county)
    return leases_list

def scrape_and_save_wells():
    counties_filename = 'all_counties_available.csv'  # The CSV containing the county names
    all_available_counties = read_and_process_csv(counties_filename)

    # Create the folder to store the CSV files
    folder_name = 'total_counties_drilling_permits'
    create_folder(folder_name)

    # Set up the driver
    driver = setup_driver()

    # Step 1: Log in before scraping
    login_url = "https://www.texas-drilling.com/login" 
    email = "mmcgovern@latitudeliquids.com"
    password = "93827MYtre"
    login_to_site(driver, login_url, email, password)

    # Loop through all counties and scrape data
    for county_url in all_available_counties:
        print(f"Starting scrape for {county_url}...")
        # Step 1: Fetch the initial page for each county
        url = create_dynamic_url(county_url) 
        navigate_to_url(driver, url)

        # Step 2: Scrape data from multiple pages if pagination exists
        all_data = []
        page_count = 1

        while True:
            print(f"Scraping page {page_count}...")
            page_data = scrape_table_data(driver.page_source)
            all_data.extend(page_data)

            # Check for pagination and move to next page if exists
            pagination_links = get_pagination_links(driver)
            if pagination_links and len(pagination_links) > page_count:
                next_page_url = pagination_links[page_count]  # Get next page URL
                navigate_to_url(driver, next_page_url)  # Navigate to the next page
                page_count += 1
            else:
                break  # No more pages, exit the loop

        # Step 3: Save the data for this county
        county_name = county_url.replace('-', ' ').title()  # Format the county name back (e.g., "Anderson County")
        save_to_csv(all_data, county_name, folder_name)

    driver.quit()  # Close the Selenium WebDriver

if __name__ == "__main__":
    scrape_and_save_wells()



