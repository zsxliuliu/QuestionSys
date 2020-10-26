from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from user.models import User
from note.models import Note
import re
# Create your views here.
# 注册
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # 进行数据校验
        if not all([username, password, phone, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username=username, password=password, phone=phone, email=email)
        user.save()

        # 返回应答, 跳转到首页
        return redirect(reverse('user:login'))

# 登录
def loginProcess(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 业务处理:登录校验
        user = authenticate(username=username, password=password)
        # 用户名密码正确
        if user is not None:

            # 记录用户的登录状态
            login(request, user)
            user_id = user.id
            #
            # 得到该用户的笔记列表
            notes = Note.objects.filter(user_id=user_id).order_by('-create_time')

            # 获取登录后所要跳转到的地址
            # 默认跳转到首页
            # next_url = request.GET.get('next', reverse('user:index'))
            #
            # # 跳转到next_url
            # response = redirect(next_url)  # HttpResponseRedirect

            return render(request, 'index.html', {"notes":notes})
            # # 返回response
            # return response
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

def logout(request):
    return redirect(reverse('user:login'))

def index(request):
    if request.method == 'GET':
        user = request.user
        user_id = user.id

        # 得到该用户的笔记列表
        notes = Note.objects.filter(user_id=user_id).order_by('-create_time')
        return render(request, 'index.html', {'notes': notes})

def usercenter(request):
    if request.method == 'GET':
        '''显示'''
        # Django会给request对象添加一个属性request.user
        # 如果用户未登录->user是AnonymousUser类的一个实例对象
        # 如果用户登录->user是User类的一个实例对象
        # request.user.is_authenticated()

        # 获取用户的个人信息
        user = request.user
        # 组织上下文
        context = {'page': 'user',}

        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件
        return render(request, 'usercenter.html', context)
    else:
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # 校验数据
        if not all([username, password, phone, email]):
            return render(request, 'usercenter.html', {'errmsg': '数据不完整'})
        # 获取用户的个人信息
        user = request.user
        user_id = user.id

        User.objects.filter(id=user_id).update(username=username, password=password, phone=phone, email=email)
    return render(request, 'usercenter.html')

