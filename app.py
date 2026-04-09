
from flask import Flask,render_template,request,jsonify,session,redirect,g,send_from_directory
from sympy.integrals.meijerint_doc import category

import config
from exsitions import db,migrate,mail
from models import User,EmailCode,Vegetable,VegetableCategory
from flask_mail import Message
import random
import string
from datetime import datetime,timedelta
import commands
from decorators import login_required
import uuid
import os
# from dlmodel import predict


app = Flask(__name__)
# 导入数据库，好用sql
app.config.from_object(config)
# 链接数据库
db.init_app(app)
migrate.init_app(app,db)
mail.init_app(app)

# 创建命令，让系统知道init-category是初始化提交蔬菜的意思
app.cli.command("init-category")(commands.init_vegetable_category)

# 添加装饰器，让每一页HTML的登录，渲染都能用到数据库里面的东西
@app.before_request
# app.before_request 会把被装饰的函数，添加到 Flask 应用实例（app）的[请求前置钩子列表]
def before_request():
    """所有请求处理前，初始化当前请求的登录用户信息"""
    user_id = session.get("user_id")
    # 从 Session 中取出用户登录后存储的 user_id（登录时会把 user_id 存入 session）
    if user_id: # 判断是否存在
        user = db.session.get(User,user_id) # 若存在 user_id，从数据库查询对应的用户对象
        # 线程全局
        g.user = user # 3. 把用户对象存入 Flask 的请求全局变量 g 中（本次请求全程可用)
    else:
        g.user = None  # 若不存在 user_id（未登录），g.user 设为 None


@app.context_processor
# @app.context_processor 装饰器是Flask 框架的 “特殊标记，自动把被装饰的函数归类为「上下文处理器」，并在模板渲染的关键时机自动执行它。
def context_processor():
    """在所有模板渲染之前，自动注入全局可用的变量"""
    # 查询数据库：获取所有蔬菜分类（比如叶菜类、根茎类、瓜茄类等
    categories = db.session.scalars(db.select(VegetableCategory)).all() # scalars() 取出查询结果的标量值，all() 转成列表
    return {
        'user': g.user,    # 把全局 g 中的登录用户信息注入模板，上面仅仅是存入而已
        'categories': categories   # 把蔬菜分类列表注入模板
    }



@app.route('/')
def index():
    """获得蔬菜的标签和相关信息，等下可以提交到HTML渲染"""
    # 规定好：前端传输category参数，通过query string的形式，即query string 的 URL：http://你的网站/?category=1
    category_id = request.args.get('category',type=int)
    if category_id:
        stmt = db.select(Vegetable).where(Vegetable.category_id == category_id) # 这里通过网站URL的category=得到所要蔬菜id
    else:
        stmt = db.select(Vegetable) # 没有专门提出就展示全部
    # 展示全部
    vegetables = db.session.scalars(stmt.order_by(Vegetable.pub_date.desc())).all()

    return render_template('index.html',vegetables=vegetables,category_id=category_id)


@app.post('/logout')
def logout():
    """这里是退出登录的地方，会清空(clear)session(钩子)里面的数据"""
    # 清除session，形成未登录状态
    session.clear()
    return redirect('/')

@app.route("/login",methods=['GET','POST']) # 规定只有GET和POST两种方式
def login():
    """这里是登录页面，会在URL里面挨个得知email，password，并且确认remember"""
    if request.method == "GET":  # 如果是get请求，就回到主页面
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        user = db.session.scalar(db.select(User).where(User.email==email)) # 这里是搜索数据库里面是否有该用户
        if user and user.check_password(password):    # 如果有该用户，且该用户密码正确
            session['user_id'] = user.id   # 提供钩子，使其可以在成为全局变量
            if remember:  # 如果确认已点击
                # 设置parmanent=True,那么会31天过期，31天内再次打开浏览器访问网站，Cookie 会自动发给后端；
                session.permanent = True  # 浏览器把 Session ID 存在「硬盘 Cookie」中，Cookie 会标注[过期时间]默认 31 天
            return redirect('/')
        else:
            print("密码或邮箱错误!")
            return redirect('/login')



@app.route("/pub",methods=['GET','POST'])  # 规定只有GET和POST两种方式
@login_required  # 这个是判断是否有全局变量,如果没有，拦截，转到登录地点，详情看装饰器
def pub():
    """这里是发表路径，先get，后post，得到相关信息提交到数据库"""
    if request.method == "GET":# if GET 是 “打开发布表单”，else POST 是 “提交表单数据”，两者是「先有页面，后有提交」的先后关系，缺一不可。
        categories = db.session.scalars(db.select(VegetableCategory)).all()
        return render_template('pub.html',categories=categories)
    else:
        # 收集信息
        picture = request.form.get('picture')
        category_id = request.form.get('category')
        name = request.form.get('name')
        content = request.form.get('content')
        price = request.form.get('price')
        place = request.form.get('place')
        provider = request.form.get('provider')
        mobile = request.form.get('mobile')
        # 排列，方便上交的对应
        vegetable = Vegetable(
            name=name,
            price=price,
            place=place,
            provider=provider,
            mobile=mobile,
            category_id=category_id,
            content=content,
            picture=picture,
            publisher_id=g.user.id
        )
        db.session.add(vegetable) # 上交修改
        db.session.commit()  # 提交修改
        return redirect('/') # 返回主页面



