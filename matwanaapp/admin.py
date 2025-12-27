from django.contrib import admin
from .models import User, Sacco, Matatu, Route, Trip, PassengerTrip, Payment, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'user_type', 'is_verified')
    list_filter = ('user_type', 'is_active', 'is_verified')
    search_fields = ('phone_number', 'id_number', 'email')

@admin.register(Matatu)
class MatatuAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'fleet_number', 'sacco', 'vehicle_type', 'current_driver')
    list_filter = ('vehicle_type', 'sacco')
    search_fields = ('plate_number', 'fleet_number')

@admin.register(Sacco)
class SaccoAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'contact_phone')
    search_fields = ('name', 'registration_number')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('matatu', 'route', 'status', 'scheduled_departure')
    list_filter = ('status', 'route')

# Register remaining models with defaults
admin.site.register(Route)
admin.site.register(PassengerTrip)
admin.site.register(Payment)
admin.site.register(Notification)