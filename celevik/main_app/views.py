import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.core.mail import send_mail
import random
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import UsersInf, Vacancy, Responses, Universities, Direction, CompanyRegApplication
from celevik import settings

# Create your views here.
from .useful_funcs import *


def index(request):
    universities = Universities.objects.all()
    directions = Direction.objects.all()
    vacancies = Vacancy.objects.filter(is_frozen=False)
    is_not_comp = request.GET.get("is_not_adm", "")
    is_not_adm = request.GET.get("is_not_adm", "")
    res_data = {'universities': universities, 'directions': directions,
                'is_not_comp': is_not_comp, 'is_not_adm': is_not_adm}
    if request.method == "POST":
        sort_universities = request.POST.get("universities")
        sort_directions = request.POST.get("directions")
        sus = sort_universities.split('|')
        sds = sort_directions.split('|')
        if sds[0] != '' or sus[0] != '':
            filtered_ids = []
            for v in vacancies:
                if sds[0] != '' and sus[0] != '':
                    if v.title.split()[1] in sds and is_intersection_list(v.partners.split('|'), sus):
                        filtered_ids.append(v.id)
                elif sds[0] == '' and sus[0] != '':
                    if is_intersection_list(v.partners.split('|'), sus):
                        filtered_ids.append(v.id)
                elif sds[0] != '' and sus[0] == '':
                    if v.title.split()[1] in sds:
                        filtered_ids.append(v.id)
            vacancies = vacancies.filter(id__in=filtered_ids)
        res_data['sort_universities'] = sort_universities
        res_data['sort_directions'] = sort_directions
    if request.POST.get("changed_sort", "") == 'True':
        page_number = 1
    else:
        page_number = int(request.POST.get("page_number", "") if request.POST.get("page_number", "") != '' else 1)
    paginator = Paginator(vacancies, 25)
    if page_number > paginator.num_pages:
        page_number = paginator.num_pages
    if page_number < 1:
        page_number = 1
    page_vacancies = paginator.get_page(page_number)
    pages_num_range = get_pages_interval(page_number, paginator.num_pages)
    res_data['vacancies'] = page_vacancies
    res_data['cur_page'] = page_number
    res_data['pages_num_range'] = pages_num_range
    res_data['vacancies_len'] = len(vacancies)
    return render(request, 'main_app/index.html', res_data)


