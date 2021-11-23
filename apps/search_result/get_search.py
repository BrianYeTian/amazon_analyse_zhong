import re
import time

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from apps.single_pd.trace_pd import add_zip


def get_search_result(keyword, page_num, mkp):
    print('正在获取数据')
    mkp_url = 'https://www.amazon.' + mkp
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.implicitly_wait(30)
    browser.get(mkp_url)
    time.sleep(1)
    try:
        add = browser.find_element_by_id('glow-ingress-line1' and 'glow-ingress-line2')
        add.click()
    except:
        pass

    time.sleep(1)
    browser.switch_to.default_content()
    try:
        zipp = browser.find_element_by_id('GLUXZipUpdateInput')
        time.sleep(1)
        add_zip('us', zipp)
        zipp.send_keys(Keys.ENTER)
    except:
        pass
    time.sleep(1)

    TitelList = []
    PriceList = []
    RatingList = []
    RatingNumList = []
    ASINlist = []

    # 如果有接受cookies的提醒需要点击
    try:
        acpt_cookie = browser.find_element_by_id('sp-cc-accept')
        acpt_cookie.click()
    except:
        pass

    browser.refresh()
    time.sleep(1)

    page = 1
    # for i in page_num:
    url = mkp_url + '/s?k=' + keyword + '&ref=nb_sb_noss'
    browser.get(url)

    for page in range(0,page_num):
        time.sleep(2)
        page_source = browser.page_source

        ASINllst = re.findall(
            '<div data-asin="(.*?)" data-index="(\d+)" data-uuid=',
            page_source)
        for ASIN in ASINllst:  # 抓取出来的有一部分是空值，需要去掉
            if ASIN == '':
                ASINllst.remove(ASIN)
        # webElement = browser.find_elements_by_xpath('//*[@]')
        print(len(ASINllst))

        for ASIN in ASINllst:
            ASINlist.append(ASIN[0])
        # print(len(ASINlist), ASINlist)

        titles = browser.find_elements_by_xpath(
            '//*[@class="s-include-content-margin s-latency-cf-section s-border-bottom s-border-top"]/div/div[2]/div[2]/div/div/div/h2/a/span')
        print(len(titles))
        for title in titles:
            # print(title.text)
            TitelList.append(title.text)

        ratings = browser.find_elements_by_xpath(
            '//*[@class="s-include-content-margin s-latency-cf-section s-border-bottom s-border-top"]/div/div[2]/div[2]/div/div/div[2]/div/span/span/a/i/span')
        print(len(ratings))
        for rating in ratings:
            # print(rating.text)
            RatingList.append(rating.text)

        prices = browser.find_elements_by_xpath(
            '//*[@class="s-include-content-margin s-latency-cf-section s-border-bottom s-border-top"]/div/div[2]/div[2]/div/div/div[3]/div/div/div/div/a/span/span')
        for price in prices:
            # print(price.text)
            if price.text != "":
                if '.' in price.text:
                    pass
                elif len(price.text) > 10:
                    pass
                else:
                    PriceList.append(price.text.replace('\n', '.'))
        print(PriceList)
        # print(PriceList)

        rating_nums = browser.find_elements_by_xpath(
            '//*[@class="s-include-content-margin s-latency-cf-section s-border-bottom s-border-top"]/div/div[2]/div[2]/div/div/div[2]/div/span[2]/a/span')
        print(len(rating_nums))
        for rating_num in rating_nums:
            # print(rating_num.text)
            RatingNumList.append(rating_num.text)

        # try:
        browser.find_element_by_xpath('//*[@class="a-last"]/a').click()
        # except:
        #     pass

    print(len(ASINlist))
    print(len(TitelList))
    print(len(PriceList))
    print(len(RatingList))
    print(len(RatingNumList))

    lst = list(zip(ASINlist, PriceList, RatingList, RatingNumList, TitelList))

    return lst

#
# get_search_result('usb hub','5','com')
