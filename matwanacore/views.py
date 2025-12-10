from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import MatwanaUser, Route, Vehicle
from .forms import PassengerSignupForm, DriverSignupForm, ConductorSignupForm, AdminSignupForm
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username") or request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, "auth/login.html", {"error": "Invalid credentials"})
    return render(request, "auth/login.html")

def signup_choice(request):
    return render(request, "auth/signup_choice.html")

def passenger_signup(request):
    if request.method == "POST":
        form = PassengerSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            MatwanaUser.objects.create(user=user, role="passenger", phone=data.get('phone'))
            login(request, user)
            return redirect('dashboard')
    else:
        form = PassengerSignupForm()
    return render(request, "auth/signup_passenger.html", {"form": form})

def driver_signup(request):
    if request.method == "POST":
        form = DriverSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            MatwanaUser.objects.create(user=user, role="driver", phone=data.get('phone'))
            login(request, user)
            return redirect('dashboard')
    else:
        form = DriverSignupForm()
    return render(request, "auth/signup_driver.html", {"form": form})

def conductor_signup(request):
    if request.method == "POST":
        form = ConductorSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            MatwanaUser.objects.create(user=user, role="conductor", phone=data.get('phone'))
            login(request, user)
            return redirect('dashboard')
    else:
        form = ConductorSignupForm()
    return render(request, "auth/signup_conductor.html", {"form": form})

def sacco_admin_signup(request):
    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            MatwanaUser.objects.create(user=user, role="admin", phone=data.get('phone'))
            login(request, user)
            return redirect('dashboard')
    else:
        form = AdminSignupForm()
    return render(request, "auth/signup_admin.html", {"form": form})

@login_required
def dashboard(request):
    # Guaranteed MatwanaUser exists
    profile, created = MatwanaUser.objects.get_or_create(
        user=request.user,
        defaults={"role": "passenger"}  # or default role
    )

    print(f"DEBUG: User role is '{profile.role}'")

    if profile.role == 'passenger':
        return redirect('passenger_dashboard')
    if profile.role == 'driver':
        return redirect('driver_dashboard')
    if profile.role == 'conductor':
        return redirect('conductor_dashboard')
    if profile.role == 'admin':
        return redirect('admin_dashboard')

    return render(request, "dashboard/role_error.html", {"error": "User role is invalid or missing."})


@login_required
def passenger_dashboard(request):
    routes = Route.objects.filter(active=True)
    return render(request, "dashboard/passenger.html", {"routes": routes})

@login_required
def driver_dashboard(request):
    return render(request, "dashboard/driver.html")

@login_required
def conductor_dashboard(request):
    return render(request, "dashboard/conductor.html")

@login_required
def sacco_dashboard(request):
    return render(request, "dashboard/sacco.html")

@login_required
def admin_dashboard(request):
    # admin metrics will be added later
    return render(request, "dashboard/admin.html")

@login_required
def passenger_route_view(request, route_id):
    route = get_object_or_404(Route, pk=route_id)
    # template will pull vehicles via API or websocket
    return render(request, "passenger/route_view.html", {"route": route})

# Add this function to your matwanacore/views.py
def forgot_password(request):
    # This is a placeholder for future password reset logic
    return render(request, "auth/forgot_password.html")