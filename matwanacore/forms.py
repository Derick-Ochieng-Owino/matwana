from django import forms
from django.contrib.auth.models import User
from .models import MatwanaUser

class BaseSignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    # Ensure password field has a minimum length for security
    password = forms.CharField(widget=forms.PasswordInput, min_length=8) 
    password_confirm = forms.CharField(widget=forms.PasswordInput, min_length=8)
    phone = forms.CharField(max_length=30, required=False)
    
    # ----------------------------------------------------
    # UNQUE FIELD VALIDATION
    # ----------------------------------------------------
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    # ----------------------------------------------------
    # PASSWORD MATCH VALIDATION
    # ----------------------------------------------------
    def clean(self):
        super().clean()
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            # Add the error to the password_confirm field specifically
            self.add_error('password_confirm', "Passwords do not match.")
        
        # as add_error updates the form's error list directly.
        return self.cleaned_data

class PassengerSignupForm(BaseSignupForm):
    pass

class DriverSignupForm(BaseSignupForm):
    pass

class ConductorSignupForm(BaseSignupForm):
    pass

class AdminSignupForm(BaseSignupForm):
    pass
