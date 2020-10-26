from django.db import models

# Create your models here.
class Note(models.Model):
    note_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=12, verbose_name='笔记标题')
    content = models.TextField(max_length=255, verbose_name='笔记内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    user = models.ForeignKey('user.User', verbose_name='用户id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'qestionsys_note'
        verbose_name = '笔记'
        verbose_name_plural = verbose_name

    # 在 str 魔法方法中, 返回用户名称
    def __str__(self):
        return self.title

