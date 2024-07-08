# scraper/scraper.py
import os
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .models import MessageData, VisitedMessage

# Constants
LINKEDIN_URL = "https://www.linkedin.com"
COOKIES_PATH = "linkedin_cookies.json"
DOWNLOAD_FOLDER = "downloads"

# Regex patterns for scraping
EMAIL_PATTERN = r'[\w\.-]+@[\w\.-]+'
PHONE_PATTERN = r'\+?\d[\d -]{8,}\d'
LINK_PATTERN = r'(https?://[^\s]+)'

def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-data-dir={os.path.abspath('profile')}")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(DOWNLOAD_FOLDER),
        "download.prompt_for_download": False,
    })
    service = Service('path/to/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login(driver):
    driver.get(LINKEDIN_URL)
    input("Complete 2FA and press Enter...")

def load_cookies(driver):
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, 'r') as file:
            cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def save_cookies(driver):
    with open(COOKIES_PATH, 'w') as file:
        json.dump(driver.get_cookies(), file)

def scrape_message_history(driver, messages):
    for message in messages:
        message_id = message.get_attribute('data-entity-urn')
        if VisitedMessage.objects.filter(message_id=message_id).exists():
            continue
        message.click()
        time.sleep(2)
        scroll_to_top(driver)
        while True:
            content = driver.find_element(By.CLASS_NAME, 'msg-s-message-list').text
            emails = re.findall(EMAIL_PATTERN, content)
            phones = re.findall(PHONE_PATTERN, content)
            links = re.findall(LINK_PATTERN, content)
            for email in emails:
                MessageData.objects.create(email=email)
            for phone in phones:
                MessageData.objects.create(phone=phone)
            for link in links:
                MessageData.objects.create(link=link)
            if not load_more_messages(driver):
                break
        VisitedMessage.objects.create(message_id=message_id)

def scroll_to_top(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.CONTROL, Keys.HOME).perform()

def load_more_messages(driver):
    try:
        load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load more messages')]")
        load_more_button.click()
        time.sleep(2)
        return True
    except:
        return False

def scrape_linkedin():
    driver = init_driver()
    load_cookies(driver)
    driver.get(LINKEDIN_URL)
    login(driver)
    save_cookies(driver)

    driver.get(f"{LINKEDIN_URL}/messaging")
    time.sleep(5)

    messages = driver.find_elements(By.CLASS_NAME, 'msg-conversation-listitem')
    scrape_message_history(driver, messages)

    driver.quit()
