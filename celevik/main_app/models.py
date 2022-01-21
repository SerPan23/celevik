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
                                verbose_name="Связь с таблицей пользователей", related_name="user_info")
    image = models.ImageField("Фотография профиля", blank=True, upload_to="puples_photo",
                              default="puples_photo/default_avatar.png")
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField("Номер телефона", null=True, max_length=150)
    code = IntegerField("Код активации", null=False)
    surname = models.CharField("Фамилия", null=True, blank=True, max_length=150)
    name = models.CharField("Имя", null=True, max_length=150)
    patronymic = models.CharField("Отчество", null=True, blank=True, max_length=150)
    role = models.CharField("Статуc", choices=ROLE_CHOICES, default='Entrant', max_length=30)
    text_about = models.TextField("Текст о пользователе", default='')

    def __str__(self):
        return 'Profile for user {}'.format(self.user.email)


class Vacancy(models.Model):
    organisation = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                     default='',
                                     verbose_name="Связь с таблицей пользователей", related_name="organisation")
    partners = models.TextField("Список вузов партнеров", null=True, default='')
    description = models.TextField("Описание вакансии", default='')
    requirements = models.TextField("Требования к соискателю", default='')
    title = models.CharField("Название", default='', null=True, blank=True, max_length=250)

    def __str__(self):
        return '{} {}'.format(self.organisation.email, self.title)


class Responses(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, null=True,
                                default='',
                                verbose_name="Связь с таблицей вакансии", related_name="vacancy")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                default='',
                                verbose_name="Связь с таблицей пользователей")
