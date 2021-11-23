# usr/env/bin python
# coding=utf-8
import time

from flask import url_for

from exts import db
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from apps.single_pd.model import Review
import datetime
import os
from settings import APP_STATIC


def get_star_rating(star, asin, mkp):
    page = 1
    print("开始爬虫")
    if star == 'all':
        check_rate = Review.query.filter_by(asin=asin).filter_by(market=mkp).all()
    else:
        check_rate = Review.query.filter_by(asin=asin).filter_by(star=star).filter_by(market=mkp).all()
    if len(check_rate) != 0:
        print("删除旧数据")
        for ra in check_rate:
            db.session.delete(ra)
            db.session.commit()

    url = 'https://www.amazon.com/product-reviews/%s/ref=cm_cr_arp_d_hist_1?ie=UTF8&showViewpoints=0&pageNumber=1&reviewerType=all_reviews&filterByStar=%s_star' % (
        asin, star)
    print("正在获取%s市场asin为%s的%s_star的评价" % (mkp, asin, star))
    # chrome_options = Options()
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('window-size=1920x3000')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--hide-scrollbars')
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    # chrome_options.add_argument('--headless')
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # browser = webdriver.Chrome(chrome_options=chrome_options)
    # # browser = webdriver.Chrome('/bin/chromedriver', chrome_options=chrome_options)
    # browser.set_page_load_timeout(40)
    # browser.set_script_timeout(40)
    browser = webdriver.Chrome()
    browser.set_page_load_timeout(40)
    browser.set_script_timeout(40)
    browser.maximize_window()

    browser.get(url)
    time.sleep(1)
    # 方法1：加一个判断，如果是第一页的时候先返回评价的总数量给前段做时间预估。需要评估行不行得通
    # 方法2：分成两个函数，互相调用。在第一次的时候返回评价总数。

    # 抓取评价的地方也还是有问题，当抓取的星级不是全部星级的时候，每页最上方是没有推荐好评和差评的，所以删除掉作者列表中的第一和第二个就会有问题

    try:
        while True:
            print('正在获取第', page, '页评价')
            if browser.find_elements_by_xpath('//*[@id="cm_cr-review_list"]/div/div/span/span[2]/a'):
                browser.find_element_by_xpath('//*[@id="cm_cr-review_list"]/div/div/span/span[2]/a').click()
            time.sleep(2)
            rate_time = browser.find_elements_by_xpath('//*[@class="a-section celwidget"]/span')
            rate_title = browser.find_elements_by_xpath('//*[@class="a-section celwidget"]/div[2]/a[2]/span')
            # name = browser.find_elements_by_xpath('//*[@class="a-section celwidget"]/div[1]/a/div[2]/span')
            name = re.findall('class="a-profile-name">(.*?)</span>', browser.page_source)
            info = browser.find_elements_by_xpath('//*[@class="a-section celwidget"]/div[4]/span/span')
            rating = re.findall('data-hook="review-star-rating"[\s\S]*?class="a-icon-alt">(.*?)</span>',
                                browser.page_source)
            # print(rate_time[1].text)
            # print(rate_title[1].text)
            # print(rating[1])
            if len(rate_title) == 10 and len(name) == 12:
                for i in range(2):
                    name.remove(name[0])

            lst = [len(rate_time), len(rate_title), len(name), len(info), len(rating)]
            print(lst)
            file_name = "%s-%s_star-%s商品评论.csv" % (
                asin, star, datetime.datetime.now().strftime('%Y-%m-%d'))
            with open(os.path.join(APP_STATIC, file_name), "a",
                      encoding='utf-8-sig') as f:
                for s in range(min(lst)):
                    # print(min(lst))
                    # 有个问题，直接取最小值的话，可能会出现中间部分遇到vine评价的，会出现信息匹配不上的问题
                    f.write("%s,%s,%s,%s,%s\n" % (name[s].replace("\n", "").replace(",", "，"),
                                                  rate_time[s].text.replace("\n", "").replace(",", "，"),
                                                  rate_title[s].text.replace("\n", "").replace(",", "，"),
                                                  info[s].text.replace("\n", "").replace(",", "，"),
                                                  rating[s].replace('\n', ""),))

                    r_info = Review(asin=asin, star=rating[s].replace("\n", ""), market=mkp,
                                    author=name[s].replace("\n", "").replace(",", "，"),
                                    rating_time=rate_time[s].text.replace("\n", "").replace(",", "，"),
                                    rating_title=rate_title[s].text.replace("\n", "").replace(",", "，"),
                                    content=info[s].text.replace("\n", "").replace(",", "，"))

                    try:
                        db.session.add(r_info)
                        db.session.commit()
                        print("更新数据成功")
                    except:
                        db.session.rollback()
            try:
                browser.find_element_by_xpath('//*[@class="a-text-center celwidget a-text-base"]/ul/li[2]/a').click()
            except:
                break
            page += 1
    except Exception as e:
        # db.session.close()
        print(e)
        print("评论抓取结束")
        return "success"

    browser.close()

# if __name__ == '__main__':
#     get_star_rating('five', 'B09BFGB8NS', 'us')
