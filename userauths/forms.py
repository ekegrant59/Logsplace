from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from .models import User
from core.models import Logs

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
class LogDetailsForm(forms.Form):
    log = forms.ModelChoiceField(queryset=Logs.objects.all(), required=True)
    details = forms.CharField(widget=forms.Textarea, required=True, help_text="Enter details separated by '*'")