from django import forms
from django.forms import fields
from django.forms.widgets import PasswordInput
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Create New Password'}))
    confirm_password = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs) -> None:
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if self.fields[field].help_text != '':
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].help_text
            
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("New Password and Confirm Password Doesn't Match")


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput())
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'profile_picture', 'city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'