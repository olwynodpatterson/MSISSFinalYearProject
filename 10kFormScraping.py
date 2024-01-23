import requests
from bs4 import BeautifulSoup
import os
import time
import random

# Function to retrieve a list of tickers from a given URL
def get_ticker_list(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        tickers = response.text.splitlines()
        return tickers
    else:
        # Raise an exception if the request failed
        raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")

# Function to choose a random CIK (Central Index Key) from the list of tickers
def choose_random_cik(tickers):
    # Choose a random ticker and associated CIK
    ticker, cik = random.choice(tickers).split('\t')
    return cik

# Function to get the URLs of 10-K filings for a given CIK
def get_10k_filing_urls(cik):
    time.sleep(3) # Delay to avoid overwhelming the server
    # Fetch the URLs for 10-K filings
    filings_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=exclude&count=10"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(filings_url, headers=headers)
    # Check response status
    if response.status_code != 200:
        print("Error fetching filings:", response.status_code)
        return None 

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='tableFile2')
    if not table:
        return None

    # Parse the table to get the filing links
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 1:
            documents_page_link = 'https://www.sec.gov' + cols[1].a['href']
            submission_text_file_link = documents_page_link.replace('-index.htm', '.txt')
            return submission_text_file_link  # Return the first link found

    return None

def dehtml(html_content):
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract text from the parsed HTML
    text = soup.get_text()

    return text

# Function to download a file from a given URL
def download_file(url, cik, folder='10k_filings'):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Set the file path using the CIK
    html_file_path = os.path.join(folder, f'{cik}_10k_form.html')
    text_file_path = os.path.join(folder, f'{cik}_10k_form.txt')

    # Make a request to download the file
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(html_file_path, 'wb') as html_file:
            for chunk in response.iter_content(chunk_size=8192):
                html_file.write(chunk)
        print(f"Downloaded HTML: {html_file_path}")

        # Read the HTML content
        with open(html_file_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()

        # Convert HTML to plain text
        plain_text = dehtml(html_content)

        # Save the plain text
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(plain_text)
        print(f"Converted to Text: {text_file_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

# Main function to drive the program
def main():
    url = 'https://www.sec.gov/include/ticker.txt'
    tickers = get_ticker_list(url)
    i=0
    while i <2:
        cik =  choose_random_cik(tickers) 
        print(f"Selected CIK: {cik}")
        filing_url = get_10k_filing_urls(cik)
        print(f"Filing URL: {filing_url}")
        if filing_url:
            download_file(filing_url, cik)
            time.sleep(1)  # Respectful delay between requests
            i += 1
        else:
            print(f"No 10-K filings found for CIK {cik}.")

if __name__ == "__main__":
    main()
    
