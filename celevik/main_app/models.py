from django.db import models
from django.contrib.auth.models import User
from django.db.models import IntegerField, BooleanField


class UsersInf(models.Model):
    ROLE_CHOICES = (
        ('Entrant', 'Абитуриент'),
        ('Company', 'Компания'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True,
                                default='',
                                verbose_name="Связь с таблицей пользователей")
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField("Номер телефона", null=True, max_length=150)
    code = IntegerField("Код активации", null=False)
    surname = models.CharField("Фамилия", null=True, max_length=150)
    name = models.CharField("Имя", null=True, max_length=150)
    patronymic = models.CharField("Отчество", null=True, max_length=150)
    role = models.CharField("Статуc", choices=ROLE_CHOICES, default='Entrant', max_length=30)
    text_about = models.TextField("Текст о пользователе", default='')

    def __str__(self):
        return 'Profile for user {}'.format(self.user.email)
