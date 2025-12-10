from django.urls import path, include
from rest_framework import routers
from . import views, api_views

router = routers.DefaultRouter()
router.register('routes', api_views.RouteViewSet, basename='route')
router.register('vehicles', api_views.VehicleViewSet, basename='vehicle')
router.register('trips', api_views.TripViewSet)
router.register('tickets', api_views.TicketViewSet)
router.register('payments', api_views.PaymentViewSet)
router.register('gps', api_views.GPSReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_choice, name='signup_choice'),
    path('signup/passenger/', views.passenger_signup, name='signup_passenger'),
    path('signup/driver/', views.driver_signup, name='signup_driver'),
    path('signup/conductor/', views.conductor_signup, name='signup_conductor'),
    path('signup/admin/', views.sacco_admin_signup, name='signup_admin'),
    path('forgot_password/', lambda r: render(r, 'auth/forgot_password.html'), name='forgot_password'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/passenger/', views.passenger_dashboard, name='passenger_dashboard'),
    path('dashboard/driver/', views.driver_dashboard, name='driver_dashboard'),
    path('dashboard/conductor/', views.conductor_dashboard, name='conductor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    path('passenger/route/<int:route_id>/', views.passenger_route_view, name='passenger_route_view'),
]
