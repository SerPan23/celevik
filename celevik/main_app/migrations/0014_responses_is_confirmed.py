# Generated by Django 4.0 on 2022-02-10 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0013_vacancy_is_frozen'),
    ]

    operations = [
        migrations.AddField(
            model_name='responses',
            name='is_confirmed',
            field=models.BooleanField(default=False, verbose_name='Подтвержден?'),
        ),
    ]
