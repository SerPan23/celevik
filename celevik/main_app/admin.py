from django.contrib import admin
from .models import UsersInf, Vacancy, Responses, Universities, Direction, CompanyRegApplication

# Register your models here.

admin.site.register(UsersInf)
admin.site.register(Vacancy)
admin.site.register(Responses)
admin.site.register(Universities)
admin.site.register(Direction)
admin.site.register(CompanyRegApplication)
