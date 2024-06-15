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
        csv_writer.writerow(["Links"])

        for link in links:
            csv_writer.writerow([link])

def extract_specific_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # difference between raise_for_status and status_code

        soup = BeautifulSoup(response.text, 'html.parser')

        #skip extraction for social media URLs
        if is_social_media_url(url):
            print(f"Skipping {url} because it's a social media link.")
            return None, None, None, None, None, None #include original link as none

        heading_element = soup.find('h1', {'style': 'margin-bottom:0.1rem;'})
        author_element = soup.find('h5', class_='text-capitalize')
        publication_date_element = soup.find('div', class_='updated_time')
        content_container = soup.find('div', class_='subscribe--wrapperx')

        #Determine category based on URL
        url_parts = urlparse(url).path.split('/')
        category = next((part for part in url_parts if part), 'Category not found')

        heading = heading_element.text.strip() if heading_element else 'Heading not found'
        author = author_element.text.strip() if author_element else 'Author not found'
        publication_date_raw = publication_date_element.text.strip() if publication_date_element else 'Publication date not found'
        publication_date = publication_date_raw.replace('Published at :','').strip()
        content = content_container.get_text(separator=' ', strip=True) if content_container else 'Content not found'

        return category, heading, author, publication_date, content

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve content from {url}. Error: {e}")
        return None, None, None, None, url, None #Include original link and None for others

def save_to_csv(data, csv_file_path):
    with open(csv_file_path, 'a', newline='', encoding='uft-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Category', 'Heading', 'Author', 'Publication_date', 'Source', 'Content'])
        csv_writer.writerow(data)

def main():
    csv_file_path = 'kathmandupost.csv'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Category', 'Heading', 'Author', 'Publication_date', 'Source', 'Content'])

    url = 'https://kathmandupost.com'
    links = extract_all_links(url)

    # Save links to CSV file
    csv_filename = 'datalinks.csv'
    save_links_to_csv(links,csv_filename)

    #Print a message indicating success
    print(f"Links extracted and saved to {csv_filename}.")

    for url in links:
        if not urlparse(url).scheme:
            url=urljoin('https://', url)

        if urlparse(url).netloc and not is_social_media_url(url):
            heading, author, publication_date, content, link, category = extract_specific_content(url)
            if heading is not None and author is not None and content is not None:
                data_to_save = [category, heading, author, publication_date, 'Kathmandu-Post', content, link]
                print(f"Data for {url}: \nHeading: {heading}\nAuthor{author}\nPublication Date: {publication_date}\SOurce: Kathmandu-Post \nContent: {content}\nLink{link}\nCategory: {category}")
                save_to_csv(data_to_save, csv_file_path)
                print(f"Data saved for {url}")
            else:
                print(f"Failed to extract data for {url}.")

if __name__ == "__main__":
    main()
