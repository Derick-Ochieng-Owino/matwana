# forms.py - Update your forms to include first_name and last_name
from django import forms
from django.contrib.auth.models import User
from .models import MatwanaUser
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, date
import re

class BaseSignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
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
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            # Add the error to the password_confirm field specifically
            self.add_error('password_confirm', "Passwords do not match.")
        
        return cleaned_data

class PassengerSignupForm(BaseSignupForm):
    pass

class DriverSignupForm(BaseSignupForm):
    license_number = forms.CharField(max_length=50, required=False, label="Driver's License Number")
    
class ConductorSignupForm(BaseSignupForm):
    badge_number = forms.CharField(max_length=50, required=False, label="Conductor Badge Number")
    
class AdminSignupForm(BaseSignupForm):
    id_number = forms.CharField(max_length=50, required=False, label="ID Number")

class AddSaccoForm(forms.Form):
    """Form for registering new Saccos"""
    sacco_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter sacco name',
            'id': 'saccoName'
        }),
        label="Sacco Name",
        help_text="Enter the official name of the transport Sacco"
    )
    
    registration_no = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., MW/001/2023',
            'id': 'registrationNo'
        }),
        label="Registration Number",
        help_text="Official registration number from transport authority"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'contact@sacco.com',
            'id': 'saccoEmail'
        }),
        label="Email Address",
        validators=[EmailValidator(message="Please enter a valid email address")]
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+254712345678'. Up to 15 digits allowed."
    )
    
    phone_number = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '07XX XXX XXX',
            'id': 'phoneNumber'
        }),
        label="Phone Number",
        validators=[phone_regex]
    )
    
    physical_address = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter physical address',
            'id': 'physicalAddress'
        }),
        label="Physical Address"
    )
    
    admin_contact = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of contact person',
            'id': 'adminContact'
        }),
        label="Admin Contact Person"
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Brief description of the sacco',
            'id': 'saccoDescription'
        }),
        label="Description",
        max_length=500
    )
    
    def clean_registration_no(self):
        registration_no = self.cleaned_data.get('registration_no')
        # Add custom validation for registration number format
        if not re.match(r'^[A-Z]{2,3}/\d{3,4}/\d{4}$', registration_no):
            raise forms.ValidationError(
                "Registration number must be in format: 'ABC/123/2023'"
            )
        return registration_no
    
    def clean(self):
        cleaned_data = super().clean()
        # You can add cross-field validation here if needed
        return cleaned_data


class AddDriverForm(forms.Form):
    """Form for registering new drivers"""
    
    # Sacco choices would typically come from the database
    SACCO_CHOICES = [
        ('', 'Choose a sacco'),
        ('MW001', 'Matwana Sacco'),
        ('MT002', 'Metro Trans Sacco'),
        ('CC003', 'City Connect Sacco'),
        ('SS004', 'Speed Shuttle Sacco'),
    ]
    
    MATATU_CHOICES = [
        ('', 'Not assigned yet'),
        ('KCA123X', 'KCA 123X'),
        ('KBB456Y', 'KBB 456Y'),
        ('KCD789Z', 'KCD 789Z'),
    ]
    
    sacco = forms.ChoiceField(
        choices=SACCO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'driverSacco'
        }),
        label="Select Sacco"
    )
    
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'id': 'driverFirstName'
        }),
        label="First Name"
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'id': 'driverLastName'
        }),
        label="Last Name"
    )
    
    national_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ID number',
            'id': 'driverID'
        }),
        label="National ID",
        validators=[RegexValidator(
            regex=r'^\d{6,8}$',
            message="National ID must be 6-8 digits"
        )]
    )
    
    phone_number = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '07XX XXX XXX',
            'id': 'driverPhone'
        }),
        label="Phone Number",
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Enter a valid phone number"
        )]
    )
    
    license_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DL-XXXXXX',
            'id': 'driverLicense'
        }),
        label="License Number",
        help_text="Enter driver's license number"
    )
    
    license_expiry = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'licenseExpiry'
        }),
        label="License Expiry",
        help_text="License expiry date"
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'driver@email.com',
            'id': 'driverEmail'
        }),
        label="Email Address"
    )
    
    assigned_matatu = forms.ChoiceField(
        required=False,
        choices=MATATU_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'assignedMatatu'
        }),
        label="Assign to Matatu"
    )
    
    def clean_license_expiry(self):
        expiry_date = self.cleaned_data.get('license_expiry')
        if expiry_date and expiry_date < date.today():
            raise forms.ValidationError("License has already expired!")
        return expiry_date
    
    def clean_license_number(self):
        license_no = self.cleaned_data.get('license_number')
        # Validate license number format (Kenyan format example)
        if not re.match(r'^[A-Z]{2}\d{6,8}$', license_no.upper()):
            raise forms.ValidationError(
                "License number should be in format: 'AB123456'"
            )
        return license_no.upper()


