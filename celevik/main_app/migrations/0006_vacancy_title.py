# Generated by Django 4.0 on 2022-01-04 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_vacancy'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='title',
            field=models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='Название'),
        ),
    ]
