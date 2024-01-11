from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('auth', views.moralis_auth, name='auth'),
    path('request_message', views.request_message, name='request_message'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('verify_message', views.verify_message, name='verify_message'),
    path('register', views.register, name='register'),
    path('login_email', views.email_password_login, name='email_password_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
appname='iElect'

   

