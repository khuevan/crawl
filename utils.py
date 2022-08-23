import json
import os
import time
import concurrent.futures

from PIL import Image
import html2text
from requests import adapters

import markdown
import requests
import validators
from bs4 import BeautifulSoup
import ssl

from urllib3 import poolmanager

from googlesearch import search
from selenium import webdriver
from selenium.webdriver.common.by import By
import pymongo

from settings import CHROME_PATH, HEIGHT, WIDTH, DOMAIN
from keywords import keywords, brands, intents

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['crawlbykeyword']
data_collection = db['data']


def searchurls():
    urls = []
    for brand in brands:
        for intent in intents:
            listurl = search(f'{brand} {intent}', num_results=5, lang='vi')
            time.sleep(5)
            for item in listurl:
                urls.append(item)
    return urls


def openbrowser():
    options = webdriver.EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    options.add_argument('headless')
    options.add_argument('window-size=0x0')
    options.add_argument('ignore-certificate-errors')
    driver = webdriver.Edge(options=options)
    return driver


def openchrome():
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
            img_url = image.get_attribute("srcset") or image.get_attribute("src") or image.get_attribute("data-src") or image.get_attribute("data-original")
            if img_url is not None:
                src = img_url
                if validators.url(src):
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
    """
    Get all text and image form url

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

        with concurrent.futures.ThreadPoolExecutor() as executor:
            imgs = executor.map(download, imgs)

        data = {
                "url": url,
                "images": list(imgs),
                "texts": texts
            }

        return data


def check_keyword(texts: list, keyword):
    """
    Check if text contain keyword

    :param texts:
    :param keyword: A list of keyword
    :return: True False
    """
    keys = []
    brand = []
    for text in texts:
        for txt in text.split('.'):
            for item in keyword:
                for key in item['keyword']:
                    a = [x for x in key if x.lower() in txt.lower()]
                    if a == key:
                        keys.append(a)
                        brand.append(item['brand'])
    if not keys:
        return False, set(brand)
    else:
        return True, set(brand)

    
def get_data(driver, url):
    data = data_collection.find_one({'url': url})
    if data is None:
        data = crawl_data(driver, url)
        imgs = [DOMAIN + '/' + str(im) for im in data['images'] if im is not None]
        text_checked = []
        for text in data['texts']:
            violation, brand = check_keyword([text], keywords)
            text_checked.append({'text': text, 'vipham': violation})
        data.update({"images": imgs})
        data.update({"texts": text_checked})
        data_collection.insert_one(data)
        return data
    else:
        return data


class TLSAdapter(adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)


def download(url, pathname='static/images/'):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        try:
            os.makedirs(pathname)
        except:
            pass
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    session = requests.session()
    session.mount('https://', TLSAdapter())

    try:
        response = requests.get(url, headers=headers)
    except:
        response = requests.get(url, headers=headers, verify=False)

    # get the file name
    filename = os.path.join(pathname, str(int(time.time()*1000))+'.jpg')
    filename = filename.replace('%', '')
    try:
        with open(filename, "wb") as f:
            f.write(response.content)
    except:
        pass
    try:
        if filter_size(filename):
            return filename
    except:
        pass


def filter_size(pathimage):
    try:
        with Image.open(pathimage) as im:
            w, h = im.size
        if h < int(HEIGHT) and w < int(WIDTH):
            os.remove(pathimage)
            return False
    except:
        os.remove(pathimage)
        return False
    return True


def add_to_database(content, brand, image, status, link, method="0"):
    url = "https://tobacco.corporateaccountabilitytool.org/action-managements/adddatabase"
    payload = json.dumps({
        "content": content,
        "brand": brand,
        "image": image,
        "method": method,
        "status": status,
        "link": link
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def crawl_to_database(link):
    data = get_data(driver, link)
    text = [txt['text'] for txt in data['texts']]
    is_violation, brand = check_keyword(text, keywords)
    content = ' '.join(map(str, text))
    image = data['images']
    add_to_database(content, list(brand), image, "0" if is_violation is False else "2", link)


if __name__ == '__main__':
    driver = openbrowser()
    urls = searchurls()
    for url in urls:
        crawl_to_database(url)
    driver.close()
