# Generated by Django 4.0 on 2021-12-25 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersinf',
            name='text_about',
            field=models.TextField(default='', verbose_name='Текст о пользователе'),
        ),
    ]