class AddConductorForm(forms.Form):
    """Form for registering new conductors"""
    
    SACCO_CHOICES = [
        ('', 'Choose a sacco'),
        ('MW001', 'Matwana Sacco'),
        ('MT002', 'Metro Trans Sacco'),
        ('CC003', 'City Connect Sacco'),
        ('SS004', 'Speed Shuttle Sacco'),
    ]
    
    MATATU_CHOICES = [
        ('', 'Not assigned yet'),
        ('KCA123X', 'KCA 123X'),
        ('KBB456Y', 'KBB 456Y'),
        ('KCD789Z', 'KCD 789Z'),
    ]
    
    sacco = forms.ChoiceField(
        choices=SACCO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'conductorSacco'
        }),
        label="Select Sacco"
    )
    
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'id': 'conductorFirstName'
        }),
        label="First Name"
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'id': 'conductorLastName'
        }),
        label="Last Name"
    )
    
    national_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ID number',
            'id': 'conductorID'
        }),
        label="National ID",
        validators=[RegexValidator(
            regex=r'^\d{6,8}$',
            message="National ID must be 6-8 digits"
        )]
    )
    
    phone_number = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '07XX XXX XXX',
            'id': 'conductorPhone'
        }),
        label="Phone Number",
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Enter a valid phone number"
        )]
    )
    
    badge_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CB-XXXXX',
            'id': 'badgeNumber'
        }),
        label="Badge Number",
        help_text="Conductor's official badge number"
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'conductor@email.com',
            'id': 'conductorEmail'
        }),
        label="Email Address"
    )
    
    experience_years = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '50',
            'placeholder': 'Years of experience',
            'id': 'conductorExperience'
        }),
        label="Experience (Years)",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(50)
        ],
        help_text="Years of experience as a conductor"
    )
    
    assigned_matatu = forms.ChoiceField(
        required=False,
        choices=MATATU_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'assignedToMatatu'
        }),
        label="Assign to Matatu"
    )
    
    def clean_badge_number(self):
        badge_no = self.cleaned_data.get('badge_number')
        # Validate badge number format
        if not re.match(r'^CB-\d{4,6}$', badge_no.upper()):
            raise forms.ValidationError(
                "Badge number should be in format: 'CB-12345'"
            )
        return badge_no.upper()


class SaccoSearchForm(forms.Form):
    """Form for searching/filtering Saccos"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, registration number...',
            'style': 'width: 300px;'
        }),
        label="Search Saccos"
    )
    
    status_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('pending', 'Pending'),
            ('suspended', 'Suspended'),
            ('inactive', 'Inactive'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 150px;'
        }),
        label="Status"
    )


class DriverSearchForm(forms.Form):
    """Form for searching/filtering drivers"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, license, phone...',
            'style': 'width: 300px;'
        }),
        label="Search Drivers"
    )
    
    sacco_filter = forms.ChoiceField(
        required=False,
        choices=AddDriverForm.SACCO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 200px;'
        }),
        label="Sacco"
    )
    
    status_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('on_leave', 'On Leave'),
            ('suspended', 'Suspended'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 150px;'
        }),
        label="Status"
    )


class ConductorSearchForm(forms.Form):
    """Form for searching/filtering conductors"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, badge, phone...',
            'style': 'width: 300px;'
        }),
        label="Search Conductors"
    )
    
    sacco_filter = forms.ChoiceField(
        required=False,
        choices=AddConductorForm.SACCO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 200px;'
        }),
        label="Sacco"
    )


class PlatformReportForm(forms.Form):
    """Form for generating platform reports"""
    REPORT_TYPES = [
        ('overview', 'Platform Overview'),
        ('revenue', 'Revenue Analysis'),
        ('growth', 'Growth Statistics'),
        ('activity', 'User Activity'),
        ('comprehensive', 'Comprehensive Report'),
    ]
    
    DATE_RANGE = [
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('quarter', 'This Quarter'),
        ('year', 'This Year'),
        ('custom', 'Custom Range'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'reportType'
        }),
        label="Report Type",
        initial='overview'
    )
    
    date_range = forms.ChoiceField(
        choices=DATE_RANGE,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'dateRange',
            'onchange': 'toggleCustomDates()'
        }),
        label="Date Range",
        initial='month'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'startDate'
        }),
        label="Start Date"
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'endDate'
        }),
        label="End Date"
    )
    
    include_saccos = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'includeSaccos'
        }),
        label="Include Sacco Details",
        initial=True
    )
    
    include_drivers = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'includeDrivers'
        }),
        label="Include Driver Statistics",
        initial=True
    )
    
    include_financials = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'includeFinancials'
        }),
        label="Include Financial Data",
        initial=True
    )
    
    report_format = forms.ChoiceField(
        choices=[
            ('pdf', 'PDF Document'),
            ('excel', 'Excel Spreadsheet'),
            ('csv', 'CSV File'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label="Output Format",
        initial='pdf'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_range = cleaned_data.get('date_range')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if date_range == 'custom':
            if not start_date:
                self.add_error('start_date', 'Start date is required for custom range')
            if not end_date:
                self.add_error('end_date', 'End date is required for custom range')
            if start_date and end_date and start_date > end_date:
                self.add_error('start_date', 'Start date cannot be after end date')
        
        return cleaned_data


class EditSaccoForm(AddSaccoForm):
    """Form for editing existing Sacco details"""
    # Could add additional fields or modify existing ones for editing
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'saccoStatus'
        }),
        label="Status"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes or comments',
            'id': 'saccoNotes'
        }),
        label="Administrator Notes"
    )


# If you're using Django models, you could also create ModelForms
# class SaccoModelForm(forms.ModelForm):
#     class Meta:
#         model = Sacco  # Assuming you have a Sacco model
#         fields = ['name', 'registration_no', 'email', 'phone_number', 
#                  'physical_address', 'admin_contact', 'description']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sacco name'}),
#             'registration_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MW/001/2023'}),
#             # ... add other widgets as needed
#         }