from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.


def user_logout(request):
    logout(request)
    messages.success(request, "Başarıyla Çkış Yaptınız.")
    return redirect("index")