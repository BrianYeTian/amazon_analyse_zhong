from flask import Flask

import settings
from apps.catelog.view import cate_bp
from apps.single_pd.view import sp_bp
from apps.user.view import user_bp
from exts import db, bootstrap
from apps.search_result.view import sr_bp


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(settings.DevelopmentConfig)
    db.init_app(app=app)
    bootstrap.init_app(app=app)
    app.register_blueprint(sp_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cate_bp)
    app.register_blueprint(sr_bp)
    return app
