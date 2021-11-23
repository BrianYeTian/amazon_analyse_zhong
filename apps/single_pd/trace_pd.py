import re
import time

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


def add_zip(mkp, zipp):
    try:
        if mkp == 'us':
            zipp.send_keys('10041')
        elif mkp == 'de':
            zipp.send_keys('04178')
        elif mkp == 'fr':
            zipp.send_keys('75020')
        elif mkp == 'uk':
            zipp.send_keys('NW1 6XE')
        elif mkp == 'jp':
            zipp.send_keys('190 0155')
        elif mkp == 'it':
            zipp.send_keys('00185')
        elif mkp == 'es':
            zipp.send_keys('28028')

        time.sleep(0.5)
    except:
        pass


def get_rank(mkp, page_resource):
    mkp_cate_lst = []
    try:
        if mkp == 'us':
            rank = re.findall('''#(\d+) in <a href''', page_resource)
            cate = re.findall('''#''' + str(rank[0]) + ''' in <a href[\s\S]*?>(.*?)</a></span>''', page_resource)

        elif mkp == 'de':
            rank = re.findall('''Nr. (\d+) in <a''', page_resource)
            cate = re.findall('''Nr. ''' + str(rank[0]) + ''' in <a href[\s\S]*?>(.*?)</a></span>''', page_resource)
        # 以下待改
        elif mkp == 'fr':
            rank = re.findall('''(\d+) en <a href''', page_resource)
            cate = re.findall(str(rank[0]) + ''' en <a href[\s\S]*?>(.*?)</a>''', page_resource)

        elif mkp == 'uk':
            rank = re.findall('''(\d+) in <a href''', page_resource)
            cate = re.findall(str(rank[0]) + ''' in <a href[\s\S]*?>(.*?)</a></span>''', page_resource)

        elif mkp == 'jp':
            rank = re.findall('''- (.*?)<a href''', page_resource)
            cate = re.findall('''- ''' + str(rank[0]) + ''' in <a href[\s\S]*?>(.*?)</a></span>''', page_resource)
        elif mkp == 'it':
            rank = re.findall('''n. (\d+) in <a href''', page_resource)
            cate = re.findall(str(rank[0]) + ''' in <a href[\s\S]*?>(.*?)</a></span>''', page_resource)

        elif mkp == 'es':
            rank = []
            rank_0 = re.findall('''<span>(.*?) en <a href''', page_resource)
            rank.append(rank_0[0].replace('nº', ''))
            print(rank)
            cate = re.findall(str(rank_0[0]) + ''' en <a href[\s\S]*?>(.*?)</a></span>''', page_resource)
        mkp_cate_lst.extend(rank)
        mkp_cate_lst.extend(cate)
    except:
        mkp_cate_lst.append('无排名')
        mkp_cate_lst.append('无目录')

    return mkp_cate_lst


def zip_or_not(times):
    if times == 0:
        return 1
    else:
        return 0


def pd_trace(url_mkps, asin_list):
    print('正在获取数据')
    browser = webdriver.Chrome()
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

    de_time = 0
    us_time = 0
    fr_time = 0
    it_time = 0
    es_time = 0
    uk_time = 0
    jp_time = 0

    for url_mkp in url_mkps:
        for mkp, url in url_mkp.items():
            print(mkp, url)
            mkp_list.append(mkp)
            amazon_url = re.findall('(.*?)/dp', url)
            browser.get(amazon_url[0])
            try:
                acpt_cookie = browser.find_element_by_id('sp-cc-accept')
                acpt_cookie.click()
            except:
                pass
            browser.refresh()
            time.sleep(2)



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
                add_zip(mkp, zipp)
                zipp.send_keys(Keys.ENTER)
            except:
                pass
            time.sleep(1)

            inventory = []

            browser.get(url)
            time.sleep(1)

            page_resource = browser.page_source
            time.sleep(1)
            html1 = etree.HTML(page_resource)

            # 获取目录排名信息
            rank_cate = get_rank(mkp, page_resource)
            rank = rank_cate[0]
            cate = rank_cate[1]

            try:
                title = browser.find_element_by_id('productTitle').text
            except:
                title = ''

            try:
                sale_price = browser.find_element_by_id('priceblock_saleprice').text
            except:
                sale_price = []

            if len(sale_price) == 0:
                try:
                    sale_price = browser.find_element_by_id('priceblock_ourprice').text
                except:
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

            # 抓取常规价格，避免在做闪促导致无法加入购物车
            try:
                price = html1.xpath('//span[@class="a-size-base gb-accordion-inactive"]')
                if len(price):
                    normaleprice = browser.find_element_by_xpath('//span[@class="a-size-base gb-accordion-inactive"]')
                    normaleprice.click()
                    time.sleep(1)
                add_to_cart = browser.find_element_by_id('add-to-cart-button')
                add_to_cart.click()
                time.sleep(3)
                ActionChains(browser).move_by_offset(300, 50).click().perform()
                time.sleep(1)
                ActionChains(browser).move_by_offset(-300, -50).perform()
                time.sleep(0.5)

                browser.get(amazon_url[0] + '/gp/cart/view.html/ref=dp_atch_dss_cart?')
                time.sleep(1)
                Menge = browser.find_element_by_xpath(
                    '//span[@class="a-dropdown-label"]' and '//span[@class="a-dropdown-prompt"]')
                Menge.click()
                time.sleep(0.5)
                dropdown_meng = browser.find_element_by_xpath(
                    '//option[@data-a-css-class="quantity-option  quantity-option-10"]')
                dropdown_meng.click()
                time.sleep(1)
                fill_num = browser.find_element_by_name('quantityBox')
                fill_num.send_keys('999')
                fill_num.send_keys(Keys.ENTER)
                time.sleep(1)
                page_source = browser.page_source
                html = etree.HTML(page_source)
                data = html.xpath('//span[@id="sc-subtotal-label-buybox"]')
                for f in data:
                    b = f.text
                    a = b.split()
                    c = ''.join(a)
                    pat = re.compile(r'[\s\S]*?[(](\d+)[\s\S]*?[)]')
                    result = pat.findall(c)
                for x in result:
                    inventory.append(x)

                # 清空购物车
                time.sleep(1)
                clear = browser.find_elements_by_xpath('//div[@class="a-row sc-action-links"]/span')
                for i in range(0, 1):
                    a = clear[i]
                    cleartext = a.get_attribute('data-old-value')
                cleartext1 = int(cleartext)
                if cleartext1 >= 10:
                    for y in range(0, 3):
                        clear1 = browser.find_element_by_name('quantityBox')

                        clear1.send_keys(Keys.BACKSPACE)
                    clear1.send_keys(Keys.ENTER)
                else:
                    clear = browser.find_element_by_xpath(
                        '//span[@class="a-dropdown-label"]' and '//span[@class="a-dropdown-prompt"]')
                    clear.click()
                    clear_menge = browser.find_element_by_xpath(
                        '//option[@value="0"]')
                    clear_menge.click()
                time.sleep(1)
            except:
                inventory.append(0)

            sales_price_list.append(sale_price)
            rating_num_list.append(rating_num)
            rating_list.append(rating[0])
            cate_list.append(cate)
            rank_list.append(rank)
            inventory_list.append(inventory[0])
            title_list.append(title)

    browser.close()

    lst = list(zip(sales_price_list, rating_num_list, rating_list, cate_list, rank_list, inventory_list, asin_list,
                   title_list, mkp_list))

    return lst

# data = pd_trace([{'es':'https://www.amazon.es/dp/B07MNFH1PX'}],['B07MNFH1PX'])
# print(data)
