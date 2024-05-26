import json
from time import timezone
from django.urls import reverse, reverse_lazy
import requests
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import ContactForm, RegistrationForm, EditProfileForm
from iElect.models import Candidate, ControlVote, Election, UserVote
from django import forms
from django.contrib import messages
from django.db import IntegrityError, transaction, models
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist


API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjBhM2I2MTRjLWQ2ZjQtNGRkOS04M2RmLTIzNmZiMjBjNzg1OCIsIm9yZ0lkIjoiMzY5NTYzIiwidXNlcklkIjoiMzc5ODE2IiwidHlwZUlkIjoiOTNiZDhjOWYtNTViZC00ZmFmLThiMTQtNTZhYTFhZmIyMjZhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MDM1MjQ5NTcsImV4cCI6NDg1OTI4NDk1N30.CrZJcIyqcCdYMtM45pbRB4tY7-fOqwxSRhEtmE_dba0'

def moralis_auth(request):
   return render(request, 'login.html', {})


def request_message(request):
   """
    Handles a request to create and send an authentication challenge.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.

    Returns:
    JsonResponse: A JSON response containing the result of the request.
   """
   data = json.loads(request.body)
   print(data)

   REQUEST_URL = 'https://authapi.moralis.io/challenge/request/evm'
   from datetime import datetime, timedelta
   
   expiration_time = (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z"
   request_object = {
       "domain": "defi.finance",
       "chainId": 1,
       "address": data['address'],
       "statement": "Please confirm",
       "uri": "https://defi.finance/",
       "expirationTime": expiration_time,
       "notBefore": "2020-01-01T00:00:00.000Z",
       "timeout": 15
   }
   x = requests.post(
       REQUEST_URL,
       json=request_object,
       headers={'X-API-KEY': API_KEY})

   return JsonResponse(json.loads(x.text))

def verify_message(request):
  """
    Handles a request to verify an authentication challenge and perform user authentication.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object containing the authentication data.

    Returns:
    JsonResponse: A JSON response containing the result of the verification process.
  """
  data = json.loads(request.body)
  print(data)

  REQUEST_URL = 'https://authapi.moralis.io/challenge/verify/evm'
  x = requests.post(
      REQUEST_URL,
      json=data,
      headers={'X-API-KEY': API_KEY})
  print(json.loads(x.text))
  print(x.status_code)
  if x.status_code == 201:
      eth_address = json.loads(x.text).get('address')
      print("eth address", eth_address)
      try:
          user = User.objects.get(username=eth_address)
      except User.DoesNotExist:
          user = User.objects.create_user(username=eth_address, password=None)
          user.save()
          request.session['needs_registration'] = True
      if user is not None:
          if user.is_active:
              login(request, user)
          request.session['auth_info'] = data
          request.session['verified_data'] = json.loads(x.text)
          return JsonResponse({'user': user.username})
      else:
          return JsonResponse({'error': 'account disabled'})
  else:
      user = User.objects.create_user(username= eth_address, password=None)
      user.save()
      request.session['needs_registration'] = True
      return JsonResponse(json.loads(x.text))

@login_required(login_url='/auth')
def register(request):
 """
    Handles user registration based on a submitted registration form.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.

    Returns:
    HttpResponse: A rendered HTML page for user registration or a JSON response
                  indicating the status of the registration process.
 """
 if request.method == 'POST':
     form = RegistrationForm(request.POST)
     print("Form submitted") 

     if form.is_valid():
         print("Form is valid")
         print("Form data: ", form.cleaned_data) 
         eth_address = request.session.get('verified_data', {}).get('address')

         if not eth_address:
             return JsonResponse({'error': 'No Ethereum address provided'})

         try:
             user = User.objects.get(username=eth_address)
             print(f"User exists: {user}") 
         except User.DoesNotExist:
             user = User.objects.create_user(username=eth_address, password=None)
             print(f"Created new user: {user}")

         form.save(commit=False)
         user.email = form.cleaned_data['email']
         user.first_name = form.cleaned_data['first_name']
         user.last_name = form.cleaned_data['last_name']
         user.password = form.cleaned_data['password']
         user.save()

         print(f"Updated user data: {user}")

         login(request, user)

         if 'needs_registration' in request.session:
             del request.session['needs_registration']

         return redirect('my_profile')

     else:
         print("Form errors: ", form.errors) 
         return JsonResponse({'status': 'error', 'errors': form.errors})

 else:
     form = RegistrationForm()

 return render(request, 'register.html', {'form': form})


def get_success_url(self):
    return reverse('dashboard.html')

@login_required(login_url='/dashboard.html')
def my_profile(request):
  user = request.user
  eth_address = user.username

  if User.objects.filter(username=eth_address).exists():
      if 'needs_registration' in request.session:
          del request.session['needs_registration']
          return redirect('register')
      else:
          return render(request, 'dashboard.html', {'user': request.user})
  else:
      return redirect('register')


def index(request):
    return render(request, 'index.html')

def edit_profile(request):
    """
    Handles the editing of the user profile based on a submitted form.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.

    Returns:
    HttpResponse: A rendered HTML page for editing the user profile or a redirection
                  to the settings page after successful profile update.
    """
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('settings')
    else:
        form = EditProfileForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'edit_profile.html', context)

