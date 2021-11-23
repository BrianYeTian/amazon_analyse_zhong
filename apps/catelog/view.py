import json
import re

from flask import Blueprint, request, session, render_template, g, Response

from apps.catelog.model import Save_cate
from apps.user.model import User
from exts import db

cate_bp = Blueprint('cate_bp', __name__)

before_req_list = ['/get_cate', '/load_cate', '/add_cate']


@cate_bp.before_app_request
def before_req():
    if request.path in before_req_list:
        uid = session.get('uid')
        # print(uid)
        if not uid:
            return render_template('user/login.html')
        else:
            user = User.query.get(uid)
            g.user = user


@cate_bp.route('/get_cate', methods=['GET', 'POST'])
def get_cate():
    if request.method == 'POST':  # post请求处理爬取目录信息
        pass
    if request.method == 'GET':
        pass
    return render_template('catelog/get_catelog.html', user=g.user)


# 通过ajax动态加载已经添加的目录和市场
@cate_bp.route('/load_cate', methods=['POST'])
def load_cate():
    res = []
    if request.method == 'POST':
        mkp = request.values.get('mkp')  # 两种方案：1. 先选择市场，那么根据市场筛选出所有的类目并返回；2. 先选择目录，那么市场肯定就只会有一个
        print(mkp)
        if mkp == '请选择市场':
            spider_info = Save_cate.query.filter_by(user_id=g.user.user_id).all()
            for info in spider_info:
                dict = {}
                dict['cate_name'] = info.cate_name
                dict['market'] = info.market
                res.append(dict)
                return Response(json.dumps(res))
        else:  # 选了市场以后加载不出来目录，需要再看看
            print('到这里了')
            spider_info = Save_cate.query.filter_by(user_id=g.user.user_id, market=mkp).all()
            for info in spider_info:
                dict = {}
                dict['cate_name'] = info.cate_name
                dict['id'] = info.id
                res.append(dict)
            print(res)
            return Response(json.dumps(res))


# 添加类目信息到数据库
@cate_bp.route('/add_cate', methods=['POST'])
def add_cate():
    result = '添加成功'
    if request.method == 'POST':
        cate_url = request.form.get('cate_url')
        cate_name = request.form.get('cate_name')
        print(cate_url)
        print(cate_name)
        if cate_url == "":
            result = '添加失败，请输入需要添加的目录'
            return Response(result)
        elif 'https://www.amazon.' in cate_url and 'gp/bestsellers' in cate_url:
            mkp = re.findall(r'https://www.amazon.(.*?)/gp', cate_url)[0]
            if cate_name == "":
                cate_name_pat = 'https://www.amazon.' + mkp + '/gp/bestsellers/(.*?)/'
                cate_name = re.findall(cate_name_pat, cate_url)[0]
            if mkp == 'com':
                mkp = 'us'
            elif mkp == 'co.uk':
                mkp = 'uk'
            elif mkp == 'co.jp':
                mkp = 'jp'

            cate_num = re.findall(r'(\d+)/ref', cate_url)[0]

            cate_info = Save_cate.query.filter_by(user_id=g.user.user_id, cate_url=cate_url).all()
            if not cate_info:
                addCate = Save_cate(cate_name=cate_name, market=mkp, cate_num=cate_num, cate_url=cate_url,
                                    user_id=g.user.user_id)
                db.session.add(addCate)
                db.session.commit()
                return Response(result)
            else:
                result = '该类目已经添加，请直接抓取类目信息'
                return Response(result)
