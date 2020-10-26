from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # username = models.CharField(max_length=50, verbose_name='用户名')
    # password = models.CharField(max_length=10, verbose_name='密码')
    phone = models.CharField(max_length=12, verbose_name='手机号', default='18832072073')
    # eamil = models.EmailField(max_length=50, verbose_name='邮箱')

    class Meta:
        db_table = 'qestionsys_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    # 在 str 魔法方法中, 返回用户名称
    def __str__(self):
        return self.username
