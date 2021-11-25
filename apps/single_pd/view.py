import json
import os
import re
import threading
from datetime import datetime
import time
from io import BytesIO

import sqlalchemy
import xlrd
import xlwt as xlwt
from flask import Blueprint, request, session, render_template, g, Response, url_for, make_response, send_from_directory
from flask_login import current_user
from werkzeug.utils import redirect

from apps.single_pd.EU_trace_pd import EU_trace_pd
from apps.single_pd.download import write_to_excel
from apps.single_pd.get_review import get_star_rating
from apps.single_pd.model import Amazon, Trace_pd_info
from apps.single_pd.product_info import get_product_info
from apps.single_pd.trace_pd import pd_trace
from apps.user.model import User
from apps.user.view import user_bp, g
from exts import db
from settings import APP_STATIC
from concurrent.futures import ThreadPoolExecutor

sp_bp = Blueprint('sp_bp', __name__)

before_request_list = ['/dp/get_review', '/dp', '/add_pd', '/query', '/query_all', '/query_by',
                       '/trace_pds', '/del', '/select_asin', 'review_download/delete', '/get_review_download',
                       '/review_download', '/add_by_sheet', '/filter', '/get_asins_chart']

executor = ThreadPoolExecutor()


@user_bp.before_app_request
def before_req():
    if request.path in before_request_list:
        uid = session.get('uid')
        # print(uid)
        if not uid:
            return render_template('user/login.html')
        else:
            user = User.query.get(uid)
            g.user = user


@sp_bp.route('/dp', methods=['GET', 'POST'])
def dp():
    if request.method == 'POST':
        lst = []
        dics = {}

        pd_lst = Amazon.query.filter_by(user_id=g.user.user_id).all()
        for pd in pd_lst:
            dic = {}
            dic['id'] = pd.product_id
            dic['asin'] = pd.asin
            dic['goods_name'] = pd.goods_name
            dic['url'] = pd.url
            dic['market'] = pd.market
            dic['time'] = pd.spider_time

            # print(dic)
            lst.append(dic)
        dics['values'] = lst
        # print(json.dumps(dics))
        return Response(json.dumps(dics))
    else:
        pd_lst = Amazon.query.filter_by(user_id=g.user.user_id).all()
        print(len(pd_lst))
        return render_template('single_product/product_page.html', user=g.user, pd_lst=pd_lst)

    # if request.method == 'POST':
    #     mkp = request.form.get('mkp')
    #     if mkp == 'all':
    #         pd_lst = Amazon.query.filter_by(user_id=g.user.user_id).all()
    #     else:
    #         pd_lst = Amazon.query.filter_by(user_id=g.user.user_id, market=mkp).all()
    #     return render_template('single_product/product_page.html', user=g.user, products=pd_lst)
    # else:
    #     # 把查询的结果传过去
    #     pd_lst = Amazon.query.filter_by(user_id=g.user.user_id).all()
    #     return render_template('single_product/product_page.html', user=g.user, products=pd_lst)


@sp_bp.route('/filter', methods=['POST'])
def filter():
    mkp = request.form.get('mkp')
    # print(mkp,'----')

    lst = []
    dics = {}
    pd_lst = Amazon.query.filter_by(user_id=g.user.user_id, market=mkp).all()
    for pd in pd_lst:
        dic = {}
        dic['id'] = pd.product_id
        dic['asin'] = pd.asin
        dic['goods_name'] = pd.goods_name
        dic['url'] = pd.url
        dic['market'] = pd.market
        dic['time'] = pd.spider_time

        # print(dic)
        lst.append(dic)
    dics['values'] = lst
    # print(json.dumps(dics))
    return Response(json.dumps(dics))


