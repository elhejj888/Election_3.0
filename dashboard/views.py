from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect

def index(request):
    return render(request, 'dashboard.html')

def settings(request):
    return render(request, 'settings_page.html')

from django.shortcuts import render
from iElect.models import Election, Candidate

def election_view(request):
 elections = Election.objects.all()
 for election in elections:
   election.candidates = Candidate.objects.filter(election=election)
 print(f"Number of elections: {len(elections)}")
 return render(request, 'elections_page.html', {'elections': elections})

def details(request):
    return render(request, 'details_page.html')