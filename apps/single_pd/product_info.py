import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_product_info(url, asin):
    print('正在获取asin%s的数据', asin)
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('window-size=1920x3000')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--headless')
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chrome_options=chrome_options)
    # browser = webdriver.Chrome('/bin/chromedriver', chrome_options=chrome_options)
    browser.set_page_load_timeout(40)
    browser.set_script_timeout(40)
    browser.get(url)

    product_title = browser.find_element_by_id('productTitle')
    #print(product_title.text)
    product_brand_text = browser.find_element_by_id('bylineInfo').text
    product_brand = re.findall('Visit the (.*?) Store',product_brand_text)
    #print(product_brand.text)
#     pat = re.compile('''Date First Available[\s]*</th>[\s]*<td class="a-size-base prodDetAttrValue">
# (.*?)
# </td>''',re.DOTALL)
#     release_date = pat.findall(browser.page_source)
    #print(release_date)
    print()
    return product_brand
