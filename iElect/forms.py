from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class RegistrationForm(forms.ModelForm):
   email = forms.EmailField(max_length=255)
   first_name = forms.CharField(max_length=255)
   last_name = forms.CharField(max_length=255)
   password = forms.CharField(widget=forms.PasswordInput())

   class Meta:
       model = User
       fields = ['email', 'first_name', 'last_name', 'password']


class EditProfileForm(UserChangeForm):
    first_name = forms.CharField(label="First Name:",
                                 max_length=32, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Last Name:",
                                max_length=32, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email",
                             max_length=50, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="",
                               max_length=50, widget=forms.PasswordInput(attrs={'type': 'hidden'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name','email']