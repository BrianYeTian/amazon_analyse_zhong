from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from apps import create_app
from exts import db, schedule
from apps.user.model import User
from apps.single_pd.model import Amazon,Review,Sales_Data
from apps.catelog.model import Catelog
from apps.search_result.model import Add_Search, Search_result

app = create_app()

manager = Manager(app=app)
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
    # schedule.start()