@sp_bp.route('/add_pd', methods=['GET', 'POST'])
def add():
    market = ['https://www.amazon.']
    add_msg = [{'msg': '添加成功'}]
    if request.method == 'POST':
        url = request.form.get('shopurl')
        if url:
            if url[-1] != '/':
                url = url + '/'
            # print(url)
            for mk in market:
                if mk in url:
                    # print(mk)
                    try:
                        goods_name = re.findall(r'https://www.amazon.[\s\S]*?/(.*?)/dp', url)[0]
                    except:
                        goods_name = ''

                    mkp = re.findall(r'https://www.amazon.(.*?)/', url)[0]
                    if goods_name:
                        asin_pat = 'https://www.amazon.' + mkp + '/' + goods_name + '/dp/(.*?)/'
                    else:
                        asin_pat = 'https://www.amazon.' + mkp + '/' + 'dp/(.*?)/'
                    asin = re.findall(asin_pat, url)[0]

                    simple_url = mk + mkp + '/dp/' + asin

                    # 根据匹配到的市场名进行对国家编号进行修改
                    if mkp == 'com':
                        mkp = 'us'
                    elif mkp == 'co.uk':
                        mkp = 'uk'
                    elif mkp == 'co.jp':
                        mkp = 'jp'

                    # 要抓取亚马逊页面信息
                    # brand = get_product_info(url, asin)

                    pd_info = Amazon.query.filter_by(asin=asin, market=mkp).all()
                    if not pd_info:
                        add_good = Amazon(asin=asin, goods_name=goods_name, market=mkp, url=simple_url,
                                          spider_time=time.strftime('%Y-%m-%d', time.localtime()),
                                          user_id=g.user.user_id)
                        db.session.add(add_good)
                        db.session.commit()
                        # print('添加1')

                    else:
                        for pd in pd_info:
                            if pd.market != mkp:
                                add_good = Amazon(asin=asin, goods_name=goods_name, market=mkp, url=simple_url,
                                                  spider_time=time.strftime('%Y-%m-%d', time.localtime()),
                                                  user_id=g.user.user_id)
                                db.session.add(add_good)
                                db.session.commit()
                                # print('添加2')
                            else:
                                print('-------------')
                                add_msg[0]['msg'] = '添加失败，产品已在列表中'
                    return render_template('single_product/add_product.html', user=g.user, add_msg=add_msg)
                else:
                    add_msg[0]['msg'] = '添加失败，请检查填入的链接是否正确'  # 这个地方还有问题，实际上添加成功了，但是提示的是这句话
            return render_template('single_product/add_product.html', user=g.user, add_msg=add_msg)
        else:
            add_msg[0]['msg'] = '添加失败，请输入产品链接'
            return render_template('single_product/add_product.html', user=g.user, add_msg=add_msg)

    return render_template('single_product/add_product.html', user=g.user)


# 批量添加
@sp_bp.route('/add_by_sheet', methods=['POST'])
def add_by_sheet():
    # print(111111)
    market = 'https://www.amazon.'

    urls = []

    if request.method == 'POST':
        ws = request.form.get('data')
        sheets = json.loads(ws)
        # print(sheets)
        for col in sheets:
            for key in col.keys():
                if key == 'URL':
                    urls.append(col['URL'])

        print(urls)

        i = 0
        for url in urls:
            if market in url:
                # print(mk)
                try:
                    goods_name = re.findall(r'https://www.amazon.[\s\S]*?/(.*?)/dp', url)[0]
                except:
                    goods_name = ''

                mkp = re.findall(r'https://www.amazon.(.*?)/', url)[0]
                # print(mkp)
                if goods_name:
                    asin_pat = 'https://www.amazon.' + mkp + '/' + goods_name + '/dp/(.*?)?'
                else:
                    asin_pat = r'https://www.amazon.' + mkp + '/' + 'dp/(.*?)?psc='
                asin = re.findall(asin_pat, url)[0].replace('?', '')
                print(asin)

                simple_url = market + mkp + '/dp/' + asin

                # 根据匹配到的市场名进行对国家编号进行修改
                if mkp == 'com':
                    mkp = 'us'
                elif mkp == 'co.uk':
                    mkp = 'uk'
                elif mkp == 'co.jp':
                    mkp = 'jp'

                # 要抓取亚马逊页面信息
                # brand = get_product_info(url, asin)

                pd_info = Amazon.query.filter_by(asin=asin, market=mkp).all()
                # print('hier')
                if not pd_info:
                    add_good = Amazon(asin=asin, goods_name=goods_name, market=mkp, url=simple_url,
                                      spider_time=time.strftime('%Y-%m-%d', time.localtime()),
                                      user_id=g.user.user_id)
                    db.session.add(add_good)
                    db.session.commit()
                    i += 1
                    # print('添加1')

                else:
                    for pd in pd_info:
                        if pd.market != mkp and pd.user_id != g.user.user_id and pd.asin != asin:
                            add_good = Amazon(asin=asin, goods_name=goods_name, market=mkp, url=simple_url,
                                              spider_time=time.strftime('%Y-%m-%d', time.localtime()),
                                              user_id=g.user.user_id)
                            db.session.add(add_good)
                            db.session.commit()
                            i += 1
                            # print('添加2')
                        # else:
                        #     print('-------------')
                        #     add_msg[0]['msg'] = '添加失败，产品已在列表中'
        #         return render_template('single_product/add_product.html', user=g.user, add_msg=add_msg)
        #     else:
        #         add_msg[0]['msg'] = '添加失败，请检查填入的链接是否正确'  # 这个地方还有问题，实际上添加成功了，但是提示的是这句话
        # return render_template('single_product/add_product.html', user=g.user, add_msg=add_msg)
        msg = '批量添加完成，成功添加' + str(i) + '个' + ';添加失败' + str(len(urls) - i) + '个'
        return Response(json.dumps(msg))


