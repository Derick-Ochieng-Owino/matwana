# models.py
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'super_admin')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = [
        ('passenger', 'Passenger'),
        ('conductor', 'Conductor'),
        ('driver', 'Driver'),
        ('sacco_admin', 'Sacco Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='passenger')
    id_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(r'^\d{8,9}$', 'Kenyan ID number must be 8 or 9 digits')
        ]
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(r'^\+254\d{9}$', 'Phone must be in the format +254XXXXXXXXX')
        ]
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_staff = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'id_number', 'phone_number']
    
    class Meta:
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Sacco(models.Model):
    name = models.CharField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    address = models.TextField()
    logo = models.ImageField(upload_to='sacco_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'sacco_admin'})
    
    def __str__(self):
        return self.name

class Matatu(models.Model):
    VEHICLE_TYPES = [
        ('minibus', 'Minibus (14-Seater)'),
        ('shuttle', 'Shuttle'),
        ('bus', 'Large Bus'),
    ]
    
    plate_number = models.CharField(max_length=20, unique=True)
    fleet_number = models.CharField(max_length=50)
    sacco = models.ForeignKey(Sacco, on_delete=models.CASCADE, related_name='matatus')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='minibus')
    capacity = models.IntegerField()
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    qr_code_data = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    current_driver = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'user_type': 'driver'}, 
        related_name='assigned_matatu_as_driver'  # Added unique related_name
    )
    current_conductor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'user_type': 'conductor'}, 
        related_name='assigned_matatu_as_conductor'  # Added unique related_name
    )
    
    def __str__(self):
        return f"{self.plate_number} - {self.fleet_number}"

class Route(models.Model):
    name = models.CharField(max_length=255)
    start_point = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_duration_minutes = models.IntegerField()
    standard_fare = models.DecimalField(max_digits=6, decimal_places=2)
    sacco = models.ForeignKey(Sacco, on_delete=models.CASCADE, related_name='routes')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['sacco', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.start_point} to {self.end_point})"

class Trip(models.Model):
    TRIP_STATUS = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    matatu = models.ForeignKey(Matatu, on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'user_type': 'driver'},
        related_name='driven_trips'  # Added unique related_name
    )
    conductor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'user_type': 'conductor'},
        related_name='conducted_trips'  # Added unique related_name
    )
    scheduled_departure = models.DateTimeField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    scheduled_arrival = models.DateTimeField()
    actual_arrival = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TRIP_STATUS, default='scheduled')
    current_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.matatu.plate_number} - {self.route.name} ({self.scheduled_departure.date()})"

class PassengerTrip(models.Model):
    PAYMENT_METHODS = [
        ('credits', 'Credits'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips', limit_choices_to={'user_type': 'passenger'})
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='passengers')
    boarding_stop = models.CharField(max_length=255)
    alighting_stop = models.CharField(max_length=255)
    fare_paid = models.DecimalField(max_digits=6, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_reference = models.CharField(max_length=255, blank=True)
    payment_qr_code = models.ImageField(upload_to='payment_qr/', null=True, blank=True)
    credits_earned = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    boarded_at = models.DateTimeField(null=True, blank=True)
    alighted_at = models.DateTimeField(null=True, blank=True)
    transaction_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['passenger', 'trip']
    
    def __str__(self):
        return f"{self.passenger} - {self.trip}"

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('trip', 'Trip Payment'),
        ('credit_topup', 'Credit Top-up'),
        ('refund', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', limit_choices_to={'user_type': 'passenger'})
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.passenger} - {self.amount} - {self.status}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('price_change', 'Price Change'),
        ('system', 'System'),
        ('promotion', 'Promotion'),
        ('trip_update', 'Trip Update'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type__in': ['super_admin', 'sacco_admin']})
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Many-to-many for targeted notifications
    recipients = models.ManyToManyField(User, related_name='notifications', blank=True)
    saccos = models.ManyToManyField(Sacco, blank=True)
    
    def __str__(self):
        return self.title