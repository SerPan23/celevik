# Generated by Django 4.0 on 2021-12-31 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_usersinf_text_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersinf',
            name='image',
            field=models.ImageField(blank=True, default='puples_photo/default_avatar.png', upload_to='puples_photo', verbose_name='Фотография профиля'),
        ),
    ]
