# matwana_app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    MatwanaUser, Sacco, Route, RouteStop, Vehicle, VehicleDocument,
    Trip, Ticket, Payment, ConductorRecord, GPSReport
)

# --- 1. Inline MatwanaUser Profile with Django User ---

class MatwanaUserInline(admin.StackedInline):
    """Allows MatwanaUser profile fields to appear directly on the Django User edit page."""
    model = MatwanaUser
    can_delete = False
    verbose_name_plural = 'Matwana Profile'
    # Display the sacco field and other custom fields
    fieldsets = (
        (None, {'fields': ('role', 'sacco', 'phone', 'id_number')}),
        ('Documents/Media', {'fields': ('profile_photo',)}),
    )
    # Exclude fields like role when creating a superuser for safety
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_superuser:
            return ('role',)
        return ()

class UserAdmin(BaseUserAdmin):
    """Define a new User Admin that includes the MatwanaUser inline profile."""
    inlines = (MatwanaUserInline,)
    
    # Custom display fields for the main list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_sacco')
    
    def get_role(self, obj):
        return obj.matwanauser.role if hasattr(obj, 'matwanauser') else 'N/A'
    get_role.short_description = 'Matwana Role'
    
    def get_sacco(self, obj):
        return obj.matwanauser.sacco.name if hasattr(obj, 'matwanauser') and obj.matwanauser.sacco else 'N/A'
    get_sacco.short_description = 'Sacco Affiliation'


# --- 2. Register Core Models ---

@admin.register(Sacco)
class SaccoAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_no', 'status', 'email', 'phone_number', 'total_vehicles')
    list_filter = ('status',)
    search_fields = ('name', 'registration_no', 'email')
    # Allow staff to easily change the status
    actions = ['make_active', 'make_suspended']

    def make_active(self, request, queryset):
        queryset.update(status='Active')
    make_active.short_description = "Mark selected Saccos as Active"

    def make_suspended(self, request, queryset):
        queryset.update(status='Suspended')
    make_suspended.short_description = "Mark selected Saccos as Suspended"

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name',)
    # inlines = [
    #     # Allows you to add/edit stops directly from the Route page
    #     admin.TabularInline(RouteStop, extra=1)
    # ]

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'sacco', 'route', 'driver', 'conductor', 'capacity', 'active')
    list_filter = ('sacco', 'route', 'active')
    search_fields = ('registration_number', 'sacco__name', 'driver__user__username')
    
# --- 3. Register Transactional/Related Models ---

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'route', 'departure_time', 'is_active', 'passenger_count', 'total_revenue')
    list_filter = ('route', 'is_active')
    date_hierarchy = 'departure_time'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('trip', 'passenger', 'seat_number', 'created_at')
    raw_id_fields = ('trip', 'passenger') # Use raw ID lookup for performance

# Register all other models
admin.site.register(VehicleDocument)
admin.site.register(Payment)
admin.site.register(ConductorRecord)
admin.site.register(GPSReport)

# --- 4. Unregister and Re-register Django User ---

# Unregister the default User model admin
admin.site.unregister(User) 
# Register our customized UserAdmin class
admin.site.register(User, UserAdmin)