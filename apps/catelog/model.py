from datetime import datetime

from exts import db


class Catelog(db.Model):
    __tablename__ = 'cate_info'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(1000), nullable=True)
    asin = db.Column(db.String(15), nullable=True)
    price = db.Column(db.String(10))
    rank = db.Column(db.Integer)
    rating = db.Column(db.String(20))
    rating_num = db.Column(db.Integer)
    cate_num = db.Column(db.String(100), nullable=True)
    cate = db.Column(db.String(100))
    update_time = db.Column(db.DateTime, default=datetime.now)
    catelog_id = db.Column(db.Integer, db.ForeignKey('add_cate.id'), nullable=False)
    catelog = db.relationship('Save_cate', backref='cateInfo')
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.user_id'), nullable=True)
    user = db.relationship('User', backref='catelog')


class Save_cate(db.Model):
    __tablename__ = 'add_cate'
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    cate_name = db.Column(db.String(100))
    market = db.Column(db.String(10), nullable=False)
    cate_num = db.Column(db.String(20), nullable=False)
    cate_url = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.user_id'), nullable=False)
    user = db.relationship('User', backref='add_cate')
