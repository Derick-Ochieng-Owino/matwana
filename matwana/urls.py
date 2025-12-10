from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from matwanacore.views import (
    passenger_signup, driver_signup, conductor_signup,
    sacco_admin_signup, login_view, dashboard,
    passenger_dashboard, driver_dashboard, conductor_dashboard, admin_dashboard,
    forgot_password
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ROOT URL redirects to login
    path('', lambda request: redirect('login'), name='home'),
    path('', include('matwanacore.urls')),
    path("login/", login_view, name="login"),

    path("signup/passenger/", passenger_signup, name="signup_passenger"),
    path("signup/driver/", driver_signup, name="signup_driver"),
    path("signup/conductor/", conductor_signup, name="signup_conductor"),
    path("signup/admin/", sacco_admin_signup, name="signup_admin"),

    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/passenger/", passenger_dashboard, name="passenger_dashboard"),
    path("dashboard/driver/", driver_dashboard, name="driver_dashboard"),
    path("dashboard/conductor/", conductor_dashboard, name="conductor_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),

    path("forgot_password/", forgot_password, name="forgot_password"),
]
