class Config:
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/amazon'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/amazon5'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'sdiufbiosdbfiouvah389y534u25890u23o8rjo'
    threaded = True


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = 'development'


import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'download_files')
