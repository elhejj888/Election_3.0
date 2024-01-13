from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect

def index(request):
    return render(request, 'dashboard.html')

def settings(request):
    return render(request, 'settings_page.html')


