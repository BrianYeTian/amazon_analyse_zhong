from datetime import datetime

from exts import db


class Add_Search(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    keyword = db.Column(db.String(500), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    page_num = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.user_id'), nullable=False)
    user = db.relationship('User', backref='Add_Search')


class Search_result(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    asin = db.Column(db.String(15), nullable=False)
    title = db.Column(db.String(1000))
    rating = db.Column(db.String(50))
    rating_num = db.Column(db.String(10))
    price = db.Column(db.String(15))
    rank = db.Column(db.String(100))
    keyword = db.Column(db.String(500), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
