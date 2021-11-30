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

from apps.single_pd.model import Amazon, Trace_pd_info, Cart
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


def spider_cart(asin, url, mkp, user_id):
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
    browser.implicitly_wait(20)

    get_pd_info=[]
    get_pd_info.append(mkp)
    get_pd_info.append(asin)
    if mkp == 'us':
        browser.get('https://www.amazon.com')
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
    html1 = etree.HTML(page_resource)
    if mkp == 'us':
        try:
            seller = browser.find_element_by_xpath('//*[@id="tabular-buybox"]/div/div[4]/div/span/a').text
            if seller is None:
                seller = browser.find_element_by_xpath('//*[@id="tabular-buybox"]/div/div[4]/div/span').text
        except:
            seller = "没有购物车"

        get_pd_info.append(seller)

        try:
            ship = browser.find_element_by_xpath('//*[@id="tabular-buybox"]/div/div[2]/div/span').text
        except:
            ship = "没有购物车"

        get_pd_info.append(ship)

    if mkp == 'de':
        try:
            seller = browser.find_element_by_xpath('//*[@id="merchant-info"]/a/span').text
            if seller:
                ship = browser.find_element_by_xpath('//*[@id="merchant-info"]/a[2]/span').text
                get_pd_info.append(seller)
                get_pd_info.append(ship)
            else:
                seller = "没有购物车"
                ship = "没有购物车"
                get_pd_info.append(seller)
                get_pd_info.append(ship)


        except:
            seller = browser.find_element_by_xpath('//*[@id="merchant-info"]/span').text
            if 'Verkauf und Versand' in seller:
                seller = "Amazon"
                ship = "Amazon"
                get_pd_info.append(seller)
                get_pd_info.append(ship)
            else:
                seller = "没有购物车"
                ship = "没有购物车"
                get_pd_info.append(seller)
                get_pd_info.append(ship)

    # 抓取价格
    if mkp == 'au':
        price = html1.xpath('//span[@class="a-price a-text-price a-size-medium"]/span')
        if price:
            sale_price = price[0].text
        else:
            sale_price = '无售价'
        get_pd_info.append(sale_price)
    else:
        price = html1.xpath('//span[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span')
        if price:
            sale_price = price[0].text
        else:
            sale_price = '无售价'
        get_pd_info.append(sale_price)

    # 抓取标题
    try:
        title = browser.find_element_by_id('productTitle').text
    except:
        title = ''
    get_pd_info.append(title)



    # 无法写入数据库的问题是因为多线程里面不能共用全局里面的session对象，需要在线程里面再重新创建新的session对象
    lock = threading.Lock()
    lock.acquire()
    t = Thread(target=write, args=(get_pd_info, user_id, asin))
    t.start()
    t.join()  # 需要使用join方法堵住主线程的运行，不然主线程跑到下一个去了，ASIN和市场就变了，导致写入数据库的数据有问题
    lock.release()

    browser.close()

def write(get_pd_info, user_id, asin):

    print(get_pd_info)

    pd_infos = sessions.query(Amazon).filter_by(asin=asin,
                                                market=get_pd_info[0],
                                                operation='get_cart',
                                                isdelete='N').first()  # 结合每个ASIN和市场在信息表里面查询到对应的id

    write_pd = Cart(asin=asin, price=get_pd_info[4], seller=get_pd_info[2], ship=get_pd_info[3],
                    pd_info_id=pd_infos.product_id,
                    user_id=user_id,
                    market=get_pd_info[0])
    sessions.add(write_pd)
    sessions.commit()
    print('数据更新成功')

    if pd_infos.goods_name == '':
        pd_infos.goods_name = get_pd_info[5]
        sessions.commit()

    sessions.remove()
