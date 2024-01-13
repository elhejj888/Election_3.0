from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('elections/', views.elections, name='elections'),
    path('details/', views.details, name='details'),
]