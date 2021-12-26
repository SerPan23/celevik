from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration', views.registration, name="registration"),
    # path('reg_user/', views.reg_user),
    path('account_confirmation/', views.account_confirmation, name='account_confirmation'),
    path('account_confirmed/', views.account_confirmed),
    path('user_profile/', views.user_profile),
    path('user_profile_editor/', views.user_profile_editor),
]