@sp_bp.route('/trace_pds', methods=['GET', 'POST'])
def trace_pds():
    global db
    mkp_url_list = []
    asin_list = []
    if request.method == 'POST':
        asins = request.form.get('asins')  # 为了避免同一asin不同市场的冲突，实际传过来的数据是所选asin在数据库中对应的编号
        id_list = json.loads(asins)
        # print(id_list)
        for pd_id in id_list:
            di = {}
            pd_info = Amazon.query.filter_by(product_id=pd_id).first()
            url = pd_info.url
            mkp = pd_info.market  # 市场需要从前台页面传过来，不然的话一个ASIN对应多个市场的时候就会有问题
            # 将市场和链接组成一个字典，再把多个字典组成列表传参给爬虫程序
            di[mkp] = url
            mkp_url_list.append(di)
            asin_list.append(pd_info.asin)

            # print(mkp_url_list)

    elif request.method == 'GET':
        di = {}
        pd_id = request.args.get('asin')
        pd_info = Amazon.query.filter_by(product_id=pd_id).first()
        url = pd_info.url
        mkp = pd_info.market
        di[mkp] = url
        mkp_url_list.append(di)
        asin_list.append(pd_info.asin)

    # executor.submit(write_to_db, mkp_url_list, asin_list)
    write_to_db(mkp_url_list,asin_list)
    pd_lst = Amazon.query.filter_by(user_id=g.user.user_id).all()
    return render_template('single_product/product_page.html', user=g.user, pd_lst=pd_lst)


def get_pds_info(mkp_url_list, asin_list):
    get_pd_infos = EU_trace_pd(mkp_url_list, asin_list)

    return get_pd_infos
    # 传回来的值是一个包含多个产品信息的列表，需要再修改


def write_to_db(mkp_url_list, asin_list):
    get_pd_infos = get_pds_info(mkp_url_list, asin_list)
    print(get_pd_infos)

    for get_pd_info in get_pd_infos:
        print(get_pd_info)
        print('到这里了1')

        pd_infos = Amazon.query.filter_by(asin=get_pd_info[6],
                                          market=get_pd_info[8]).first()  # 结合每个ASIN和市场在信息表里面查询到对应的id
        print('到这里了2')
        write_pd = Trace_pd_info(asin=get_pd_info[6], price=get_pd_info[0], rating_num=get_pd_info[1],
                                 rating=get_pd_info[2], cate=get_pd_info[3], rank=get_pd_info[4],
                                 inventory=get_pd_info[5], pd_info_id=pd_infos.product_id, user_id=g.user.user_id,
                                 market=get_pd_info[8])
        print(write_pd)
        db.session.add(write_pd)
        db.session.commit()
        print('数据更新成功')

        if pd_infos.goods_name == '':
            pd_infos.goods_name = get_pd_info[7]
            db.session.commit()


@sp_bp.route('/query', methods=['GET', 'POST'])
def query():  # 需要改成根据id查询
    if request.method == 'GET':
        asin = request.args.get('asin')
        pd_list = Trace_pd_info.query.filter_by(pd_info_id=asin).all()
        g.user = current_user
        # all_pd = Trace_pd_info.query.filter_by(user_id=g.user.user_id)
        return render_template('single_product/query_pd.html', user=g.user, pd_list=pd_list)
    # if request.method == 'POST':
    #     pd_list = []
    #     g.user = current_user
    #     pd_id = Amazon.query.filter_by(user_id=g.user.user_id).all()
    #     for pd in pd_id:
    #         pd_info = Trace_pd_info.query.filter_by(pd_info_id=pd).all()
    #         for info in pd_info:
    #             dict = {}
    #             dict['asin'] = info.asin
    #             pd_list.append(dict)
    #     return Response(json.dumps(pd_list))


@sp_bp.route('/query_all', methods=['POST', 'GET'])
def query_all():
    if request.method == 'POST':
        all_list = Trace_pd_info.query.filter_by(user_id=g.user.user_id).all()
        return render_template('single_product/query_pd.html', pd_list=all_list, user=g.user)


@sp_bp.route('/query_by', methods=['POST'])
def query_by():
    if request.method == 'POST':
        mkp = request.form.get('mkp')
        asin = request.form.get('asin')
        print(mkp)
        print(asin)
        if mkp:
            if asin:
                all_list = Trace_pd_info.query.filter_by(user_id=g.user.user_id, market=mkp, asin=asin).all()
            else:
                all_list = Trace_pd_info.query.filter_by(user_id=g.user.user_id, market=mkp).all()
        else:
            all_list = Trace_pd_info.query.filter_by(user_id=g.user.user_id, asin=asin).all()
        return render_template('single_product/query_pd.html', user=g.user, pd_list=all_list)


