# Generated by Django 2.0 on 2020-10-22 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, verbose_name='用户名')),
                ('password', models.CharField(max_length=10, verbose_name='密码')),
                ('phone', models.CharField(default='18832072073', max_length=12, verbose_name='手机号')),
                ('eamil', models.EmailField(max_length=50, verbose_name='邮箱')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'db_table': 'qestionsys_user',
            },
        ),
    ]
