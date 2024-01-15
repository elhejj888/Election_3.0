from django.urls import path

from iElect.views import voteView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('elections/', views.election_view, name='elections'),
    path('results/', views.results, name='results'),
    path('guidelines/', views.guidelines, name='guidelines'),
    path('candidate/<int:candidate_id>/', views.candidate_detail_view, name='candidate_detail'),
    path('vote/<int:election_id>/<int:candidate_id>/', voteView, name='vote'),

]