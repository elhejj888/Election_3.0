from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import path
from .views import voteView
from django.conf.urls.static import static

urlpatterns = [
    path('auth', views.moralis_auth, name='auth'),
    path('request_message', views.request_message, name='request_message'),
    path('verify_message', views.verify_message, name='verify_message'),
    path('register', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('', views.index, name='index'),
    path('dashboard/', include('dashboard.urls')),
    path('contact', views.contact, name='contact'),
    path('clear-messages/', views.clear_messages, name='clear_messages'),
    path('vote/<int:election_id>/<int:candidate_id>/', voteView, name='vote'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
appname='iElect'

  




