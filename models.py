from exsitions import db
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import Integer,String,Text,ForeignKey,DateTime,Float
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from typing import List


class User(db.Model):
    """这里创建了一个用户的表，记录了用户的名字，密码，邮箱"""
    __tablename__ = "user" # 本质是 “ORM自定义表名”，Django里面不能用
    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)  # 给用户标上序号，方便管理。Integer：整数，primary_key：数据库表中用于唯一标识每条记录的核心字段属性
    username: Mapped[str] = mapped_column(String(50),nullable=False) # 是否允许留空：nullable
    _password: Mapped[str] = mapped_column(String(256),nullable=False)
    email: Mapped[str] = mapped_column(String(200),nullable=False)

    vegetables: Mapped["Vegetable"] =relationship("Vegetable",back_populates="publisher")  # 这里和蔬菜的发布商关联，一对多，因为外键不在这里

    def __init__(self, *args,**kwargs):
        """这里是对password的加密和反加密，方便传入和取出"""
        # 从关键字参数中获取用户传入的明文密码
        password = kwargs.get("password")
        if password:    # 若传入了密码，从 kwargs 中删除"password"键 原因：避免父类（如SQLAlchemy模型）直接将明文密码映射到数据库字段
            kwargs.pop("password")
        # 调用父类构造方法，初始化其他字段（如username、id等非密码字段
        super().__init__(*args, **kwargs)
        # 将获取到的明文密码赋值给self.password，触发下面的@password.setter自动加密
        self.password = password


    @property
    def password(self):
        """这是管理密码的读取"""
        # 对外提供统一读取接口，返回加密后的哈希值（隐藏底层私有变量）
        # 外部执行 user.password 时，实际获取的是 self._password（加密后的值）
        return self._password


    @password.setter
    def password(self, raw_password):
        """这里是对密码的加密"""
        # 拦截所有对self.password的赋值，自动将明文密码加密成哈希值，generate_password_hash：明文转哈希的工具函数（如werkzeug.security提供）
        self._password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """这里是对登录验证的处理"""
        # 验证明文密码：将输入的明文加密后，与存储的哈希值对比，check_password_hash：哈希值与明文的校验工具函数（如werkzeug.security提供）
        return check_password_hash(self.password, raw_password)  # 返回True（密码正确）或False（密码错误）




class VegetableCategory(db.Model):
    """创建一个蔬菜名和序列的类，方便显示的全部蔬菜管理"""
    __tablename__ = "vegetable_category"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True) # 定义蔬菜的序列
    name: Mapped[str] = mapped_column(String(100)) # 蔬菜名

    vegetables: Mapped[List["Vegetable"]] = relationship("Vegetable",back_populates="category")
    # 这里是外键，也相关蔬菜对应




class Vegetable(db.Model):
    """这里才是创建蔬菜的地方，记录你等级蔬菜的名字和相关信息，并对于相关序列"""
    __tablename__ = "vegetable"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)  # Text:文本
    price: Mapped[float] = mapped_column(Float)
    picture: Mapped[str] = mapped_column(String(200))
    mobile: Mapped[str] = mapped_column(String(100))
    place: Mapped[str] = mapped_column(String(200))
    provider: Mapped[str] = mapped_column(String(100))
    pub_date: Mapped[datetime] = mapped_column(DateTime,default=datetime.now) # DateTime：时间的记录

    category_id: Mapped[int] = mapped_column(Integer,ForeignKey("vegetable_category.id")) # # 外键：绑定分类表的主键
    category: Mapped[VegetableCategory] = relationship("VegetableCategory",back_populates="vegetables")
    # # ORM关联：一个分类对应多个蔬菜
    publisher_id: Mapped[int] = mapped_column(Integer,ForeignKey("user.id"))    # # 外键：绑定用户表的主键
    publisher: Mapped[User] = relationship("User",back_populates="vegetables") # ORM关联：一个用户对应多个蔬菜





class EmailCode(db.Model):
    """这里是记录邮箱和验证码的地方，方便验证和验证的时效性"""
    __tablename__ = "email_code"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    code: Mapped[str] = mapped_column(String(10))  # 验证码，我发出它会记录
    email: Mapped[str] = mapped_column(String(100))
    create_time: Mapped[datetime] = mapped_column(DateTime,default=datetime.now) # 保证验证的时效性