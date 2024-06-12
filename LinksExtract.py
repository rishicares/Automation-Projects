import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd

def is_social_media_url(url):
    social_media_domains = ['twitter.com', 'facebook.com', 'instagram.com'] #Add more if needed
    for domain in social_media_domains:
        if domain in url:
            return True
    return False

def extract_all_links(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract all links using BeautifulSoup methods
            links = [a['href'] for a in soup.find_all('a', href=True)]

            # Convert relative URLs to absolute URLs
            links = [urljoin(url, link) for link in links]

            return links
        else:
            print(f"Failed to retrieve data from '{url}'. Status code: {response.status_code}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return []

def save_links_to_csv(links, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Link'])

    for link in links:
        csv_writer.writerow([link])

def extract_specific_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        #skip extraction for social medaia URLs
        if is_social_media_url(url):
            print(f"Skipping {url} because it's a social media link.")
            return None, None, None, None, None, None #include original link as none

        heading_element = soup.find('h1', {'style': 'margin-bottom:0.1rem;'})
        author_element = soup.find('h5', class_='text-capitalize')
        publication_date_element = soup.find('div', class_='updated_time')
        content_element = soup.find('div', class_='subscribe--wrapperx')
