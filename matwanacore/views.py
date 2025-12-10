# views.py - Fix the imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MatwanaUser, Route, Vehicle, Sacco  # Added Sacco here
from .forms import PassengerSignupForm, DriverSignupForm, ConductorSignupForm, AdminSignupForm, AddSaccoForm

def require_matwana_user(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            request.user.matwanauser
        except MatwanaUser.DoesNotExist:
            MatwanaUser.objects.create(
                user=request.user,
                role="passenger",
                phone=""
            )
            messages.info(request, "A default passenger profile has been created for you.")
        
        return view_func(request, *args, **kwargs)
    return wrapper

def signup(request):
    return render(request, "auth/signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username") or request.POST.get("email")
        password = request.POST.get("password")
        
        print(f"DEBUG: Login attempt - Username: {username}, Password: {password}")
        
        user = authenticate(request, username=username, password=password)
        
        print(f"DEBUG: Authentication result - User: {user}")
        
        if user is not None:
            login(request, user)
            print(f"DEBUG: User logged in - {user.username}")
            
            # Get or create MatwanaUser profile
            try:
                profile = MatwanaUser.objects.get(user=user)
                print(f"DEBUG: MatwanaUser found - Role: {profile.role}")
            except MatwanaUser.DoesNotExist:
                profile = MatwanaUser.objects.create(
                    user=user,
                    role="passenger",
                    phone=""
                )
                print(f"DEBUG: MatwanaUser created - Role: {profile.role}")
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Debug print before redirect
            print(f"DEBUG: Redirecting based on role: {profile.role}")
            
            # Redirect based on role
            if profile.role == 'passenger':
                return redirect('passenger_dashboard')
            elif profile.role == 'driver':
                return redirect('driver_dashboard')
            elif profile.role == 'conductor':
                return redirect('conductor_dashboard')
            elif profile.role == 'sacco':
                return redirect('sacco_dashboard')
            elif profile.role == 'admin':
                return redirect('admin_dashboard')
            else:
                print(f"DEBUG: Unknown role: {profile.role}, redirecting to dashboard")
                return redirect('dashboard')
        else:
            print("DEBUG: Authentication failed")
            messages.error(request, "Invalid credentials")
    
    return render(request, "auth/login.html")

# Enhanced Passenger Signup
def passenger_signup(request):
    if request.method == "POST":
        form = PassengerSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                # Create user with first_name and last_name if provided
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )
                
                # Create MatwanaUser profile
                MatwanaUser.objects.create(
                    user=user,
                    role="passenger",
                    phone=data.get('phone', '')
                )
                
                # Auto-login the user
                login(request, user)
                messages.success(request, 'Passenger account created successfully!')
                return redirect('passenger_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Form is invalid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PassengerSignupForm()
    
    return render(request, "auth/signup_passenger.html", {"form": form})

# Enhanced Driver Signup
def driver_signup(request):
    if request.method == "POST":
        form = DriverSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )
                
                MatwanaUser.objects.create(
                    user=user,
                    role="driver",
                    phone=data.get('phone', '')
                )
                
                login(request, user)
                messages.success(request, 'Driver account created successfully!')
                return redirect('driver_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = DriverSignupForm()
    
    return render(request, "auth/signup_driver.html", {"form": form})

# Enhanced Conductor Signup
def conductor_signup(request):
    if request.method == "POST":
        form = ConductorSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )
                
                MatwanaUser.objects.create(
                    user=user,
                    role="conductor",
                    phone=data.get('phone', '')
                )
                
                login(request, user)
                messages.success(request, 'Conductor account created successfully!')
                return redirect('conductor_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ConductorSignupForm()
    
    return render(request, "auth/signup_conductor.html", {"form": form})

# Enhanced Sacco Admin Signup (IMPORTANT: Role should be 'sacco' not 'admin')
def sacco_admin_signup(request):
    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )
                
                # CRITICAL: Role should be 'sacco' for sacco admin
                MatwanaUser.objects.create(
                    user=user,
                    role="sacco",  # NOT 'admin' - that's for system admin
                    phone=data.get('phone', '')
                )
                
                login(request, user)
                messages.success(request, 'Sacco Admin account created successfully!')
                return redirect('sacco_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AdminSignupForm()
    
    return render(request, "auth/signup_admin.html", {"form": form})

# System Admin Signup (This should be restricted or have additional verification)
def system_admin_signup(request):
    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )
                
                # System admin role
                MatwanaUser.objects.create(
                    user=user,
                    role="admin",  # System admin
                    phone=data.get('phone', '')
                )
                
                login(request, user)
                messages.success(request, 'System Admin account created successfully!')
                return redirect('admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AdminSignupForm()
    
    return render(request, "auth/signup_system_admin.html", {"form": form})

# views.py - Update dashboard function
@login_required
def dashboard(request):
    try:
        # Try to get existing MatwanaUser
        profile = request.user.matwanauser
    except MatwanaUser.DoesNotExist:
        # Create one if it doesn't exist
        profile = MatwanaUser.objects.create(
            user=request.user,
            role="passenger",
            phone=""
        )
        messages.info(request, "A passenger profile has been created for you.")
    
    print(f"DEBUG: User role is '{profile.role}'")
    
    # Redirect based on role
    if profile.role == 'passenger':
        return redirect('passenger_dashboard')
    elif profile.role == 'driver':
        return redirect('driver_dashboard')
    elif profile.role == 'conductor':
        return redirect('conductor_dashboard')
    elif profile.role == 'sacco':
        return redirect('sacco_dashboard')
    elif profile.role == 'admin':
        return redirect('admin_dashboard')
    else:
        # Default fallback
        return redirect('passenger_dashboard')

@login_required
@require_matwana_user
def passenger_dashboard(request):
    routes = Route.objects.filter(active=True)
    profile = request.user.matwanauser
    
    # Only passengers can access this
    if profile.role != 'passenger':
        messages.warning(request, "You don't have permission to access the passenger dashboard.")
        return redirect('dashboard')
    
    return render(request, "dashboard/passenger.html", {
        "routes": routes,
        "profile": profile
    })

@login_required
@require_matwana_user
def driver_dashboard(request):
    profile = request.user.matwanauser
    
    # Only drivers can access this
    if profile.role != 'driver':
        messages.warning(request, "You don't have permission to access the driver dashboard.")
        return redirect('dashboard')
    
    return render(request, "dashboard/driver.html", {"profile": profile})

@login_required
@require_matwana_user
def conductor_dashboard(request):
    profile = request.user.matwanauser
    
    # Only conductors can access this
    if profile.role != 'conductor':
        messages.warning(request, "You don't have permission to access the conductor dashboard.")
        return redirect('dashboard')
    
    return render(request, "dashboard/conductor.html", {"profile": profile})

@login_required
@require_matwana_user
def sacco_dashboard(request):
    profile = request.user.matwanauser
    
    # Only sacco admins can access this
    if profile.role != 'sacco':
        messages.warning(request, "You don't have permission to access the sacco dashboard.")
        return redirect('dashboard')
    
    # Get the sacco managed by this user
    try:
        sacco = Sacco.objects.get(admin_user=profile)
    except Sacco.DoesNotExist:
        sacco = None
        messages.info(request, "You haven't been assigned to manage any sacco yet.")
    
    return render(request, "dashboard/sacco.html", {
        "profile": profile,
        "sacco": sacco
    })

@login_required
@require_matwana_user
def admin_dashboard(request):
    profile = request.user.matwanauser
    
    # Only system admins can access this
    if profile.role != 'admin':
        messages.warning(request, "You don't have permission to access the system admin dashboard.")
        return redirect('dashboard')
    
    # Fetch ALL Saccos to populate the dropdowns
    available_saccos = Sacco.objects.all().order_by('name')
    
    return render(request, "dashboard/admin.html", {
        'saccos_list': available_saccos,
        'profile': profile
    })

@login_required
def passenger_route_view(request, route_id):
    route = get_object_or_404(Route, pk=route_id)
    # template will pull vehicles via API or websocket
    return render(request, "passenger/route_view.html", {"route": route})

# Add this function to your matwanacore/views.py
def forgot_password(request):
    # This is a placeholder for future password reset logic
    return render(request, "auth/forgot_password.html")

def add_sacco(request):
    if request.method == 'POST':
        form = AddSaccoForm(request.POST)
        if form.is_valid():
            # Process form data
            sacco_name = form.cleaned_data['sacco_name']
            # Save to database, etc.
            return redirect('sacco_list')
    else:
        form = AddSaccoForm()
    
    return render(request, 'dashboard.html', {'sacco_form': form})