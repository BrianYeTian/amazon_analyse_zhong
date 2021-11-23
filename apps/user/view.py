from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, g
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
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        nickname = request.form.get('nickname')

        if password == repassword:
            user = User()
            user.username = username
            user.password = generate_password_hash(password)
            user.nickname = nickname

            db.session.add(user)
            db.session.commit()
            return render_template('user/login.html')
    return render_template('user/register.html')


@user_bp.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('passwords')
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


@user_bp.route('/user/check_username')
def check_username():
    input_username = request.args.get('username')
    print(input_username)
    user = User.query.filter(User.username == input_username)
    if len(user):
        return jsonify(code=400, msg='用户名已经被注册')
    else:
        return jsonify(code=200, msg='用户名可用')


@user_bp.route('/homepage')
def homepage():
    return render_template('homepage.html',user=g.user)
