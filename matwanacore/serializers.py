from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Route, RouteStop, Vehicle, Trip, Ticket, Payment, GPSReport, 
    Sacco, MatwanaUser, ConductorRecord, VehicleDocument
)

# --- UTILITY SERIALIZERS ---

class RouteStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStop
        fields = ('id', 'name', 'order', 'lat', 'lng')

class RouteSerializer(serializers.ModelSerializer):
    # This ensures that when a Route is fetched, its stops are embedded.
    stops = RouteStopSerializer(many=True, read_only=True) 
    class Meta:
        model = Route
        fields = ('id', 'name', 'description', 'stops')

class SaccoSerializer(serializers.ModelSerializer):
    # The 'total_vehicles' method is exposed as a read-only field
    total_vehicles = serializers.SerializerMethodField()

    class Meta:
        model = Sacco
        # '__all__' is fine here for now, but we'll manually exclude 'admin_user' 
        # in the Admin registration flow in the view layer.
        fields = '__all__'
        read_only_fields = ('created_at', 'status', 'total_vehicles') # Prevent direct setting

class GPSReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSReport
        fields = '__all__'


# --- VEHICLE AND TRIP SERIALIZERS ---

class VehicleSerializer(serializers.ModelSerializer):
    # Foreign key fields for read operations should use primary key related fields
    sacco_id = serializers.PrimaryKeyRelatedField(queryset=Sacco.objects.all(), source='sacco')
    route_id = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), source='route')
    driver_id = serializers.PrimaryKeyRelatedField(queryset=MatwanaUser.objects.filter(role='driver'), source='driver')
    conductor_id = serializers.PrimaryKeyRelatedField(queryset=MatwanaUser.objects.filter(role='conductor'), source='conductor')
    
    # Custom method to check vehicle status
    is_full = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        # Include custom fields and exclude Foreign Key objects to use simple IDs
        fields = (
            'id', 'registration_number', 'name', 'capacity', 'sacco_id', 
            'route_id', 'driver_id', 'conductor_id', 'active', 'image',
            'last_lat', 'last_lng', 'current_passenger_count', 'is_full'
        )
        read_only_fields = ('is_full',)

    def get_is_full(self, obj):
        return obj.is_full() # Use the method defined in the model


class TripSerializer(serializers.ModelSerializer):
    # Expose the revenue and passenger count model methods
    passenger_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = Trip
        fields = '__all__'
        
    def get_passenger_count(self, obj):
        return obj.passenger_count()

    def get_total_revenue(self, obj):
        return obj.total_revenue()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        
class ConductorRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConductorRecord
        fields = '__all__'


# --- USER MANAGEMENT SERIALIZERS (For Admin Dashboard Forms) ---

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Base serializer for creating a new Django User object.
    Used internally for Driver/Conductor registration.
    """
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
        # We don't expose 'username' here; we'll generate it in the view (e.g., from email/ID).

class DriverConductorRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer used by the Admin panel to create a new MatwanaUser profile 
    and the corresponding Django User (Driver or Conductor).
    """
    # Fields that belong to the related Django User model
    user_details = UserRegistrationSerializer(write_only=True)
    license_number = serializers.CharField(max_length=50, write_only=True)
    license_expiry = serializers.DateField(write_only=True)
    
    # Field corresponding to the HTML form's Assigned Matatu (Vehicle) selection
    assigned_matatu_reg = serializers.CharField(max_length=50, required=False, allow_blank=True, write_only=True) 

    # Fields that belong to the MatwanaUser model
    class Meta:
        model = MatwanaUser
        # We need data from the form that maps to MatwanaUser fields:
        fields = [
            'user_details', 'sacco', 'phone', 'id_number', 
            'license_number', 'license_expiry', 'assigned_matatu_reg'
        ]
        read_only_fields = ['role'] # The role is set in the view logic

    def create(self, validated_data):
        user_data = validated_data.pop('user_details')
        license_number = validated_data.pop('license_number')
        license_expiry = validated_data.pop('license_expiry')
        assigned_matatu_reg = validated_data.pop('assigned_matatu_reg', None)
        
        # 1. Create the Django User (using National ID as a base for username)
        username_base = f"{user_data['first_name']}.{validated_data['id_number']}"
        django_user = User.objects.create_user(
            username=username_base,
            email=user_data.get('email', f"{username_base}@matwana.com"),
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
        )

        # 2. Create the MatwanaUser profile
        matwana_user = MatwanaUser.objects.create(
            user=django_user, 
            role=self.context.get('role'), # Role injected by the view (driver/conductor)
            **validated_data
        )

        # 3. Create the Vehicle Document (Driver License)
        VehicleDocument.objects.create(
            user=matwana_user,
            doc_type='license',
            file=None, # Assuming file upload is a separate process or handled differently
            # In a real app, file would be uploaded and saved here.
        )
        
        # 4. Handle Matatu Assignment (Optional and requires additional logic in a real view)
        # We'll skip the actual Vehicle update here for simplicity, 
        # but the view would handle linking the matwana_user to the Vehicle model.

        return matwana_user

# Specialized serializer for Drivers (Inherits from base to customize later if needed)
class AdminDriverRegistrationSerializer(DriverConductorRegistrationSerializer):
    pass

# Specialized serializer for Conductors
class AdminConductorRegistrationSerializer(DriverConductorRegistrationSerializer):
    pass