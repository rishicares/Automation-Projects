import os
import sys
import time
import requests
from pytube import YouTube
from pytube import exceptions

def ytdownloader():
    video_url = input("Enter the YouTube video URL: ")
    save_path = 'C:\\Users\\rishi\\OneDrive - Storage\\Programming\\Automation-Projects\\downloads'

    try:
        yt = YouTube(video_url)
        video = yt.streams.get_highest_resolution()
        video.download(save_path)
        print("Video downloaded successfully!")
    except exceptions.RegexMatchError:
        print("Invalid YouTube video URL!")
    except exceptions.VideoUnavailable:
        print("The video is unavailable!")
    except exceptions.ExtractError:
        print("Error extracting video information!")
    except exceptions.RequestError:
        print("Error connecting to YouTube!")

ytdownloader()