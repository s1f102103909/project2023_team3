from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class ChatForm(forms.Form):
    prompt = forms.CharField(label='チャット', widget=forms.Textarea(), required=True)

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        