import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import lxml
import re
import time
import csv

# Define headers for HTTP requests
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/131.0.0.0 Safari/537.36",
}


def setup_driver():
    """
    Configure and return a Selenium WebDriver instance.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('detach', False)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def navigate_to_url(driver, url):
    """
    Navigate the driver to the specified URL.
    """
    driver.get(url)
    time.sleep(2)  # Wait for the page to load


def format_data_csv (entries):
    cleaned_entries = []
    for entry in entries:
        # Remove commas between characters and format into proper county names
        cleaned_entry = ''.join(entry.split(',')).strip()  # Remove all commas and whitespace
        # Ensure the correct format (county name, County)
        if 'County' not in cleaned_entry:
            cleaned_entry += ', County'
        cleaned_entries.append(cleaned_entry)
    return cleaned_entries

def get_pagination_links(driver):
    """
    Retrieve all pagination links on the page.
    """
    pagination = driver.find_element(By.ID, 'content_table_paginate')
    pagination_buttons = pagination.find_elements(By.TAG_NAME, 'a')
    print("Pagination buttons ------------------------")
    print(pagination_buttons)
    page_href = [button.get_attribute('href') for button in pagination_buttons]
    print(page_href)
    return [button.get_attribute('href') for button in pagination_buttons]


def scrape_table_data(page_source):
    """
    Parse the page source and extract data from specified tables.
    """
    soup = BeautifulSoup(page_source, 'lxml')
    tables = soup.find_all('table', class_="table_a smpl_tbl")

    county_names = []
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            for cell in cells:
                links = cell.find_all('a')
                for link in links:
                    county_names.append(link.text.strip())
    return county_names


def clean_data(entries):
    """
    Clean and normalize the extracted data.
    """
    return [re.sub(r"^Drilling Permits in |, TX$", "", entry) for entry in entries]


def main():
    # Initialize Selenium WebDriver
    driver = setup_driver()

    try:
        url = 'https://www.texas-drilling.com/drilling-permits'
        navigate_to_url(driver, url)

        # Retrieve and navigate through pagination links
        pagination_links = get_pagination_links(driver)

        all_county_names = []
        page_count = 1  # Track page number

        for link in pagination_links:
            print(f"Navigating to Page {page_count}: {link}")
            navigate_to_url(driver, link)

            # Scrape data for the current page
            county_names = scrape_table_data(driver.page_source)
            cleaned_entries = clean_data(county_names)

            # Log the number of entries for the current page
            print(f"Page {page_count} has {len(cleaned_entries)} items.")

            all_county_names.extend(cleaned_entries)

            page_count += 1

        # Display total data collected
        print(all_county_names)
        print(f"Total cleaned entries across all pages: {len(all_county_names)}")
        csv_filename = 'all_counties_available.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            formatted_data = format_data_csv(all_county_names)
            for county in formatted_data:
                writer.writerow([county])  # Write each county name as a single row

    finally:
        driver.quit()  # Ensure the driver is closed properly


# Ensure the driver is closed properly


if __name__ == "__main__":
    main()
