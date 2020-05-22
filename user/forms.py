from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)