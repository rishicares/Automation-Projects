import requests
import os

# Define a function to search for photos on Flickr
def search_flickr(query, api_key, num_images=10):
    #Base URL for the Flickr API
    url = "https://api.flickr.com/services/rest/"

    #Parameters for the API request
    params = {
        "method": "flickr.photos.search",
        "api_key": api_key,
        "text": query,
        "tags": "rishikesh",
        "sort": "relevance",
        "per_page": num_images,
        "format": "json",
        "nojsoncallback": 1
    }

    # Send a GET request to the Flickr API
    response = requests.get(url, params=params)

    #Check if the request was successful
    if response.status_code == 200:
        #Parse JSON response and extract the list of photos
        return response.json()['photos']['photo']
    else:
        #Print error message if request failed
        print("Failed to fetch data from Flicker API.")
        return []

#Define a function to construct the URL of a photo
def get_photo_url(photo, size='large'):
    #Base URL for the photo
    url = f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}"

    #Append size suffix to the URL based on the specified size

    if size == 'large':
        url +='_b.jpg'
    elif size =="medium":
        url+="_z.jpg"
    else:
        url += '.jpg'

    return url
    
def download_images(photo_list, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i, photo in enumerate(photo_list):
        img_url = get_photo_url(photo)

        img_path = os.path.join(directory, f"image_{i+1}.jpg")

        with open(img_path, 'wb') as img_file:
            img_file.write(requests.get(img_url).content)

#Define the main function
def main():
    query= "rishikesh"
    api_key= "5946546e4038b015cb4f45a9f30ef0d9"
    num_images= 10
    photo_list = search_flickr(query, api_key, num_images)
    download_images(photo_list, "rishikesh_images")


if __name__ == "__main__":
    main()

