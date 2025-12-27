from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.template import loader
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import User
from .forms import LoginForm, SignupForm, ForgotPasswordForm

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # 'username' is the field name from your LoginForm class
        login_input = form.cleaned_data['username'] 
        password = form.cleaned_data['password']
        
        try:
            # Search for a passenger matching the input in any of the three fields
            passenger = User.objects.get(
                Q(id_number=login_input) | 
                Q(email=login_input) | 
                Q(first_name=login_input) # Or username if you have that field
            )
            
            # Check the hashed password
            if check_password(password, passenger.password):
                request.session['passenger_id'] = passenger.id
                return redirect('dashboard')
            else:
                form.add_error('password', 'Incorrect password')
                
        except User.DoesNotExist:
            form.add_error('username', 'Account not found with that Email or ID')

    return render(request, 'auth/login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            passenger = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = SignupForm()
    
    return render(request, 'auth/signup.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Here you would typically:
            # 1. Generate a password reset token
            # 2. Send an email with reset link
            # 3. Show success message
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('login')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'auth/forgot_password.html', {'form': form})

def dashboard(request):
    # Check if user is logged in
    if 'passenger_id' not in request.session:
        messages.error(request, 'Please login to access dashboard')
        return redirect('login')
    
    passenger_id = request.session['passenger_id']
    try:
        passenger = User.objects.get(id=passenger_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')
    
    context = {
        'passenger': passenger,
    }
    return render(request, 'passenger/dashboard.html', context)

def logout(request):
    # Clear the session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# @login_required
def passenger(request):
    return render(request, 'passenger/dashboard.html')

def sacco(request):
    return render(request, 'sacco/dashboard.html')

def admin(request):
    return render(request, 'admin/dashboard.html')

def driver(request):
    return render(request, 'driver/dashboard.html')

def conductor(request):
    return render(request, 'conductor/dashboard.html')