from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.core.mail import send_mail
import random
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .models import UsersInf
from celevik import settings


# Create your views here.
def index(request):
    return render(request, 'main_app/index.html')


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


def user_profile(request):
    # uid = request.user.id
    # user = User.objects.get(id=uid)
    # u = UsersInf.objects.get(user=user)
    # return render(request, 'main_app/user_profile.html', {'u': u})
    return render(request, 'main_app/user_profile.html')


def user_profile_editor(request):
    # uid = request.user.id
    # user = User.objects.get(id=uid)
    # u = UsersInf.objects.get(user=user)
    # return render(request, 'main_app/user_profile.html', {'u': u})
    return render(request, 'main_app/user_profile_editor.html')