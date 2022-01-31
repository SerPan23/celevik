from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration', views.registration, name="registration"),
    # path('reg_user/', views.reg_user),
    path('account_confirmation/', views.account_confirmation, name='account_confirmation'),
    path('account_confirmed/', views.account_confirmed),
    path('user_profile/<int:pk>/', views.user_profile),
    path('user_profile_editor/', views.user_profile_editor),
    path('organization_profile/<int:pk>/', views.organization_profile),
    path('organization_profile_editor/', views.organization_profile_editor),
    path('vacancy/<int:pk>/', views.vacancy_page),
    path('add_vacancy/', views.add_vacancy),
    path('del_vacancy/<int:pk>/', views.del_vacancy),
    path('respond/<int:pk>/', views.respond),
    path('user_vacancies_list/', views.user_vacancies_list),
    path('list_of_applications_for_registration/', views.list_of_applications_for_registration),
    path('list_of_universities/', views.list_of_universities),
    path('list_of_directions/', views.list_of_directions),
]
