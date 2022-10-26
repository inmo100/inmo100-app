from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#custom form for new user registration
class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'input'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'input'}))
    last_name = forms.CharField(max_length=70, widget=forms.TextInput(attrs={'class':'input'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] =  'input'
        self.fields['password1'].widget.attrs['class'] =  'input'
        self.fields['password2'].widget.attrs['class'] =  'input'

#custom form for login as a user
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username","class": "input"}), error_messages={'required': 'The username field is required.'})
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password","class": "input"}), error_messages={'required': 'The password field is required.'})
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "input"}))
