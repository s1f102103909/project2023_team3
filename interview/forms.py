from django import forms

class ChatForm(forms.Form):
    prompt = forms.CharField(label='チャット', widget=forms.Textarea(), required=True)