@sp_bp.route('/del', methods=['POST'])
def del_asin():
    asin = request.form.get('asin')
    print(asin)
    pd_info = Amazon.query.filter_by(product_id=asin).first()
    print(pd_info.asin)
    db.session.delete(pd_info)
    db.session.commit()
    # return redirect(url_for('sp_bp.dp'))

    lst = []
    dics = {}
    pd_lst = Amazon.query.filter_by(user_id=g.user.user_id).all()
    for pd in pd_lst:
        dic = {}
        dic['id'] = pd.product_id
        dic['asin'] = pd.asin
        dic['goods_name'] = pd.goods_name
        dic['url'] = pd.url
        dic['market'] = pd.market
        dic['time'] = pd.spider_time

        # print(dic)
        lst.append(dic)
    dics['values'] = lst
    # print(json.dumps(dics))
    return Response(json.dumps(dics))


@sp_bp.route('/download', methods=['POST'])
def download():
    id_lst = request.form.get('id_lst')
    print(id_lst)

    # id_list = json.loads(id_lst)

    new = write_to_excel(id_lst)
    print(new)
    sio = BytesIO()
    new.save(sio)  # 将数据存储为bytes
    sio.seek(0)
    response = make_response(sio.getvalue())
    response.headers['Content-type'] = 'application/vnd.ms-excel'  # 响应头告诉浏览器发送的文件类型为excel
    response.headers['Content-Disposition'] = 'attachment;filename=newlist.xls'  # 浏览器打开/保存的对话框，data.xlsx-设定的文件名
    # response.write(sio.getvalue())

    return response


# 以下为抓取评价的部分
@sp_bp.route('/select_asin', methods=['POST'])
def select_asin():
    if request.method == 'POST':
        spider_info = Amazon.query.filter_by(user_id=g.user.user_id).all()
        res = []
        for info in spider_info:
            dict = {}
            dict['product_id'] = info.product_id
            dict['asin'] = info.asin
            res.append(dict)
        return Response(json.dumps(res))


@sp_bp.route('/dp/get_review', methods=['GET', 'POST'])
def get_review():
    if request.method == 'POST':
        asin = request.form.get('goods')
        star = request.form.get('good_star')
        mkp = request.form.get('market')
        get_star_rating(star, asin, mkp)
        return render_template('single_product/get_review.html', user=g.user)
    return render_template('single_product/get_review.html', user=g.user)


@sp_bp.route('/review_download', methods=['POST'], endpoint='review_download')
@sp_bp.route('/get_review_download', methods=['GET'], endpoint='get_review_download')
def review_download():
    file_name = os.listdir(APP_STATIC)
    if request.method == 'POST':
        file_list = []
        for i in file_name:
            dict = {}
            dict['file'] = i
            file_list.append(dict)
        return Response(json.dumps(file_list))
    if request.method == 'GET':
        return render_template('single_product/review_download.html', user=g.user)


@sp_bp.route('/review_download/delete', methods=['POST'])
def review_delete():
    if request.method == 'POST':
        file_name = request.values.get('name')
        os.remove(os.path.join(APP_STATIC, file_name))
        return Response('success')


@sp_bp.route('/review_download/<file>', methods=['GET'])
def put_files(file):
    return send_from_directory(APP_STATIC, file, as_attachment=True)


@sp_bp.route('/create_chart', methods=['GET', 'POST'])
def create_chart():
    if request.method == 'POST':
        asins = request.form.get('asins')
        date = request.form.get('date')
        mkp = request.form.get('mkp')
        if asins:
            for asin in json.loads(asins):
                pd = Amazon.query.filter_by(asin=asin, market=json.loads(mkp), user_id=g.user.user_id)
    return render_template('single_product/test1.html')


@sp_bp.route('/get_asins_chart', methods=['POST'])
def get_asins_chart():
    if request.method == 'POST':
        lst = []
        mkp = request.form.get('mkp')
        print(mkp)
        pd_lst = Amazon.query.filter_by(market=mkp, user_id=g.user.user_id)
        if pd_lst:
            for pd in pd_lst:
                dic = {}
                dic['asin'] = pd.asin  # 最好把ID传过去，不然到时候获取asin销量的时候会有问题
                lst.append(dic)
            return Response(json.dumps(lst))
        else:
            return Response(json.dumps([{'msg': '无查询结果'}]))
