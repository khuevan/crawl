# crawl

## Installation

```
pip install -r requirements.txt
```

## Function

Hàm `openbrowser()` mở trình duyệt Edge chạy ngầm

```python
def openbrowser():
    options = webdriver.EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    options.add_argument('headless')
    options.add_argument('window-size=0x0')
    options.add_argument('ignore-certificate-errors')
    driver = webdriver.Edge(options=options)
    return driver
```

Hàm `crawl()` truyền vào *url* và lấy tất cả *text* và *image* từ *url* và trả về 1 *dict* chứa url, mảng images, mảng texts

```python
def crawl(driver, url):
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
```
Hàm `check_keyword()` kiểm tra trong câu có chứa keyword không. 

```python
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
```

`get_data()` lấy dữ liệu trả về dữ liệu theo url

```python
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
```

### API

API có dạng:

```python
[
  {
    "_id": {
      "$oid": "62cf12122f546937e7649a72"
    },
    "url": "https://www.vinataba.com.vn/2021/08/12/dang-uy-tong-cong-ty-thuoc-la-viet-nam-so-ket-5-nam-thuc-hien-nghi-quyet-trung-uong-4-khoa-xii-5/",
    "images": [
      "/static/images/1657737742914619.jpg",
      "/static/images/1657737745335906.jpg",
      "/static/images/16577377455767.jpg"
    ],
    "texts": [
      {
        "text": "Vinataba ủng hộ Quỹ vắc xin phòng Covid-19 100 tỷ đồng",
        "vipham": true
      },
      {
        "text": "Tối 05/06/2021, Lễ ra mắt Quỹ vaccine phòng, chống COVID-19 đã diễn ra tại Hà Nội",
        "vipham": false
      },
      {
        "text": "Đồng chí Phạm Minh Chính – Ủy viên Bộ Chính trị, Thủ tướng Chính phủ tham dự sự kiện",
        "vipham": false
      },
      {
        "text": "Tại buổi lễ, Bí thư Đảng uỷ, Chủ tịch HĐTV Hồ Lê Nghĩa đã trao tặng Quỹ số tiền ủng hộ 100 tỷ đồng của Tổng công ty Thuốc lá Việt Nam.",
        "vipham": true
      }
    ]
  },
]
```
