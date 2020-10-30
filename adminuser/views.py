from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from adminuser.models import AdminUser

# 管理员登录
def adminLogin(request):
    if request.method == 'GET':
        if 'adminname' in request.COOKIES:
            username = request.COOKIES.get('adminname')
            password = request.COOKIES.get('adminpassword')
            checked = 'checked'
        else:
            username = ''
            password = ''
            checked = ''
        return render(request, 'admin_login.html', {'adminname': username, 'adminpassword': password, 'checked': checked})
    else:
        # 接收数据
        username = request.POST.get('adminname')
        password = request.POST.get('adminpassword')

        # 校验数据
        if not all([username, password]):
            return render(request, 'admin_login.html', {'errmsg': '数据不完整'})

        # 业务处理:登录校验
        user = AdminUser.objects.filter(admin_name=username, admin_password=password).first()
        # 用户名密码正确
        if user is not None:
            print('找到了')

            # 获取登录后所要跳转到的地址
            # 默认跳转到首页
            next_url = request.GET.get('next', reverse('adminuser:adminIndex'))

            # 跳转到next_url
            response = redirect(next_url)  # HttpResponseRedirect

            # 判断是否需要记住用户名

            # 记住用户名
            response.set_cookie('adminname', username, max_age=7 * 24 * 3600)
            response.set_cookie('adminpassword', password, max_age=7 * 24 * 3600)
            print('记住了')

            # 返回response
            return response
        else:
            # 用户名或密码错误
            return render(request, 'admin_login.html', {'errmsg': '用户名或密码错误'})

# 显示首页
def adminIndex(request):
    username = request.COOKIES.get('adminname')
    if username:
        print('ok')
        return render(request, 'admin_index.html', {'adminname':username})
    else:
        print('error')
        return redirect(reverse('adminuser:adminlogin'))

# 知识库查询
def knowledgebase(request):
    return render(request, 'searchkb.html')

# 欢迎页
def welcome(request):
    return render(request, 'welcome.html')

# 添加实体
def addEntity(request):
    return render(request, 'addEntity.html')

# 修改实体
def changeEntity(request):
    return render(request, 'changeEntity.html')

# 删除实体
def deleteEntity(request):
    return render(request, 'deleteEntity.html')

# 添加关系
def addRelation(request):
    return render(request, 'addRelation.html')

# 修改关系
def changeRelation(request):
    return render(request, 'changeRelation.html')

# 删除关系
def deleteRelation(request):
    return render(request, 'deleteRelation.html')

# 用户列表
def userList(request):
    return render(request, 'userlist.html')

# 管理员个人信息显示
def adminInfo(request):
    return render(request, 'admininfo.html')


