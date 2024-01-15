from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect
from iElect.models import Election, Candidate
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'dashboard.html')

def settings(request):
    return render(request, 'settings_page.html')

@login_required(login_url='/auth')
def election_view(request):
 elections = Election.objects.all()
 for election in elections:
   election.candidates = Candidate.objects.filter(election=election)
 print(f"Number of elections: {len(elections)}")
 return render(request, 'elections_page.html', {'elections': elections})

@login_required(login_url='/auth')
def candidate_detail_view(request, candidate_id):
   candidate = get_object_or_404(Candidate, pk=candidate_id)
   return render(request, 'details_page.html', {'candidate': candidate})


def results(request):
    return render(request, 'results_page.html')

def guidelines(request):
    return render(request, 'guidelines_page.html')

def results(request, election_id):
   election = Election.objects.get(pk=election_id)

   candidates = Candidate.objects.filter(election=election).order_by('-total_vote')

   total_votes = sum(candidate.total_vote for candidate in candidates)

   candidates_with_percentage = []
   for candidate in candidates:
       if total_votes == 0:
           percentage = 0
       else:
           percentage = (candidate.total_vote / total_votes) * 100

       candidates_with_percentage.append({
           'candidate': candidate,
           'percentage': percentage
       })

   print(candidates_with_percentage) # Add this line

   context = {
       'election': election,
       'candidates_with_percentage': candidates_with_percentage,
   }

   return render(request, 'results_page.html', context)