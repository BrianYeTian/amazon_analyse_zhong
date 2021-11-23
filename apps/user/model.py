from datetime import datetime

from exts import db


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(20), unique=True, nullable=False)
    isdelete = db.Column(db.Boolean, default=True)
    rtime = db.Column(db.DateTime, default=datetime.now)
    __tablename__ = 'tb_user'
