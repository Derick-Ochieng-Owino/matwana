from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# keep using your MatwanaUser one-to-one profile
class MatwanaUser(models.Model):
    USER_TYPES = [
        ('passenger', 'Passenger'),
        ('driver', 'Driver'),
        ('conductor', 'Conductor'),
        ('sacco', 'Sacco Admin'),
        ('admin', 'Matwana Admin'),
    ]
    sacco = models.ForeignKey('Sacco', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=30, blank=True, null=True)
    # extra fields
    id_number = models.CharField(max_length=50, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Route(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Sacco(models.Model):
    # Foreign Key to the Sacco Admin User (MatwanaUser with role='sacco')
    admin_user = models.ForeignKey(
        MatwanaUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'role': 'sacco'}, 
        related_name='managed_saccos',
        verbose_name='Sacco Administrator'
    )
    
    name = models.CharField(max_length=150, unique=True)
    registration_no = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Status fields (as seen in your dashboard table)
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending', 'Pending Review'),
        ('Suspended', 'Suspended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def total_vehicles(self):
        return self.vehicles.count()

    def __str__(self):
        return self.name

class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=150)  # e.g., "Ngara"
    order = models.PositiveIntegerField()  # sequence on the route
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('route', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.route.name} — {self.name}"


class Vehicle(models.Model):
    """
    Matatu / vehicle
    """
    sacco = models.ForeignKey('Sacco', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    registration_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150, blank=True)  # optional nickname
    capacity = models.PositiveIntegerField(default=14)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    driver = models.ForeignKey(MatwanaUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='driven_vehicles')
    conductor = models.ForeignKey(MatwanaUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='conducted_vehicles')
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # realtime / snapshot fields (cached)
    current_passenger_count = models.PositiveIntegerField(default=0)
    last_seen = models.DateTimeField(null=True, blank=True)
    last_lat = models.FloatField(null=True, blank=True)
    last_lng = models.FloatField(null=True, blank=True)

    def is_full(self):
        return self.current_passenger_count >= self.capacity

    def __str__(self):
        return f"{self.registration_number} ({self.route.name if self.route else 'Unassigned'})"


class VehicleDocument(models.Model):
    """
    Documents for the vehicle or driver (insurance, logbook, driver's license)
    """
    DOCUMENT_TYPES = [
        ('license', 'Driver License'),
        ('logbook', 'Logbook / Logbook copy'),
        ('insurance', 'Insurance'),
        ('inspection', 'Inspection Certificate'),
        ('other', 'Other')
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    user = models.ForeignKey(MatwanaUser, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    doc_type = models.CharField(max_length=40, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='vehicle_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = self.vehicle.registration_number if self.vehicle else self.user.user.username
        return f"{who} - {self.doc_type}"


class Trip(models.Model):
    """
    A scheduled or ad-hoc trip instance. A 'trip' groups a vehicle on a route at a time.
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)   # trip is ongoing
    created_at = models.DateTimeField(auto_now_add=True)

    def passenger_count(self):
        return self.tickets.count()

    def total_revenue(self):
        return sum([p.amount for p in self.payments.all()])

    def __str__(self):
        return f"{self.vehicle.registration_number} @ {self.departure_time:%Y-%m-%d %H:%M}"


class Ticket(models.Model):
    """
    A passenger on a trip (not strict booking — can be used to track presence/payment)
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='tickets')
    passenger = models.ForeignKey(MatwanaUser, on_delete=models.CASCADE, related_name='tickets')
    seat_number = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'seat_number')  # if seat assignment used

    def __str__(self):
        return f"{self.passenger.user.username} -> {self.trip}"


class Payment(models.Model):
    """
    Payment records (M-Pesa or other). Payment provider metadata stored for reconciliation.
    """
    PAYMENT_STATUS = [
        ('pending','Pending'),
        ('completed','Completed'),
        ('failed','Failed'),
    ]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='payments')
    passenger = models.ForeignKey(MatwanaUser, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=50, default='mpesa')
    provider_reference = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.user.username} paid {self.amount} ({self.status})"


class ConductorRecord(models.Model):
    """
    For conductor to record per-ride payments and totals. Linking to ticket or payment.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='conductor_records')
    conductor = models.ForeignKey(MatwanaUser, on_delete=models.CASCADE, related_name='conductor_records')
    passenger_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.conductor.user.username} - {self.passenger_name} : {self.amount}"


class GPSReport(models.Model):
    """
    Crowd-sourced position reports from passengers (fallback) or driver app reporting.
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='gps_reports', null=True, blank=True)
    reporter = models.ForeignKey(MatwanaUser, on_delete=models.SET_NULL, null=True, blank=True)
    lat = models.FloatField()
    lng = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reporter} @ {self.reported_at}"
