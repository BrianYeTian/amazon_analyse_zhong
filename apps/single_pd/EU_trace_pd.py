import re
import time

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

from apps.single_pd.trace_pd import get_rank, add_zip
# from apps.webdriver import ChromeDriver
import logging


def get_quanlity_re(pat1, pat2, page_source):
    inven_num = re.findall(pat1, page_source)
    if not inven_num:
        inven_num = re.findall(pat2, page_source)
        inven_num = ['限制最大订单数量' + inven_num[0]]
        if not inven_num:
            inven_num = [0]
    return inven_num


def get_quanlity(page_source, mkp):
    global inven_num
    if mkp == 'de':
        inven_num = get_quanlity_re(r'beträgt momentan lediglich: (\d+). <a href=', r'auf (\d+) aktualisiert.',
                                    page_source)
    elif mkp == 'fr':
        inven_num = get_quanlity_re(r'''mais le vendeur que vous avez choisi n'en a que (\d+) de''',
                                    r'''limite de vente de (\d+) articles par client''', page_source)
    elif mkp == 'it':
        inven_num = get_quanlity_re(r'''numero superiore alla quantità di (\d+) articoli''',
                                    r'''presenta un limite di (\d+) per cliente''', page_source)
    elif mkp == 'es':
        inven_num = get_quanlity_re(r'de los (\d+) disponibles.', r'un límite de (\d+) por cliente', page_source)

    elif mkp == 'us' or mkp == 'uk':
        inven_num = get_quanlity_re(r'than the (\d+) available from the seller','has a limit of (\d+) per customer',page_source)

    return inven_num


def EU_trace_pd(url_mkps, asin_list):
    # logging.info('正在获取数据')
    # wd = ChromeDriver()
    browser = webdriver.Chrome()
    # try:
    #     browser = wd.GetChromeDriver()
    #
    # except Exception as err:
    #     logging.error(err)
    #     return None

    # browser = webdriver.Chrome()
    browser.maximize_window()
    browser.implicitly_wait(10)
    sales_price_list = []
    rating_num_list = []
    rating_list = []
    rank_list = []
    cate_list = []
    inventory_list = []
    title_list = []
    mkp_list = []

    asin_num = 0
    for url_mkp in url_mkps:
        asin = asin_list[asin_num]
        for mkp, url in url_mkp.items():
            # print(mkp, url)
            mkp_list.append(mkp)
            amazon_url = re.findall('(.*?)/dp', url)
            browser.get(amazon_url[0])
            try:
                acpt_cookie = browser.find_element_by_id('sp-cc-accept')
                acpt_cookie.click()
            except:
                pass
            browser.refresh()
            time.sleep(0.5)

            try:
                add = browser.find_element_by_id('glow-ingress-line1' and 'glow-ingress-line2')
                add.click()
            except:
                pass

            time.sleep(1)
            browser.switch_to.default_content()
            if mkp == 'au':
                try:
                    zipp = browser.find_element_by_id('GLUXPostalCodeWithCity_PostalCodeInput')
                    time.sleep(0.5)
                    zipp.send_keys('3000')
                    time.sleep(1)
                    city = browser.find_element_by_id('GLUXPostalCodeWithCity_CityValue')
                    city.click()
                    browser.find_element_by_id('GLUXPostalCodeWithCity_DropdownList_0').click()
                    time.sleep(0.5)
                    browser.find_element_by_id('GLUXPostalCodeWithCityApplyButton').click()
                except:
                    pass
            else:
                try:
                    zipp = browser.find_element_by_id('GLUXZipUpdateInput')
                    time.sleep(1)
                    add_zip(mkp, zipp)
                    zipp.send_keys(Keys.ENTER)
                except:
                    pass
            time.sleep(1)

            browser.get(url)
            time.sleep(1)

            page_resource = browser.page_source
            time.sleep(0.1)
            html1 = etree.HTML(page_resource)

            # 获取目录排名信息

            rank_cate = get_rank(mkp, page_resource)
            rank = rank_cate[0]
            cate = rank_cate[1]

            try:
                title = browser.find_element_by_id('productTitle').text
            except:
                title = ''

            if mkp == 'au':
                price = html1.xpath('//span[@class="a-price a-text-price a-size-medium"]/span')
                if price:
                    sale_price = price[0].text
                else:
                    sale_price = '无售价'
            else:
                price = re.findall('a-price a-text-price a-size-medium apexPriceToPay[\s\S]*?<span aria-hidden="true">(.*?)</span>',page_resource)
                if price:
                    sale_price = price[0]
                else:
                    sale_price = '无售价'

            try:
                rating_num = re.findall('(.*?) ', browser.find_element_by_id('acrCustomerReviewText').text)[0]
            except:
                rating_num = 0

            try:
                ratings = re.findall('''class="reviewCountTextLinkedHistogram noUnderline" title="(.*?)">''',
                                     browser.page_source)
                rating = re.findall('(.*?) [\s\S]*? 5', ratings[0])
            except:
                rating = []
                rating.append('无评价')

            if mkp == 'uk':
                # offeringID = re.findall(r'id="offerListingID" name="offerListingID" value="(.*?)"',page_resource)[0]
                # print(offeringID)
                offeringID = ''
            else:
                offeringID = re.findall(r'<input type="hidden" id="twister-plus-offer-listing-id" value="(.*?)"',page_resource)[0]

            # 获取当前市场和页面的cookies
            cookies = browser.get_cookies()
            # print(cookies)
            if mkp =='uk':
                session_id =cookies[-5]['value']
            else:
                session_id = cookies[-1]['value']
            # print(session_id)
            # print(mkp)
            print(offeringID)

            hbx_url = amazon_url[
                          0] + '/gp/product/handle-buy-box/ref=dp_start-bbf_1_glance&session-id=' + session_id + '&ASIN=' + asin + '&quantity=509990' + '&offerListingID=' + offeringID

            # print(hbx_url)
            browser.get(hbx_url)
            time.sleep(1)
            page_source = browser.page_source
            # print(page_source)
            inven_num = get_quanlity(page_source, mkp)
            # print(inven_num)

            sales_price_list.append(sale_price)
            rating_num_list.append(rating_num)
            rating_list.append(rating[0])
            cate_list.append(cate)
            rank_list.append(rank)
            inventory_list.append(inven_num[0])
            title_list.append(title)
        asin_num += 1

    browser.close()

    lst = list(zip(sales_price_list, rating_num_list, rating_list, cate_list, rank_list, inventory_list, asin_list,
                   title_list, mkp_list))

    return lst

#
# if __name__ == '__main__':
#     lst = EU_trace_pd([{'de': 'https://www.amazon.de/dp/B08SLS9W72'}], ['B08SLS9W72'])
#     print(lst)
