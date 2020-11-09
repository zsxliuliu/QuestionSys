from django.db import models

# Create your models here.
class AdminUser(models.Model):
    id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=12, verbose_name='管理员名称')
    admin_password = models.CharField(max_length=10, verbose_name='管理员密码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')


    class Meta:
        db_table = 'qestionsys_adminuser'
        verbose_name = '管理员信息'
        verbose_name_plural = verbose_name

    # 在 str 魔法方法中, 返回用户名称
    def __str__(self):
        return self.admin_name

class EntityType(models.Model):
    id = models.AutoField(primary_key=True)
    entity_type = models.CharField(max_length=12, verbose_name='实体类别')

    class Meta:
        db_table = 'qestionsys_entitytype'
        verbose_name = '实体类别'
        verbose_name_plural = verbose_name

class RelationType(models.Model):
    id = models.AutoField(primary_key=True)
    relation_type = models.CharField(max_length=12, verbose_name='关系类别')

    class Meta:
        db_table = 'qestionsys_relationtype'
        verbose_name = '关系类别'
        verbose_name_plural = verbose_name