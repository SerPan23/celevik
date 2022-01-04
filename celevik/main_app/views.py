from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.core.mail import send_mail
import random
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import UsersInf, Vacancy
from celevik import settings


# Create your views here.
def index(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'main_app/index.html', {'vacancies': vacancies})


def registration(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password != password2:
            return HttpResponseRedirect("/registration?error_pass=True")
        try:
            validate_password(password)
        except ValidationError as vale:
            return render(request, "registration/registration.html", {'vale': vale})
        new_user = User.objects.create_user(username=email, email=email, password=password)
        new_user.is_active = False
        new_user.save()
        code = generate_code()
        user_inf = UsersInf.objects.create(user=new_user, code=code)
        user_inf.code = code
        user_inf.save()
        message = 'Код подтверждения регистрации: ' + code
        send_mail(settings.EMAIL_TOPIC, message,
                  settings.EMAIL_HOST_USER, [email])
        return HttpResponseRedirect("/account_confirmation?username=" + email)
    error_pass = request.GET.get("error_pass", "")
    return render(request, "registration/registration.html", {'error_pass': error_pass})


def generate_code():
    random.seed()
    return str(random.randint(10000, 99999999))


def account_confirmation(request):
    username = request.GET.get("username", "")
    error = request.GET.get("error", "")
    return render(request, "registration/account_confirmation.html", {'username': username, 'error': error})


def account_confirmed(request):
    if request.method == "POST":
        username = request.POST.get("username")
        code = request.POST.get("code")
        user = User.objects.get(username=username)
        user_inf = UsersInf.objects.get(user=user)
        db_code = user_inf.code
        if code == str(db_code):
            user.is_active = True
            user.save()
            return HttpResponseRedirect("/login/")
        else:
            return HttpResponseRedirect("/account_confirmation?username=" + username + "&error=True")


def user_profile(request, pk):
    # pk = request.user.id
    user = User.objects.get(id=pk)
    u_info = UsersInf.objects.get(user=user)
    if u_info.role == 'Company':
        return HttpResponseRedirect("/organization_profile/" + str(pk) + "/")
    return render(request, 'main_app/user_profile.html', {'u_info': u_info})


@login_required
def user_profile_editor(request):
    uid = request.user.id
    user = User.objects.get(id=uid)
    u_info = UsersInf.objects.get(user=user)
    error_pass = request.GET.get("error_pass", "")
    if request.method == "POST":
        pass_edit = request.POST.get("pass_edit", "")
        info_edit = request.POST.get("info_edit", "")
        username = request.POST.get("username")
        if pass_edit:
            oldpassword = request.POST.get("old_password")
            password = request.POST.get("new_password1")
            password2 = request.POST.get("new_password2")
            if password != password2 or password == '' or not user.check_password(str(oldpassword)):
                return HttpResponseRedirect("/user_profile_editor?error_pass=True")
            else:
                try:
                    validate_password(password)
                except ValidationError as vale:
                    return render(request, 'main_app/user_profile_editor.html',
                                  {'u_info': u_info, 'error_pass': error_pass, 'vale': vale})
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                login(request, user)
        if info_edit:
            name = request.POST.get("name")
            surname = request.POST.get("surname")
            patronymic = request.POST.get("patronymic")
            phone_number = request.POST.get("phone_number")
            date_of_birth = request.POST.get("date_of_birth")
            text_about = request.POST.get("text_about")
            if name != '':
                u_info.name = name
            if surname != '':
                u_info.surname = surname
            if patronymic != '':
                u_info.patronymic = patronymic
            if phone_number != '':
                u_info.phone_number = phone_number
            if date_of_birth != '':
                u_info.date_of_birth = date_of_birth
            if text_about != '':
                u_info.text_about = text_about
            if request.FILES["avatar"]:
                u_info.image = request.FILES["avatar"]
            u_info.save()
    return render(request, 'main_app/user_profile_editor.html', {'u_info': u_info, 'error_pass': error_pass})


def organization_profile(request, pk):
    # pk = request.user.id
    user = User.objects.get(id=pk)
    u_info = UsersInf.objects.get(user=user)
    vacancies = Vacancy.objects.filter(organisation=user)
    if u_info.role == 'Entrant':
        return HttpResponseRedirect("/user_profile/" + str(pk) + "/")
    return render(request, 'main_app/organization_profile.html', {'u_info': u_info, 'vacancies': vacancies})


@login_required
def organization_profile_editor(request):
    uid = request.user.id
    user = User.objects.get(id=uid)
    u_info = UsersInf.objects.get(user=user)
    error_pass = request.GET.get("error_pass", "")
    if request.method == "POST":
        pass_edit = request.POST.get("pass_edit", "")
        info_edit = request.POST.get("info_edit", "")
        username = request.POST.get("username")
        if pass_edit:
            oldpassword = request.POST.get("old_password")
            password = request.POST.get("new_password1")
            password2 = request.POST.get("new_password2")
            if password != password2 or password == '' or not user.check_password(str(oldpassword)):
                return HttpResponseRedirect("/organization_profile_editor?error_pass=True")
            else:
                try:
                    validate_password(password)
                except ValidationError as vale:
                    return render(request, 'main_app/organization_profile_editor.html',
                                  {'u_info': u_info, 'error_pass': error_pass, 'vale': vale})
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                login(request, user)
        if info_edit:
            name = request.POST.get("name")
            phone_number = request.POST.get("phone_number")
            text_about = request.POST.get("text_about")
            if name != '':
                u_info.name = name
            if phone_number != '':
                u_info.phone_number = phone_number
            if text_about != '':
                u_info.text_about = text_about
            u_info.save()
    return render(request, 'main_app/organization_profile_editor.html', {'u_info': u_info, 'error_pass': error_pass})


def vacancy_page(request, pk):
    vacancy = Vacancy.objects.get(id=pk)
    return render(request, 'main_app/vacancy_page.html', {"vacancy": vacancy})
