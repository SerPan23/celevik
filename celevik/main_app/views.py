import json

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

from .models import UsersInf, Vacancy, Responses, Universities, Direction
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
def user_vacancies_list(request):
    user = User.objects.get(id=request.user.id)
    responses = Responses.objects.filter(user=user)
    return render(request, 'main_app/user_vacancies_list.html', {'responses': responses})


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
    responses = Responses.objects.filter(vacancy=vacancy)
    is_respond = False
    if request.user.is_authenticated and responses.filter(user=request.user).exists():
        is_respond = True
    return render(request, 'main_app/vacancy_page.html', {"vacancy": vacancy, "responses": responses, "is_respond": is_respond})


@login_required
def add_vacancy(request):
    edit_id = request.GET.get("edit_id", "")
    universities = Universities.objects.all()
    directions = Direction.objects.all()
    if edit_id:
        vacancy = Vacancy.objects.get(id=edit_id)
        return render(request, 'main_app/add_vacancy.html', {"vacancy": vacancy, "universities": universities, "directions": directions})
    if request.method == "POST":
        edit = request.POST.get("edit", "")
        title = request.POST.get("title", "")
        partners = request.POST.get("partners", "")
        description = request.POST.get("description", "")
        requirements = request.POST.get("requirements", "")
        if edit == "True":
            vacancy_id = request.POST.get("vacancy_id", "")
            vacancy = Vacancy.objects.get(id=vacancy_id)
            vacancy.title = title
            vacancy.partners = partners
            vacancy.description = description
            vacancy.requirements = requirements
            vacancy.save()
            return HttpResponseRedirect("/vacancy/" + str(vacancy_id) + "/")
        else:
            uid = request.user.id
            organisation = User.objects.get(id=uid)
            vacancy = Vacancy.objects.create(organisation=organisation)
            vacancy.title = title
            vacancy.partners = partners
            vacancy.description = description
            vacancy.requirements = requirements
            vacancy.save()
            return HttpResponseRedirect("/vacancy/" + str(vacancy.id) + "/")
    return render(request, 'main_app/add_vacancy.html', {"universities": universities, "directions": directions})


@login_required
def del_vacancy(request, pk):
    vacancy = Vacancy.objects.get(id=pk)
    vacancy.delete()
    return HttpResponseRedirect("/")


@login_required
def respond(request, pk):
    vacancy = Vacancy.objects.get(id=pk)
    user = User.objects.get(id=request.user.id)
    response = Responses.objects.create(vacancy=vacancy, user=user)
    response.save()
    return HttpResponseRedirect("/vacancy/"+str(pk)+"/")


def applications_for_registration_list(request):
    return render(request, 'main_app/applications_for_registration_list.html')


def list_of_universities(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        if data["type"] == "edit":
            id = data["id"]
            text = data["text"]
            university = Universities.objects.get(id=id)
            university.title = text
            university.save()
        if data["type"] == "del":
            id = data["id"]
            university = Universities.objects.get(id=id)
            university.delete()
        if data["type"] == "add":
            text = data["text"]
            university = Universities.objects.create(title=text)
            university.save()
    universities = Universities.objects.all()
    return render(request, 'main_app/list_of_universities.html', {'universities': universities})


def list_of_directions(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        if data["type"] == "edit":
            id = data["id"]
            code = data["code"]
            text = data["text"]
            dir = Direction.objects.get(id=id)
            dir.code = code
            dir.title = text
            dir.save()
        if data["type"] == "del":
            id = data["id"]
            dir = Direction.objects.get(id=id)
            dir.delete()
        if data["type"] == "add":
            text = data["text"]
            code = data["code"]
            university = Direction.objects.create(title=text, code=code)
            university.save()
    directions = Direction.objects.all()
    return render(request, 'main_app/list_of_directions.html', {'directions': directions})
