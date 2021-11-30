from datetime import datetime

from exts import db


class Amazon(db.Model):
    __tablename__ = 'product_info'
    # __abstract__ = True
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asin = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(20), nullable=False)
    goods_name = db.Column(db.String(1000), nullable=False)
    # brand = db.Column(db.String(20), nullable=False)
    # release_date = db.Column(db.DateTime, default='')
    url = db.Column(db.String(500), nullable=False)
    limit = db.Column(db.String(10), default="N")
    isdelete = db.Column(db.String(10), default='N')
    operation = db.Column(db.String(100),default=None)
    spider_time = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.user_id'), nullable=False)
    user = db.relationship('User', backref='pd_info')


class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asin = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10),nullable=False)
    star = db.Column(db.String(10), nullable=False)
    author = db.Column(db.String(1000), nullable=False)
    rating_time = db.Column(db.String(300), nullable=False)
    rating_title = db.Column(db.String(2000), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Sales_Data(db.Model):
    __tablename__ = "sales_data"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asin = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(1000), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    stock = db.Column(db.Integer, nullable=False)


class Trace_pd_info(db.Model):
    __tablename__ = "trace_pd"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asin = db.Column(db.String(10), nullable=False)
    price = db.Column(db.String(10))
    rating_num = db.Column(db.String(20))
    inventory = db.Column(db.String(50))
    rank = db.Column(db.String(10))
    cate = db.Column(db.String(100))
    rating = db.Column(db.String(100))
    update_date = db.Column(db.DateTime, default=datetime.now)
    pd_info_id = db.Column(db.ForeignKey('product_info.product_id'))
    user_id = db.Column(db.ForeignKey('tb_user.user_id'))
    pd_info = db.relationship('Amazon', backref='trace_pd')
    market = db.Column(db.String(10), nullable=False)

class Cart(db.Model):
    __tablename__="cart"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asin = db.Column(db.String(10), nullable=False)
    price = db.Column(db.String(10))
    market = db.Column(db.String(10), nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.now)
    seller = db.Column(db.String(100))
    ship=db.Column(db.String(100))
    pd_info_id = db.Column(db.ForeignKey('product_info.product_id'))
    pd_info = db.relationship('Amazon', backref='get_cart')
    user_id = db.Column(db.ForeignKey('tb_user.user_id'))