@app.post("/upload/picture")
def upload_picture():
    """这里是对上传图片的修改，并且重命名，防止重名"""
    # 让用户上传图片的时候，图片的name为picture
    picture = request.files.get('picture')
    # 重新给图片命名
    # abc.jpg => ['abc','jpg']
    ext = picture.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    picture_path = os.path.join(app.config['MEDIA_DIR'], filename)
    # 在Flask中，request.files.get('picture')获取的是一个文件对象（类似Python的File对象）。
    # 它的save()方法允许你指定一个新的路径和文件名，相当于 “把文件复制 / 移动到新位置，并以新名字保存”。
    picture.save(picture_path)

    # ai功能的废弃
    # # 预测蔬菜分类
    # category_name = predict(picture_path)  # 通过模型的判断返还蔬菜名字，自动匹配
    # # 根据返还回来的蔬菜名，让其实现对蔬菜的定位
    # category = db.session.scalar(db.select(VegetableCategory).where(VegetableCategory.name==category_name))

    # 让前端返回相关信息
    return jsonify({
        "result":True,
        "filename":filename,
        "category":{"id":0,"name":"请手动选择"}
    })



@app.route("/register",methods=['GET','POST'])
def reg():
    """这里是注册，会用到验证码和验证码的时效"""
    if request.method == "GET": # 先get获取网页的HTML渲染
        return render_template('register.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        code = request.form.get('code') # 获取相关信息，提交到修改那里去
        code_model = db.session.scalar(db.select(EmailCode).where(EmailCode.email == email,EmailCode.code == code))
        # timedelta
        # 这里就验证了如果验证码不同或者验证码过期的情况
        if not code_model or (datetime.now() - code_model.create_time) > timedelta(minutes=5):
            return jsonify({'result':False,'message':"请输入正确的验证码！"})
        user = User(username=username,email=email,password=password) # 统一到user里面
        db.session.add(user)  # 增加修改
        db.session.commit()   # 提交修改
        return jsonify({'result':True,'message':None})  # 反映是否成功


@app.get("/email/code")
def get_email_code():
    """这里是对验证码的设计，保证用户接收到正确信息的验证码，并把验证码上交到数据库，实现验证码验证"""
    # /email/code?email=abc@qq.com
    email =  request.args.get('email')
    if not email:
        return jsonify({'result':False,"message":"请输入邮箱!"})
   # 生成验证码
    source = string.digits * 4
    code = "".join(random.sample(source, 4))
    message = Message(  # 这里规定了验证码的格式，让人一眼看出来验证码是哪里来的，来干什么
        subject="【小乐蔬菜供应商】注册验证码",
        recipients=[email],
        body=f"【小乐蔬菜供应商】注册验证码：{code}"
    )
    try:  # 这里进行发验证码，如果失败，返还错误。
        mail.send(message)
    except Exception as e:
        return jsonify({'result':False,"message":str(e)})
    # mecached/redis
    code_model = EmailCode(code=code,email=email) # 统一验证码格式，方便提交
    db.session.add(code_model) # 创建修改
    db.session.commit()  # 提交修改
    return jsonify({'result':True,"message":None})



@app.route("/detail/<int:vegetable_id>")
def detail(vegetable_id):
    """这里是对蔬菜详细信息页的后端，获得蔬菜序号和蔬菜"""
    vegetabler = db.session.get(Vegetable,vegetable_id)
    return render_template('detail.html',vegetable=vegetabler)


@app.route("/media/<filename>")
def media(filename):
    """这里是提供服务器本地MEDIA_DIR目录下文件的HTTP访问能力,
    让浏览器能通过URL直接预览/下载上传的媒体文件（如蔬菜发布的图片）限制文件访问范围仅为MEDIA_DIR，防止路径遍历攻击，保证服务器安全"""
    return  send_from_directory(config.MEDIA_DIR,filename) # Flask内置函数，安全地从指定目录发送文件

if __name__ == '__main__':
    # 关键修改：host='0.0.0.0' 允许外部访问，port可保持5000或自定义
    app.run(host='0.0.0.0', port=5000, debug=True)


# https://www.whatismyip.com/
# 172.26.108.52