from django.contrib.auth import login, authenticate

@login_required
def CandidateView(request, pos):
  """
    Handles the view for a specific election position and candidate voting.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.
    - pos (int): The primary key of the Election object.

    Returns:
    HttpResponse: A rendered HTML page displaying election information and candidate list.
                  Handles user voting and redirects based on the voting outcome.
  """
  obj = get_object_or_404(Election, pk=pos)

  if request.method == "POST":
      candidate_id = request.POST.get('candidate_id')
      candidate = get_object_or_404(Candidate, pk=candidate_id)

      now = timezone.now()
      if not (obj.start_date <= now <= obj.end_date):
          request.session['message'] = 'Voting is not currently open for this election.'
          request.session['message_type'] = 'error'
          return redirect('elections')

      if UserVote.objects.filter(user=request.user, election=obj).exists():
          request.session['message'] = 'You have already voted in this election.'
          request.session['message_type'] = 'warning'
          return redirect('elections')

      control_vote, created = ControlVote.objects.get_or_create(user=request.user, position=candidate)
      if control_vote.status:
          request.session['message'] = 'You have already voted for this candidate.'
          request.session['message_type'] = 'warning'
          return redirect('elections')

      control_vote.status = True
      control_vote.save()

      UserVote.objects.create(user=request.user, election=obj).save()

      request.session['message'] = 'Your vote has been recorded. Thank you for voting!'
      request.session['message_type'] = 'success'
      return redirect('elections')

  else:
      candidates = Candidate.objects.filter(election=obj)
      candidates_dict = []
      for candidate in candidates:
          control_vote, _ = ControlVote.objects.get_or_create(user=request.user, position=candidate)
          candidates_dict.append({
              'candidate': candidate,
              'already_voted': control_vote.status
          })

      return render(request, 'elections.html', {'obj': obj, 'candidates': candidates_dict})


@login_required
@transaction.atomic
@csrf_protect
def voteView(request, election_id, candidate_id):
  """
    Handles user voting for a specific candidate in an election.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.
    - election_id (int): The primary key of the Election object.
    - candidate_id (int): The primary key of the Candidate object.

    Returns:
    HttpResponse: Redirects to the 'elections' page based on the voting outcome.
  """
  election = get_object_or_404(Election, pk=election_id)
  candidate = get_object_or_404(Candidate, pk=candidate_id)

  now = timezone.now()
  if not (election.start_date <= now <= election.end_date):
      request.session['message'] = 'Voting is not currently open for this election.'
      request.session['message_type'] = 'error'
      return redirect('elections')

  if UserVote.objects.filter(user=request.user, election=election).exists():
      request.session['message'] = 'You have already voted in this election.'
      request.session['message_type'] = 'warning'
      return redirect('elections')

  if ControlVote.objects.filter(user=request.user, position=candidate).exists():
      request.session['message'] = 'You have already voted for this candidate.'
      request.session['message_type'] = 'warning'
      return redirect('elections')

  ControlVote.objects.create(user=request.user, position=candidate).save()

  UserVote.objects.create(user=request.user, election=election).save()

  request.session['message'] = 'Your vote has been recorded. Thank you for voting!'
  request.session['message_type'] = 'success'

  return redirect('elections')

def clear_messages(request):
    """
    Clears any messages stored in the session.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.

    Returns:
    JsonResponse: A JSON response indicating the status of the operation.
    """
    request.session.pop('message', None)
    request.session.pop('message_type', None)
    return JsonResponse({'status': 'success'})
    
def contact(request):
    """
    Handles the contact form submission.

    Parameters:
    - request (HttpRequest): The Django HttpRequest object.

    Returns:
    HttpResponse: Redirects to the 'index' page after processing the contact form.
                  Displays a success message on successful form submission.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
         name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        
        subject = f'New message from {name}'
        message_body = f'Thank you for reaching out to us, {name}!\n\nWe have received your message and will get back to you as soon as possible.\n\nBest regards,\nThe iElect Team'
            
        send_mail(
                subject,
                message_body,
                email, 
                ['ielect43@gmail.com'],  
                fail_silently=False,
            )
        messages.success(request, 'Message sent successfully!')
        context = {'sent_message': True}

        return redirect('index')  
    else:
        form = ContactForm() 

    return render(request, 'contact_popup.html', {'form': form})  


