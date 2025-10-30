# 导入统一的数据库对象
from .models import db

# 定义函数：将 ORM 实例与app核心对象绑定
def init_app_db(app):
    db.init_app(app)  # 关联 app，让 ORM 知道要操作哪个应用的数据库