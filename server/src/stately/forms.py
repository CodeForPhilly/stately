from django import forms

class SendAuthTokenForm (forms.Form):
    email = forms.EmailField()
