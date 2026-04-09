from flask import g,redirect



"""这里保护用户密码不被泄露，所以用封装"""
def login_required(func):
    """保护指定的视图函数（接口 / 页面），只有已登录的用户才能访问，未登录用户会被自动跳转到登录页。"""
    def inner(*args, **kwargs):
        """定义内部函数 inner（实际执行的逻辑包装器），接收任意参数（适配不同视图函数）,进行判断"""
        if g.user: # 如果你已经登录，你可以访问
            return func(*args, **kwargs)
        else:
            return redirect('/login') # 未登录，跳转到登录界面

    return inner

