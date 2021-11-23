import time
from exts import db
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import datetime
from lxml import etree


def get_cate_info(url):
    print("开始爬虫")

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('window-size=1920x3000')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('lang=en_US.UTF-8')
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chrome_options=chrome_options)
    # browser = webdriver.Chrome('/bin/chromedriver', chrome_options=chrome_options)
    browser.set_page_load_timeout(40)
    browser.set_script_timeout(40)
    #browser.get(url)

    price_list = []
    rating_list = []
    rating_num_list = []
    asin_list = []
    title_list = []
    rank_list = []

    for page_num in range(1, 3):
        url = url + 'ref=zg_bs_pg_' + str(page_num) + '?ie=UTF8&pg=' + str(page_num)
        print(url)
        browser.get(url)
        time.sleep(1)
        print(browser.page_source)

        asins = re.findall('''a class="a-link-normal" href="[\s\S]*?/dp/(.*?)/ref=''', browser.page_source)
        print(asins)
        rank = browser.find_elements_by_xpath('//*[@class="zg-badge-text"]')
        asin_list.extend(asins)
        rank_list.extend(rank)
        for asin in asins:
            print(asin)
            price = re.findall(
                '''href="/[\s\S]*?/dp/''' + asin + '''/ref[\s\S]*?span class='p13n-sc-price' >(.*?)</span>''',
                browser.page_source)
            price_list.extend(price)
            print(price)
            rating = re.findall('title="(.*?)" href="/product-reviews/' + asin + '/ref', browser.page_source)
            rating_num = re.findall('''a-link-normal" href="/product-reviews/''' + asin + '''/ref[\s\S]*?>(\d+)</a>''',browser.page_source)
            rating_list.extend(rating)
            rating_num_list.extend(rating_num)

        title = re.findall('''<div class="p13n-sc-truncate p13n-sc-line-clamp-3" aria-hidden="true" data-rows="3">
                (.*?)
            </div>''', browser.page_source)
        title_list.extend(title)
    time.sleep(1)

    data = list(zip(asin_list, title_list, price_list, rating_list, rating_num_list, rank_list))
    print(data)

    return data

get_cate_info('https://www.amazon.de/gp/bestsellers/computers/430064031/')