def registration(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(username=email).exists():
            return HttpResponseRedirect("/registration?username_busy=True")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        name = request.POST.get("name")
        surname = request.POST.get("surname")
        patronymic = request.POST.get("patronymic")
        phone_number = request.POST.get("phone_number")
        date_of_birth = request.POST.get("date_of_birth")
        text_about = request.POST.get("text_about")
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
        user_inf.name = name
        user_inf.surname = surname
        user_inf.patronymic = patronymic
        user_inf.phone_number = phone_number
        user_inf.date_of_birth = date_of_birth
        user_inf.text_about = text_about
        user_inf.save()
        message = 'Код подтверждения регистрации: ' + code
        send_mail(settings.EMAIL_TOPIC, message,
                  settings.EMAIL_HOST_USER, [email])
        return HttpResponseRedirect("/account_confirmation?username=" + email)
    error_pass = request.GET.get("error_pass", "")
    username_busy = request.GET.get("username_busy", "")
    return render(request, "registration/registration.html", {'error_pass': error_pass, 'username_busy': username_busy})


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


@company_login_required
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
    res_data = {}
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        if request.user.id == vacancy.organisation.id:
            if data["type"] == "confirm":
                u = User.objects.get(id=data["user_id"])
                response = responses.get(user=u)
                response.is_confirmed = True
                response.save()
                message = 'Вам подтвердили заявку на ' + str(response.vacancy.title) + '\nОт ' \
                          + str(response.vacancy.organisation.user_info.name)
                send_mail(settings.EMAIL_TOPIC, message,
                          settings.EMAIL_HOST_USER, [u.email])
            elif data["type"] == "del":
                vacancy.delete()
            elif data["type"] == "frost":
                vacancy.is_frozen = True
                vacancy.save()
            elif data["type"] == "defrost":
                vacancy.is_frozen = False
                vacancy.save()
        elif data["type"] == "respond":
            user = User.objects.get(id=request.user.id)
            response = Responses.objects.create(vacancy=vacancy, user=user)
            response.save()
            message = str(user.user_info.surname) + ' ' + str(user.user_info.name) + \
                      ' заинтересовался вашей вакансией: ' + str(response.vacancy.title)
            send_mail(settings.EMAIL_TOPIC, message,
                      settings.EMAIL_HOST_USER, [response.vacancy.organisation.email])
    res_data['is_respond'] = False
    res_data['is_confirm'] = False
    if request.user.is_authenticated and responses.filter(user=request.user).exists():
        res_data['is_respond'] = True
        r = responses.get(user=request.user)
        res_data['is_confirm'] = r.is_confirmed
    res_data['vacancy'] = vacancy
    res_data['responses'] = responses
    return render(request, 'main_app/vacancy_page.html', res_data)


@company_login_required
def add_vacancy(request):
    edit_id = request.GET.get("edit_id", "")
    universities = Universities.objects.all()
    directions = Direction.objects.all()
    if edit_id:
        vacancy = Vacancy.objects.get(id=edit_id)
        return render(request, 'main_app/add_vacancy.html',
                      {"vacancy": vacancy, "universities": universities, "directions": directions})
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


def company_reg(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        text_about = request.POST.get("text_about")
        application = CompanyRegApplication.objects.create(name=name, email=email, phone_number=phone_number,
                                                           text_about=text_about)
        application.save()
        return HttpResponseRedirect("/")
    return render(request, "registration/company_reg.html")


@admin_login_required
def list_of_applications_for_registration(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        application = CompanyRegApplication.objects.get(id=id)
        if data["type"] == "approve":
            password = User.objects.make_random_password()
            new_company = User.objects.create_user(username=application.email, email=application.email,
                                                   password=password)
            new_company.is_active = True
            new_company.save()
            user_inf = UsersInf.objects.create(user=new_company, code=0, role='Company')
            user_inf.name = application.name
            user_inf.phone_number = application.phone_number
            user_inf.text_about = application.text_about
            user_inf.save()
            message = 'Ваша заявка на регистрацию одобрена!\nВаш пароль: ' + password
            send_mail(settings.EMAIL_TOPIC, message,
                      settings.EMAIL_HOST_USER, [application.email])
        if data["type"] == "reject":
            message = 'К сожалению ваша заявку на регистрацию отклонена\nПопробуйте подать заявку заново'
            send_mail(settings.EMAIL_TOPIC, message,
                      settings.EMAIL_HOST_USER, [application.email])
        application.delete()
    page_number = int(request.GET.get("page_number", "") if request.GET.get("page_number", "") != '' else 1)
    applications = CompanyRegApplication.objects.all()
    paginator = Paginator(applications, 25)
    if page_number > paginator.num_pages:
        return HttpResponseRedirect("/list_of_applications_for_registration/?page_number=" + str(paginator.num_pages))
    if page_number < 1:
        return HttpResponseRedirect("/list_of_applications_for_registration/?page_number=1")
    page_applications = paginator.get_page(page_number)
    return render(request, 'main_app/list_of_applications_for_registration.html',
                  {"applications": page_applications, "pages_num_range": range(1, paginator.num_pages + 1),
                   'cur_page': page_number, 'applications_len': len(applications)})


@admin_login_required
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
    page_number = int(request.GET.get("page_number", "") if request.GET.get("page_number", "") != '' else 1)
    universities = Universities.objects.all()
    paginator = Paginator(universities, 25)
    if page_number > paginator.num_pages:
        return HttpResponseRedirect("/list_of_universities/?page_number=" + str(paginator.num_pages))
    if page_number < 1:
        return HttpResponseRedirect("/list_of_universities/?page_number=1")
    page_applications = paginator.get_page(page_number)
    return render(request, 'main_app/list_of_universities.html',
                  {'universities': page_applications, "pages_num_range": range(1, paginator.num_pages + 1),
                   'cur_page': page_number, 'universities_len': len(universities)})


@admin_login_required
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
    page_number = int(request.GET.get("page_number", "") if request.GET.get("page_number", "") != '' else 1)
    directions = Direction.objects.all()
    paginator = Paginator(directions, 25)
    if page_number > paginator.num_pages:
        return HttpResponseRedirect("/list_of_directions/?page_number=" + str(paginator.num_pages))
    if page_number < 1:
        return HttpResponseRedirect("/list_of_directions/?page_number=1")
    page_applications = paginator.get_page(page_number)
    pages_num_range = get_pages_interval(page_number, paginator.num_pages)
    return render(request, 'main_app/list_of_directions.html',
                  {'directions': page_applications, "pages_num_range": pages_num_range,
                   'cur_page': page_number, 'directions_len': len(directions)})
