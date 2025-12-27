from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User
from django.contrib.auth.hashers import make_password

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a strong password',
            'class': 'form-control'
        }),
        required=True,
        min_length=8,
        error_messages={
            'required': 'Password is required',
            'min_length': 'Password must be at least 8 characters long'
        }
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'form-control'
        }),
        required=True,
        error_messages={'required': 'Please confirm your password'}
    )

    class Meta:
        model = User
        fields = ['id_number', 'first_name', 'last_name', 'phone_number', 'email', 'password']
        widgets = {
            'id_number': forms.TextInput(attrs={
                'placeholder': 'Enter your national ID number',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First name',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last name',
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': '0712 345 678 or 712 345 678',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'name@example.com',
                'class': 'form-control'
            }),
        }
        error_messages = {
            'id_number': {'required': 'ID number is required'},
            'first_name': {'required': 'First name is required'},
            'last_name': {'required': 'Last name is required'},
            'phone_number': {'required': 'Phone number is required'},
            'email': {'required': 'Email is required', 'invalid': 'Enter a valid email address'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add ID number validator (Kenyan IDs can be 8 or 9 digits)
        self.fields['id_number'].validators.append(
            RegexValidator(
                regex=r'^\d{8,9}$',
                message='Kenyan ID number must be 8 or 9 digits',
                code='invalid_id'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
        
        return cleaned_data

    # forms.py

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # 1. Remove all non-digits (keeps just 254740095168)
        digits = ''.join(filter(str.isdigit, phone))
        
        # 2. If it starts with 0, remove it (0740... -> 740...)
        if digits.startswith('0'):
            digits = digits[1:]
        
        # 3. If it starts with 254 and is long, it's already prefixed
        if digits.startswith('254') and len(digits) > 9:
            # Just use the digits as they are, but we'll add the + back
            clean_digits = digits
        else:
            # It's a raw number like 740...
            clean_digits = f"254{digits}"

        # 4. Final formatted number for storage
        formatted_phone = f"+{clean_digits}"
        
        # 5. Check uniqueness (VERY IMPORTANT)
        # Exclude the current user if this is an update form
        user_exists = User.objects.filter(phone_number=formatted_phone)
        if self.instance.pk:
            user_exists = user_exists.exclude(pk=self.instance.pk)
        
        if user_exists.exists():
            raise ValidationError('A user with this phone number already exists.')
        
        return formatted_phone

    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        # Remove any spaces or special characters
        cleaned_id = ''.join(filter(str.isdigit, id_number))
        
        if not cleaned_id:
            raise ValidationError('ID number is required')
        
        # Check length
        if len(cleaned_id) not in [8, 9]:
            raise ValidationError('ID number must be 8 or 9 digits')
        
        # Check uniqueness
        if User.objects.filter(id_number=cleaned_id).exists():
            raise ValidationError('A passenger with this ID number already exists.')
        
        return cleaned_id

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        
        if not email:
            raise ValidationError('Email is required')
        
        # Check uniqueness
        if User.objects.filter(email=email).exists():
            raise ValidationError('A passenger with this email already exists.')
        
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        
        # Phone number is already cleaned to 9 digits without 0
        # Format it to +254 for storage
        phone = self.cleaned_data['phone_number']
        user.phone_number = f'{phone}'
        
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Email or ID number',
            'class': 'form-control'
        }),
        error_messages={'required': 'Please enter your email or ID number'}
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control'
        }),
        required=True,
        error_messages={'required': 'Password is required'}
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        }),
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New password',
            'class': 'form-control'
        }),
        required=True,
        min_length=8,
        error_messages={
            'required': 'New password is required',
            'min_length': 'Password must be at least 8 characters long'
        }
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'class': 'form-control'
        }),
        required=True,
        error_messages={'required': 'Please confirm your new password'}
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
        
        return cleaned_data