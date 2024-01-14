from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('elections/', views.election_view, name='elections'),
    path('candidate/<int:candidate_id>/', views.candidate_detail_view, name='candidate_detail'),
]