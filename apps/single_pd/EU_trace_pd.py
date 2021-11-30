import re
import threading
import time

from flask import g, session
from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

from apps.single_pd.model import Amazon, Trace_pd_info
from apps.single_pd.trace_pd import get_rank, add_zip
# from apps.webdriver import ChromeDriver
import logging

from apps.user.model import User
from exts import db

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from threading import Thread

engine = create_engine(
    "mysql+pymysql://root:root@127.0.0.1:3306/amazon5?charset=utf8",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)

SessionFactory = sessionmaker(bind=engine)
sessions = scoped_session(SessionFactory)


def get_quanlity_re(pat1, pat2, page_source):
    try:
        inven_num = re.findall(pat1, page_source)
        if not inven_num:
            inven_num = re.findall(pat2, page_source)
            inven_num = ['限制最大订单数量' + inven_num[0]]

    except:
        inven_num = ['0']
    return inven_num


def get_quanlity(page_source, mkp, browser):
    global inven_num
    if mkp == 'de':
        inven_num = get_quanlity_re(r'beträgt momentan lediglich: (\d+). <a href=', r'auf (\d+) aktualisiert.',
                                    page_source)
    elif mkp == 'fr':
        browser.refresh()
        inven_num = get_quanlity_re(r'''mais le vendeur que vous avez choisi n'en a que (\d+) de''',
                                    r'''limite de vente de (\d+) articles par client''', page_source)
    elif mkp == 'it':
        inven_num = get_quanlity_re(r'''numero superiore alla quantità di (\d+) articoli''',
                                    r'''presenta un limite di (\d+) per cliente''', page_source)
    elif mkp == 'es':
        inven_num = get_quanlity_re(r'de los (\d+) disponibles.', r'un límite de (\d+) por cliente', page_source)

    elif mkp == 'us' or mkp == 'uk':
        inven_num = get_quanlity_re(r'than the (\d+) available from the seller', 'has a limit of (\d+) per customer',
                                    page_source)

    elif mkp == 'jp':
        inven_num = get_quanlity_re(r'商品は、(\d+)点のご注文に制限', '一人あたり(\d+)までと限定',
                                    page_source)

    return inven_num


def EU_trace_pd(url_mkps, asin_list, user_id):
    logging.info('正在获取数据')
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

    asin_num = 0
    mkp_old = ''
    for url_mkp in url_mkps:
        asin = asin_list[asin_num]
        print('正在抓取第', asin_num + 1, '个', '共提交', len(url_mkps), '个')
        for mkp, url in url_mkp.items():
            sales_price_list = []
            rating_num_list = []
            rating_list = []
            rank_list = []
            cate_list = []
            inventory_list = []
            title_list = []
            mkp_list = []

            # print(mkp, url)
            mkp_list.append(mkp)
            amazon_url = re.findall('(.*?)/dp', url)
            if mkp_old != mkp:
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
                price = html1.xpath('//span[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span')
                if price:
                    sale_price = price[0].text
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

            if mkp == 'us' or mkp == 'de':
                try:
                    # offeringID = re.findall(r'id="offerListingID" name="offerListingID" value="(.*?)"',page_resource)[0]
                    # print(offeringID)
                    offeringID = \
                        re.findall(r'<input type="hidden" id="twister-plus-offer-listing-id" value="(.*?)"',
                                   page_resource)[
                            0]
                except:
                    offeringID = ''
            else:
                offeringID = ''

            # 获取当前市场和页面的cookies
            cookies = browser.get_cookies()
            # print(cookies)
            for cookie in cookies:
                keys = cookie.values()
                # print(keys)
                for val in keys:
                    if val == 'session-id':
                        session_id = list(keys)[-1]
                        # print(session_id)
            if mkp == 'us' or mkp == 'de':
                hbx_url = amazon_url[
                              0] + '/gp/product/handle-buy-box/ref=dp_start-bbf_1_glance&session-id=' + session_id + '&ASIN=' + asin + '&quantity=509990' + '&offerListingID=' + offeringID
            else:
                hbx_url = amazon_url[
                              0] + '/gp/product/handle-buy-box/ref=dp_start-bbf_1_glance&session-id=' + session_id + '&ASIN=' + asin + '&quantity=509990'

            browser.get(hbx_url)
            print(hbx_url)
            time.sleep(1)
            page_source = browser.page_source
            # print(page_source)
            try:
                inven_num = get_quanlity(page_source, mkp, browser)
            except:
                inven_num = ['无库存']
            # print(inven_num)

            mkp_old = mkp

            sales_price_list.append(sale_price)
            rating_num_list.append(rating_num)
            rating_list.append(rating[0])
            cate_list.append(cate)
            rank_list.append(rank)
            inventory_list.append(inven_num[0])
            title_list.append(title)

            get_pd_infos = list(
                zip(sales_price_list, rating_num_list, rating_list, cate_list, rank_list, inventory_list, asin_list,
                    title_list, mkp_list))

            # 无法写入数据库的问题是因为多线程里面不能共用全局里面的session对象，需要在线程里面再重新创建新的session对象
            lock = threading.Lock()
            lock.acquire()
            t = Thread(target=write, args=(get_pd_infos, user_id, asin))
            t.start()
            t.join()  # 需要使用join方法堵住主线程的运行，不然主线程跑到下一个去了，ASIN和市场就变了，导致写入数据库的数据有问题
            lock.release()

        asin_num += 1

    browser.close()

    # 可以再加一个记录，成功了多少，失败了多少，失败的是哪些产品？有没有限定最大订单数量？然后再返回到个人记录的任务栏日志下面去


def write(get_pd_infos, user_id, asin):
    for get_pd_info in get_pd_infos:
        print(get_pd_info)

        if '限制最大订单' in get_pd_info:
            limit = "Y"
        else:
            limit = "N"

        pd_infos = sessions.query(Amazon).filter_by(asin=asin,
                                                    market=get_pd_info[8],
                                                    isdelete='N').first()  # 结合每个ASIN和市场在信息表里面查询到对应的id

        write_pd = Trace_pd_info(asin=asin, price=get_pd_info[0], rating_num=get_pd_info[1],
                                 rating=get_pd_info[2], cate=get_pd_info[3], rank=get_pd_info[4],
                                 inventory=get_pd_info[5], pd_info_id=pd_infos.product_id,
                                 user_id=user_id,
                                 market=get_pd_info[8])
        sessions.add(write_pd)
        sessions.commit()
        print('数据更新成功')

        pd_infos.limit = limit
        sessions.commit()

        if pd_infos.goods_name == '':
            pd_infos.goods_name = get_pd_info[7]
            sessions.commit()

        sessions.remove()
