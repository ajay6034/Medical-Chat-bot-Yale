import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize the Selenium webdriver (make sure to download the appropriate webdriver for your browser)
driver = webdriver.Chrome()

# Define the URLs
url1 = "https://www.ynhhs.org/find-a-doctor#q=psychiatry&sort=relevancy&numberOfResults=100&f:affiliations=[YaleMedNortheast]"
url2 = "https://www.ynhhs.org/find-a-doctor#q=psychiatry&first=100&sort=relevancy&numberOfResults=100&f:affiliations=[YaleMedNortheast]"

# Function to scrape data from a page
def scrape_doctors(url):
    driver.get(url)
    time.sleep(5)  # Adjust the sleep time as needed
    doctor_cards = driver.find_elements(By.CLASS_NAME, "doctor-card")
    doctors_data = []
    for doctor_card in doctor_cards:
        try:
            name = doctor_card.find_element(By.CLASS_NAME, "info-container").text.strip()
            doctors_data.append([name])  # Here you might want to extract more details
        except Exception as e:
            print(f"Error processing card: {e}")
    return doctors_data

# Open the first URL and scrape
doctors_info = scrape_doctors(url1)

# Open the second URL and continue scraping
doctors_info.extend(scrape_doctors(url2))

# Save all the doctor information to a CSV file
with open('doctors_info.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Name'])  # Write header row
    writer.writerows(doctors_info)  # Write all data rows

# Close the webdriver
driver.quit()