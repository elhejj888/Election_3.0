from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import path
from .views import admin_auto_login
from django.conf.urls.static import static

urlpatterns = [
    path('auth', views.moralis_auth, name='auth'),
    path('request_message', views.request_message, name='request_message'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('verify_message', views.verify_message, name='verify_message'),
    path('register', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('', views.index, name='index'),
    path('admin_auto_login/', admin_auto_login, name='admin_auto_login'),
    path('dashboard/', include('dashboard.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
appname='iElect'

  




