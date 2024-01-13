from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect

def index(request):
    return render(request, 'dashboard.html')

def settings(request):
    return render(request, 'settings_page.html')

def elections(request):
    return render(request, 'elections_page.html')

def details(request):
    return render(request, 'details_page.html')