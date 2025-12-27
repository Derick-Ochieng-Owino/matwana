from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/', views.admin, name='admin'),
    path('conductor/', views.conductor, name='conductor'),
    path('passenger/', views.passenger, name='passenger'),
    path('driver/', views.sacco, name='sacco'),
    path('sacco/', views.driver, name='driver'),
]