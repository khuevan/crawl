import time
import urllib.request

import html2text

import markdown
import validators
from bs4 import BeautifulSoup

from googlesearch import search
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import pymongo

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
    if validators.url:
        driver.get(url)
        time.sleep(3)

        images = driver.find_elements(By.TAG_NAME, 'img')
        div = driver.find_elements(By.TAG_NAME, 'div')
        html = driver.page_source
        text = html2text.html2text(html, bodywidth=0)
        html = markdown.markdown(text)
        text = "".join(BeautifulSoup(html, "html.parser").findAll(text=True))
        texts = []
        for t in text.split("\n"):
                for x in t.split('. '):
                    if len(x.split(' ')) > 5:
                        texts.append(x)
        imgs = []
        for el in div:
            try:
                image = el.value_of_css_property("background-image")[5:-2]
                if image != 'none':
                    if validators.url(image):
                        imgs.append(image)
            except:
                pass

        for image in images:
            try:
                if image.get_attribute('src') is not None:
                    src = image.get_attribute('src')
                    imgs.append(src)
            except:pass

        data = {
                "url": url,
                "images": imgs,
                "texts": texts
            }
        return data


def check_keyword(text, keyword):
    """Check if text contain keyword
    :param text: A sentence
    :param listkeyword: A list of keyword [ [key1, key3], [key2, key3] ]
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

    
def get_data(url):
    data = data_collection.find_one({'url': url})
    if data is None:
        data = crawl_data(openbrowser(), url)
        text_checked = [{'text': text, 'vipham': check_keyword(text, get_keyword())}for text in data['texts']]
        data.update({"texts": text_checked})
        data_collection.insert_one(data)
        return data
    else:
        return data


# if __name__ == '__main__':
#     searchurls()
#     for data in url_collection.find():
#         for url in data['urls']:
#             get_data(url)


