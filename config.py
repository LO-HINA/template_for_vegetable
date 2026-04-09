import os
from dotenv import load_dotenv
"""相关密码，数据库，电脑接口的配置"""
load_dotenv()

# session密码的设置
"""里面的东西对现在的你来说就是随便填，加密相关的"""
SECRET_KEY = os.environ.get("SECRET_KEY","")  # SECRET_KEY 是 Python Web 框架（最典型的是 Django）中用于安全加密、签名的核心密钥

# 配置路径
"""因为要提交给flask库，有这个确定了路径，规避一些错误"""
# os.path.dirname(__file__)：获取__file__的「目录部分」（即去掉文件名，只保留所在文件夹路径）即HTML_study路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 将上面的「相对目录路径」转换成「绝对路径」
MEDIA_DIR = os.path.join(BASE_DIR, "media")    # 上传文件保存在这里上交



"""连接到我的mysql，无所谓我用的什么运行mysql软件"""
# MySQL所在的主机名
HOSTNAME = os.environ.get("DB_HOSTNAME", "")
# MySQL监听的端口号，默认3306
PORT = 3306
# 连接MySQL的用户名，读者用自己设置的
USERNAME = os.environ.get("DB_USERNAME", "")
# 连接MySQL的密码，读者用自己的
PASSWORD = os.environ.get("PASSWORD", "")
# MySQL上创建的数据库名称
DATABASE = "sell_thing"

# 如果驱动程序是mysqlclient，那么以下前缀就是：mysql+mysqldb
# 如果驱动程序是pymysql，那么以下前缀就是：mysql+pymysql
SECRET = os.environ.get("SECRET", "")
SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"  # 拼接在一起
SQLALCHEMY_TRACK_MODIFICATIONS = False


"""验证码那里要用到，qq开启相关作用，可以发验证码给别人"""
# 邮箱配置
MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "")
MAIL_PORT = int(os.environ.get("MAIL_PORT", ""))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")  # qq用户
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")  # 从qq开启功能哪里你会拿到这串密码
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "") # qq用户
