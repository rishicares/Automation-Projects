import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutExceptions, NoSuchElementException

def job():
    #set the full path for the download directory
    download_directory = os.path.join(os.getcwd(), 'gorkhapatra_friday')
 
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)