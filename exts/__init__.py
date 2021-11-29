from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bootstrap = Bootstrap()
schedule = BackgroundScheduler(daeon=True)