from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from celevik import settings


# Create your views here.
def index(request):
    return render(request, 'main_app/index.html')