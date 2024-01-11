from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
   email = forms.EmailField(max_length=255)
   first_name = forms.CharField(max_length=255)
   last_name = forms.CharField(max_length=255)
   password = forms.CharField(widget=forms.PasswordInput())

   class Meta:
       model = User
       fields = ['email', 'first_name', 'last_name', 'password']
