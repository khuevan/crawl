## test
from utils import crawl_data, openbrowser, openchrome, download

driver = openchrome()
# url = 'https://www.frisogold.com.my/'
url = 'https://www.hipp.my/'

data = crawl_data(driver, url)
# img_url = 'https://www.hipp.my/fileadmin/_processed_/4/8/csm_teaser_promo_big_organic_39934e78af.png'

# print(download(img_url))