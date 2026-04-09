from models import VegetableCategory
from exsitions import db



def init_vegetable_category():
    """给蔬菜序列生成内容，填充到数据库里面"""
    categories = ["豌豆","苦瓜","蒲瓜","茄子","西兰花","卷心菜","灯笼椒","胡萝卜","花菜","黄瓜","木瓜","土豆","南瓜","萝卜","西红柿"]
    category_models = [VegetableCategory(name=category) for category in categories] # 挨个填充
    db.session.add_all(category_models) # 提交里面的内容
    db.session.commit()
    print("蔬菜初始化成功！")