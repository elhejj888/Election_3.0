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
 """
    Displays a list of elections along with their candidates.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.

    Returns:
    HttpResponse: Renders the 'elections_page.html' template with a context
                  containing a list of elections and their associated candidates.
 """
 elections = Election.objects.all()
 for election in elections:
   election.candidates = Candidate.objects.filter(election=election)
 print(f"Number of elections: {len(elections)}")
 return render(request, 'elections_page.html', {'elections': elections})


@login_required(login_url='/auth')
def candidate_detail_view(request, candidate_id):
   """
    Displays details for a specific candidate.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.
    - candidate_id (int): The primary key of the Candidate object.

    Returns:
    HttpResponse: Renders the 'details_page.html' template with details of the specified candidate.
   """
   candidate = get_object_or_404(Candidate, pk=candidate_id)
   return render(request, 'details_page.html', {'candidate': candidate})


def results(request):
    return render(request, 'results_page.html')

def guidelines(request):
    return render(request, 'guidelines_page.html')

def results(request, election_id):
 """
    Displays the election results, including candidate details and vote percentages.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.
    - election_id (int): The primary key of the Election object.

    Returns:
    HttpResponse: Renders the 'results_page.html' template with details of the specified election results.
 """
 election = Election.objects.get(pk=election_id)

 candidates = Candidate.objects.filter(election=election).order_by('id')

 total_votes = sum(candidate.get_vote_count() for candidate in candidates)

 candidates_with_percentage = []
 for candidate in candidates:
     if total_votes == 0:
         percentage = 0
     else:
         percentage = (candidate.get_vote_count() / total_votes) * 100

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


