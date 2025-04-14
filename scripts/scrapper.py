# --------Imports--------
import deep_translator
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import threading
import json
import time
import re
import os

import sys
sys.stdout.reconfigure(encoding='utf-8')

# --------Functions--------


def get_driver(headless=False):
    """
    Creates a new instance of the Chrome driver.

    Args:
        headless (bool): Whether to run the driver in headless mode.

    Returns:
        undetected_chromedriver.Chrome: The Chrome driver.
    """
    # Create a new instance of ChromeOptions
    options = uc.ChromeOptions()

    # If headless is True, add the headless argument
    if headless:
        options.add_argument('--headless')

    # Add the profile directory argument
    options.add_argument('--profile-directory=Default')

    # Add the disable blink features argument
    options.add_argument('--disable-blink-features=AutomationControlled')

    # Create a new instance of the Chrome driver
    return uc.Chrome(
        options=options,  # Pass the options to the Chrome driver
        # Specify the path to the chromedriver
        driver_executable_path='./res/chromedriver.exe',
        version_main=135,  # Specify the major version of Chrome
        # Specify the user data directory
        user_data_dir='C:/Users/Mikec/AppData/Local/Google/Chrome/User Data'
    )


def scrape_posts(query: str, note_items: dict, scroll_amount=20):
    """Scrapes the main page of Xiaohongshu for posts with the given query.

    Args:
        query (str): The query to search for.
        note_items (dict): A dictionary containing the scraped posts.

    Returns:
        None
    """
    # Scraping url
    url = f"https://www.xiaohongshu.com/search_result?keyword={query}"
    driver.get(url)
    scroll_attempts = 0
    last_height = driver.execute_script(
        "return document.body.scrollHeight")

    try:
        while scroll_attempts < scroll_amount:
            # print(f"Scrolling {scroll_attempts}/{scroll_amount}")
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extracting posts
            posts = soup.find_all('a', {'class': 'cover mask ld'})
            for post in posts:
                if "https://www.xiaohongshu.com" + post['href'] in note_items:
                    continue
                print("New page found")
                note_items["https://www.xiaohongshu.com" + post['href']] = {
                    'title': {
                        'zh': '',
                        'en': '',
                    },
                    'description': {
                        'zh': '',
                        'en': '',
                    },
                    'images': [],
                    'videos': [],
                }

            # Scrolling
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Allow new content to load
            new_height = driver.execute_script(
                "return document.body.scrollHeight")

            if new_height == last_height:  # Stop if no more content loads
                print("No more content to load")
                break
            last_height = new_height
            scroll_attempts += 1

    except Exception as e:
        print(f'No posts found: \n {e}')
        # print(soup.prettify())


def scrape_post(url: str, id):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    with open(f'./res/pages/{id}.html', 'w+', encoding='utf-8') as f:
        f.write(soup.head.prettify())


def scrape_post_thread(name: str,  url: str, note_items: dict):
    # HTML
    soup = BeautifulSoup(
        open(f'./res/pages/{name}.html', 'r', encoding='utf-8').read(), 'html.parser')

    # Extracting Title
    try:
        title = soup.find('meta', {'name': 'og:title'}).get('content')
    except:
        title = 'NULL'

    # Extracting Description
    try:
        desc = soup.find('meta', {'name': 'description'}).get('content')
    except:
        desc = 'NULL'

    # Extracting Images

    try:
        imgs = soup.find_all('meta', {'name': 'og:image'})
        imgs = [img.get('content') for img in imgs]
    except:
        imgs = []

    # Extracting Video
    try:
        videos = soup.find_all('meta', {'name': 'og:video'})
        videos = [video.get('content') for video in videos]
    except:
        videos = []

    with lock:
        note_items[url]['title']['zh'] = title
        note_items[url]['title']['en'] = translator.translate(title)
        note_items[url]['description']['zh'] = desc
        note_items[url]['description']['en'] = translator.translate(desc)
        note_items[url]['images'] = imgs
        note_items[url]['videos'] = videos


# --------Data--------
global driver
driver = get_driver(headless=True)
translator = GoogleTranslator(source='auto', target='en')
results = {}
lock = threading.Lock()

if __name__ == "__main__":
    note_items = json.load(open('res/output.json', 'r', encoding='utf-8'))
    # Scraping main page
    if False:
        scrape_posts('Labubu One Piece Weights', note_items)
        json.dump(note_items, open('res/output.json',
                  'w', encoding='utf-8'), indent=4)

    # Scraping posts from main page
    if False:
        for url in note_items:
            name = url.split('/')[4].split('?')[0]
            if os.path.exists(f'./res/pages/{name}.html'):
                continue
            print(f"Scraping {name}")
            scrape_post(url, name)

    # Scraping posts from saved pages
    if False:
        threads = []
        for url in note_items:
            print(f"Scraping {counter}/{len(note_items)}", end='\r')

            name = url.split('/')[4].split('?')[0]

            if os.path.exists(f'./res/pages/{name}.html'):
                t = threading.Thread(
                    target=scrape_post_thread, args=(name, url, note_items))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()
        json.dump(note_items, open('res/output.json',
                  'w', encoding='utf-8'), indent=4)

    # Display
    if False:
        for url in note_items:
            print(f"Title: {note_items[url]['title']['en']}")
            # print(f"\tImage: {note_items[url]['image']}")
            print(f"\tDescription: {note_items[url]['description']['en']}")
            print("-" * 50)
        # print(len(note_items))

    driver.quit()
