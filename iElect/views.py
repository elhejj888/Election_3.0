import json
from django.urls import reverse, reverse_lazy
import requests
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.mail import send_mail
from .forms import ContactForm

from iElect.models import Candidate, ControlVote
from .forms import RegistrationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from .forms import EditProfileForm
from django.contrib import messages

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjBhM2I2MTRjLWQ2ZjQtNGRkOS04M2RmLTIzNmZiMjBjNzg1OCIsIm9yZ0lkIjoiMzY5NTYzIiwidXNlcklkIjoiMzc5ODE2IiwidHlwZUlkIjoiOTNiZDhjOWYtNTViZC00ZmFmLThiMTQtNTZhYTFhZmIyMjZhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MDM1MjQ5NTcsImV4cCI6NDg1OTI4NDk1N30.CrZJcIyqcCdYMtM45pbRB4tY7-fOqwxSRhEtmE_dba0'

def moralis_auth(request):
   return render(request, 'login.html', {})


def request_message(request):
   data = json.loads(request.body)
   print(data)

   REQUEST_URL = 'https://authapi.moralis.io/challenge/request/evm'
   
   # Adjusted expiration time to 5 minutes from the current time
   expiration_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat() + "Z"

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
      # user can authenticate
      eth_address = json.loads(x.text).get('address')
      print("eth address", eth_address)
      try:
          user = User.objects.get(username=eth_address)
      except User.DoesNotExist:
          # If user does not exist, create a new user
          user = User.objects.create_user(username=eth_address, password=None)
          user.save()
          # Set a flag in the session to indicate that the user needs to complete the registration process
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
      # If user does not exist, create a new user
      user = User.objects.create_user(username= eth_address, password=None)
      user.save()
      # Set a flag in the session to indicate that the user needs to complete the registration process
      request.session['needs_registration'] = True
      return JsonResponse(json.loads(x.text))

@login_required(login_url='/auth')
def register(request):
 if request.method == 'POST':
     form = RegistrationForm(request.POST)
     print("Form submitted") # Debugging print statement

     if form.is_valid():
         print("Form is valid") # Debugging print statement
         print("Form data: ", form.cleaned_data) # Debugging print statement
         eth_address = request.session.get('verified_data', {}).get('address')

         if not eth_address:
             return JsonResponse({'error': 'No Ethereum address provided'})

         try:
             user = User.objects.get(username=eth_address)
             print(f"User exists: {user}") # Debugging print statement
         except User.DoesNotExist:
             user = User.objects.create_user(username=eth_address, password=None)
             print(f"Created new user: {user}")

         # Update the existing user with the form data
         form.save(commit=False)
         user.email = form.cleaned_data['email']
         user.first_name = form.cleaned_data['first_name']
         user.last_name = form.cleaned_data['last_name']
         user.password = form.cleaned_data['password']
         user.save()

         print(f"Updated user data: {user}")

         # Authenticate the user
         login(request, user)

         # Remove 'needs_registration' from the session after registration
         if 'needs_registration' in request.session:
             del request.session['needs_registration']

         # Redirect to my_profile
         return redirect('my_profile')

     else:
         # If the form is not valid, print the form errors
         print("Form errors: ", form.errors) # Debugging print statement
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
from django.shortcuts import redirect


def admin_auto_login(request):
    # Check if the user is an admin
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('index')  # Redirect to the home page if already logged in

    # If not logged in as an admin, perform automatic login
    admin_user = authenticate(username='admin', password='your_admin_password')  # Change the password accordingly
    if admin_user is not None:
        login(request, admin_user)
        return redirect('index')  # Redirect to the home page after login

    return redirect('login')  # Redirect to the login page if auto-login fails
from .models import Election,Candidate,ControlVote

@login_required
def CandidateDetailView(request, id):
    # The obj variable is used to store the Candidate object
    obj = get_object_or_404(Candidate, pk=id)
    
    # The render function is used to render the candidate detail page
    # obj is passed to the candidate detail page to display the details of the candidate
    return render(request, "", {'obj': obj})
from .models import Election,Candidate,ControlVote

@login_required
def CandidateDetailView(request, id):
    # The obj variable is used to store the Candidate object
    obj = get_object_or_404(Candidate, pk=id)
    
    # The render function is used to render the candidate detail page
    # obj is passed to the candidate detail page to display the details of the candidate
    return render(request, "/candidate_detail.html", {'obj': obj})
from .models import Election,Candidate,ControlVote
@login_required

def CandidateView(request, pos):
    # The obj variable is used to store the position object
    obj = get_object_or_404(Election, pk = pos)
    # if statement is used to check if the request method is POST
    if request.method == "POST":
        # The temp variable is used to store the ControlVote object 
        # it is used to check if the user has already voted for the position
        temp = ControlVote.objects.get_or_create(user=request.user, position=obj)[0]
        # if statement is used to check if the user has already voted for the position
        if temp.status == False:
            # The temp2 variable is used to store the Candidate object
            # The total_vote of the candidate is incremented by 1
            # The status of the ControlVote object is changed to True
            # The user is redirected to the position page
            temp2 = Candidate.objects.get(pk=request.POST.get(obj.title))
            temp2.total_vote += 1
            temp2.save()
            temp.status = True
            temp.save()
            return HttpResponseRedirect('/position/')
        else:
            # if the user has already voted for the position then the user is redirected to the position page
            # and the error message is displayed
            messages.success(request, 'you have already been voted this position.')
            return render(request, 'poll/candidate.html', {'obj':obj})
    else:
        # if the request method is not POST then the render function is used to render the candidate page
        return render(request, 'poll/candidate.html', {'obj':obj})

@login_required    

def ElectionView(request):
    # The obj variable is used to store the list of positions
    obj = Election.objects.all()
    # The render function is used to render the position page
    # obj is passed to the position page to display the list of positions
    return render(request, "poll/position.html", {'obj':obj})
@login_required
def resultView(request):
    # The obj variable is used to store the list of Candidate objects
    obj = Candidate.objects.all().order_by('position','-total_vote')
    # The render function is used to render the result page
    return render(request, "", {'obj':obj})
    
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


def contact(request):
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

        return redirect('index')  # Redirect to the index page after successful submission
    else:
        form = ContactForm()  # Instantiate the ContactForm

    return render(request, 'contact_popup.html', {'form': form})  # Make sure to use the correct template name


