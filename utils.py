import time
import urllib.request
from datetime import datetime

import html2text

import markdown
import validators
from bs4 import BeautifulSoup

from googlesearch import search
from selenium import webdriver
from selenium.webdriver.common.by import By
import pymongo

from settings import CHROME_PATH
from keywords import keywords

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['crawlbykeyword']
brands_collection = db['brands']
intents_collection = db['intents']
data_collection = db['data']
url_collection = db['urls']
key_collection = db['keywords']


def get_keyword():
    listkey = []
    for brand in brands_collection.find():
        for key in key_collection.find():
            for k in key['keyword']:
                listkey.append([k, brand['brand']])
    return listkey


def searchurls():
    for brand in brands_collection.find():
        for intent in intents_collection.find():
            liststrurl = []
            listurl = search(f'{brand["brand"]} {intent["intent"]}', num_results=5, lang='vi')
            time.sleep(5)
            for item in listurl:
                liststrurl.append(item)

            url_collection.insert_one({
                "brand": brand['brand'],
                "intent": intent['intent'],
                "urls": liststrurl
            })


def openbrowser():
    options = webdriver.EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    options.add_argument('headless')
    options.add_argument('window-size=0x0')
    options.add_argument('ignore-certificate-errors')
    driver = webdriver.Edge(options=options)
    return driver


def openChrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path=CHROME_PATH, chrome_options=chrome_options)
    return driver


def get_image(images, backgoundimg=None):
    imgs = []
    for el in backgoundimg or []:
        try:
            image = el.value_of_css_property("background-image")[5:-2]
            if image != 'none':
                if validators.url(image):
                    imgs.append(image)
        except:pass
    for image in images or []:
        try:
            if image.get_attribute('src') is not None:
                src = image.get_attribute('src')
                imgs.append(src)
        except:pass
    return imgs


def gettexthtml(html):
    texts = []
    text = html2text.html2text(html, bodywidth=0)
    html = markdown.markdown(text)
    text = "".join(BeautifulSoup(html, "html.parser").findAll(text=True))
    for t in text.split("\n"):
        for x in t.split('. '):
            if len(x.split(' ')) > 5:
                texts.append(x)
    return texts


def crawl_data(driver, url):
    """Get all text and image form url
    :param driver: webdriver
    :param url: url
    :return: A dict contain url, list image, list text
            {
                'url': url
                'images': [...]
                'texts': [...]
            }
    """
    if validators.url(url):
        driver.get(url)
        time.sleep(2)

        images = driver.find_elements(By.TAG_NAME, 'img')
        div = driver.find_elements(By.TAG_NAME, 'div')
        html = driver.page_source

        try:
            imgs = get_image(images, div)
        except:
            imgs = []
        try:
            texts = gettexthtml(html)
        except:
            texts = []

        data = {
                "url": url,
                "images": imgs,
                "texts": texts
            }

        return data


def check_keyword(text, keyword: list):
    """Check if text contain keyword
    :param keyword: A list of keyword [ [key1, key3], [key2, key3] ]
    :param text: A sentence
    :return: True False
    """
    keys = []
    for item in keyword:
        a = [key for key in item if key.lower() in text.lower()]
        if a == item:
            keys.append(a)
    if not keys:
        return False
    else:
        return True

    
def get_data(url, driver):
    data = data_collection.find_one({'url': url})
    if data is None:
        data = crawl_data(driver, url)
        path = 'static/image'
        images = [image for image in saveimage(data['images'], path)]
        text_checked = [{'text': text, 'vipham': check_keyword(text, keywords)}for text in data['texts']]
        data.update({"texts": text_checked})
        data.update({"images": images})
        data_collection.insert_one(data)
        return data
    else:
        return data


def saveimage(images: list, path):
    """Save image file with TimeStamp as file name
    :param images: list url f image
    :param path: place to save
    :return: list path to images
    """
    listimages = []
    for image in images:
        dt = datetime.now
        ts = datetime.timestamp(dt)
        name = '/' + str(ts) + image.split('.')[-1]
        urllib.request.urlretrieve(image, name)
        listimages.append(path + name)
    return listimages


# if __name__ == '__main__':
#     searchurls()
#     for data in url_collection.find():
#         for url in data['urls']:
#             get_data(url)


