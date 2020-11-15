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

class Quest(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField(max_length=255, verbose_name='笔记标题')
    answer = models.TextField(max_length=255, verbose_name='笔记内容')

    class Meta:
        db_table = 'qestionsys_quest'
        verbose_name = '日志'
        verbose_name_plural = verbose_name

    # 在 str 魔法方法中, 返回用户名称
    def __str__(self):
        return self.question
