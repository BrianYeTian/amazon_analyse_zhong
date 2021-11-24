import json

from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, g, Response
from werkzeug.security import generate_password_hash, check_password_hash

from apps.user.model import User
from exts import db

user_bp = Blueprint('user_bp', __name__)

before_request_list = ['/']


@user_bp.before_app_request
def before_req():
    if request.path in before_request_list:
        uid = session.get('uid')
        if not uid:
            return render_template('user/login.html')
        else:
            user = User.query.get(uid)
            g.user = user


@user_bp.route('/')
def index():
    return render_template('index.html',user=g.user)


@user_bp.route('/user/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        value = json.loads(request.form.get('value'))
        if value[0]:
            username = value[0]
            password = value[1]
            repassword = value[2]
            nickname = value[3]

            # print(username)

            if password == repassword:
                user = User()
                user.username = username
                user.password = generate_password_hash(password)
                user.nickname = nickname

                db.session.add(user)
                db.session.commit()
                return Response('注册成功！')
            else:
                return Response('注册失败')
        else:
            return Response('请输入用户名或密码')
    return render_template('user/register.html')


@user_bp.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
        users = User.query.filter_by(username=username).all()
        for user in users:
            print(user.password)
            # print(password)
            if check_password_hash(user.password, password):
                session['uid'] = user.user_id
                return redirect(url_for('user_bp.index'))
        else:
            return render_template('user/login.html', msg='用户名或密码有误，请重新登陆！')
    return render_template('user/login.html')


@user_bp.route('/user/logout')
def logout():
    session.clear()
    return redirect(url_for('user_bp.index'))


@user_bp.route('/user/check_username',methods=['POST'])
def check_username():
    input_username = request.form.get('username')
    print(input_username)
    if input_username:
        user = User.query.filter(User.username == input_username).all()
        if user:
            return Response('用户名已被注册')
        else:
            return Response('用户名可用')
    else:
        return Response('请输入用户名')


@user_bp.route('/homepage')
def homepage():
    return render_template('homepage.html',user=g.user)
