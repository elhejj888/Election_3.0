import json
from django.urls import reverse, reverse_lazy
import requests
import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
         return redirect('dashboard')

     else:
         # If the form is not valid, print the form errors
         print("Form errors: ", form.errors) # Debugging print statement
         return JsonResponse({'status': 'error', 'errors': form.errors})

 else:
     form = RegistrationForm()

 return render(request, 'register.html', {'form': form})


def get_success_url(self):
    return reverse('my_profile')

@login_required(login_url='/my_profile')
def my_profile(request):
  user = request.user
  eth_address = user.username

  if User.objects.filter(username=eth_address).exists():
      if 'needs_registration' in request.session:
          del request.session['needs_registration']
          return redirect('register')
      else:
          return render(request, 'profile.html', {'user': request.user})
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



