## test
from utils import crawl_data, openbrowser

driver = openbrowser()
url = 'https://www.anmum.com/nz/products/assura-organic/assura-organic-1'

data = crawl_data(driver, url)