import json

from flask import Blueprint, request, session, render_template, g, Response

from apps.search_result.get_search import get_search_result
from apps.search_result.model import Add_Search
from apps.user.model import User
from exts import db

sr_bp = Blueprint('sr_bp', __name__, static_folder='../static', template_folder='../templates')

before_req_list = ['/add_search', '/get_search', '/load_keyword']


@sr_bp.before_app_request
def before_req():
    if request.path in before_req_list:
        uid = session.get('uid')
        # print(uid)
        if not uid:
            return render_template('user/login.html')
        else:
            user = User.query.get(uid)
            g.user = user


@sr_bp.route('/add_search', methods=['GET', 'POST'])
def add_search():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        mkp = request.form.get('market')
        page_num = request.form.get('page_num')

        if keyword == "" or mkp == "" or page_num == "":
            return render_template('search_result/add_search.html', user=g.user, msg='关键词或市场或抓取的页数不能为空')
        else:
            if mkp == 'com':
                mkp = 'us'
            elif mkp == 'co.uk':
                mkp = 'uk'
            elif mkp == 'co.jp':
                mkp = 'jp'

            pd_info = Add_Search.query.filter_by(user_id=g.user.user_id, keyword=keyword, market=mkp).all()
            if not pd_info:
                add = Add_Search(keyword=keyword, market=mkp, user_id=g.user.user_id, page_num=page_num)
                db.session.add(add)
                db.session.commit()
                return render_template('search_result/add_search.html', user=g.user, msg='添加成功')
            else:
                return render_template('search_result/add_search.html', user=g.user, msg='添加失败，关键词已经存在')
    return render_template('search_result/add_search.html', user=g.user)


@sr_bp.route('/get_search', methods=['GET', 'POST'])
def get_search():
    if request.method == 'POST':
        mkp = request.form.get('markets')
        keyword = request.form.get('keywords')
        if mkp == "" or keyword == "":
            return render_template('search_result/get_search.html', user=g.user, msg='关键词或市场不能为空')
        else:
            pd_info = Add_Search.query.filter_by(user_id=g.user.user_id, keyword=keyword, market=mkp).first()
            page_num = pd_info.page_num
            if mkp == 'us':
                mkp = 'com'
            elif mkp == 'uk':
                mkp = 'co.uk'
            elif mkp == 'jp':
                mkp = 'co.jp'
            # 开始写抓取搜索排名的部分
            lst = get_search_result(keyword, page_num, mkp)  # 需要接收返回的值

            #搜索结果页为22个的
            if len(lst[0]) == 22:
                #写入数据库，但需要注意区分自然搜索和广告位置
                add = ''

    return render_template('search_result/get_search.html', user=g.user)


@sr_bp.route('/load_keyword', methods=['POST'])
def load_keyword():
    res = []
    if request.method == 'POST':
        mkp = request.values.get('mkp')
        # print(mkp)
        kws = Add_Search.query.filter_by(user_id=g.user.user_id, market=mkp).all()
        for kw in kws:
            dict = {}
            dict['keyword'] = kw.keyword
            res.append(dict)
        return Response(json.dumps(res))
