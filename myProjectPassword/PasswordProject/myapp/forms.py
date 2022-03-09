from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Password


class MyUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PasswordForm(ModelForm):

    class Meta:
        model = Password
        fields = ('url', 'username', 'password')
        exclude = ('logo', 'user', 'name')