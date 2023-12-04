import requests
import time
import os
from bs4 import BeautifulSoup
import random

# Function to retrieve a list of tickers from a given URL
def get_ticker_list(url):
    headers = {'User-Agent': 'Mozilla/5.0'}# Set a user-agent to mimic a web browser (some websites block non-browser requests)
    response = requests.get(url, headers=headers)# Make an HTTP GET request to the specified URL
    # Check if the request was successful
    if response.status_code == 200:
        tickers = response.text.splitlines()# Split the response text by new lines and return the list of tickers
        return tickers
    else:
        # Raise an exception if the request failed
        raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")

# Function to choose a random CIK (Central Index Key) from the list of tickers
def choose_random_cik(tickers):
    # Randomly choose a ticker and its associated CIK (assumes they are separated by a tab)
    ticker, cik = random.choice(tickers).split('\t')
    return cik

# Function to retrieve 10-K forms for a given CIK
def get_10k_forms(cik):
    print(cik)
    time.sleep(10)
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar" # Base URL for the SEC EDGAR database
    headers = {'User-Agent': 'Mozilla/5.0'} # Again, set a user-agent header for the request
    # Parameters for the SEC API request
    params = {
        'action': 'getcompany',
        'CIK': cik,
        'type': '10-K',
        'dateb': '',
        'output': 'html',
        'count': 40  # Number of results, adjust as needed
    }

    # Make the HTTP GET request with the specified parameters
    response = requests.get(base_url, headers=headers, params=params)
    print(response.text)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve 10-K forms. Status code: {response.status_code}")

    # Use Beautiful Soup to parse the initial response
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the link to the 10-K document
    doc_link = None
    for link in soup.find_all('a'):
        print('Got to soup.find(a)')
        if link.text == 'Documents':
            doc_link = 'https://www.sec.gov' + link.get('href')
            print(doc_link)
            break

    if not doc_link:
        raise Exception("Failed to find the link to the 10-K document.")
        return None

    # Fetch the 10-K document
    doc_response = requests.get(doc_link, headers=headers)
    if doc_response.status_code != 200:
        raise Exception(f"Failed to retrieve the 10-K document. Status code: {doc_response.status_code}")

    # Parse the 10-K document content
    doc_soup = BeautifulSoup(doc_response.text, 'html.parser')

    # Extract the text content or structured content as needed
    # This step depends on the structure of the 10-K document page
    # For example, if the content is in a <pre> tag:
    report_content = doc_soup.find('pre').text if doc_soup.find('pre') else doc_soup.text

    return report_content

# Main execution block
if __name__ == '__main__':  # Ensure this code runs only when the script is executed directly
    # Directory where files will be saved
    save_dir = '/content/10k_reports'
    os.makedirs(save_dir, exist_ok=True)
    # URL for the ticker list
    ticker_url = 'https://www.sec.gov/include/ticker.txt'

    for i in range(5):
        attempts = 0
        while True:
            try:
                tickers = get_ticker_list(ticker_url)# Retrieve the list of tickers from the SEC website
                cik = 320193 #choose_random_cik(tickers)
                forms_data = get_10k_forms(cik)

                if forms_data is not None:
                    file_path = os.path.join(save_dir, f'{cik}_10k_form.txt')
                    with open(file_path, 'w') as file:
                        file.write(forms_data)
                    print(f"Saved 10-K form for CIK {cik} to {file_path}")
                    break  # Break the while loop if successful
                else:
                    print(f"No 10-K form found for CIK {cik}, trying another.")
                    attempts += 1
                    if attempts >= 3:  # Limit the number of attempts per ticker
                        print("Maximum attempts reached, moving to next CIK.")
                        break

            except Exception as e:
                print(f"An error occurred for CIK {cik}: {e}")
                attempts += 1
                if attempts >= 3:  # Limit the number of attempts per ticker
                    print("Maximum attempts reached, moving to next CIK.")
                    break