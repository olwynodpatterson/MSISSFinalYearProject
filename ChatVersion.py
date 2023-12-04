import requests
from bs4 import BeautifulSoup
import os
import time
import random

# Function to retrieve a list of tickers from a given URL
def get_ticker_list(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tickers = response.text.splitlines()
        return tickers
    else:
        raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")

# Function to choose a random CIK (Central Index Key) from the list of tickers
def choose_random_cik(tickers):
    ticker, cik = random.choice(tickers).split('\t')
    return cik

def get_10k_filing_urls(cik):
    time.sleep(3)
    # Fetch the URLs for 10-K filings
    filings_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=exclude&count=10"
    #print(filings_url)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(filings_url, headers=headers)
    if response.status_code != 200:
        print("Error fetching filings:", response.status_code)
        return None 

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='tableFile2')
    if not table:
        return None

    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 1:
            documents_page_link = 'https://www.sec.gov' + cols[1].a['href']
            submission_text_file_link = documents_page_link.replace('-index.htm', '.txt')
            return submission_text_file_link  # Return the first link found

    return None

def download_file(url, cik, folder='10k_filings'):
    # Download the file from the given URL
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Set the file path using the CIK
    file_path = os.path.join(folder, f'{cik}_10k_form.txt')

    # Make a request to download the file
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def main():
    url = 'https://www.sec.gov/include/ticker.txt'
    tickers = get_ticker_list(url)
    cik = 320193 #choose_random_cik(tickers)
    print(f"Selected CIK: {cik}")

    filing_url = get_10k_filing_urls(cik)
    print(f"Filing URL: {filing_url}")
    if filing_url:
        download_file(filing_url, cik)
        time.sleep(1)  # Respectful delay between requests
    else:
        print(f"No 10-K filings found for CIK {cik}.")

if __name__ == "__main__":
    main()
