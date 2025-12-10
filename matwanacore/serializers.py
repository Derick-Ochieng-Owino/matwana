from rest_framework import serializers
from .models import Route, RouteStop, Vehicle, Trip, Ticket, Payment, GPSReport

class RouteStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStop
        fields = ('id','name','order','lat','lng')

class RouteSerializer(serializers.ModelSerializer):
    stops = RouteStopSerializer(many=True, read_only=True)
    class Meta:
        model = Route
        fields = ('id','name','description','stops')

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id','registration_number','name','capacity','route_id','driver_id','conductor_id','last_lat','last_lng','current_passenger_count','is_full')
    is_full = serializers.SerializerMethodField()
    def get_is_full(self, obj):
        return obj.current_passenger_count >= obj.capacity

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class GPSReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSReport
        fields = '__all__'
