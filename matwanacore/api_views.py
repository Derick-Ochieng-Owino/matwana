from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Route, Vehicle, Trip, Ticket, Payment, GPSReport
from .serializers import RouteSerializer, VehicleSerializer, TripSerializer, TicketSerializer, PaymentSerializer, GPSReportSerializer
from django.utils import timezone

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.filter(active=True)
    serializer_class = RouteSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['get'])
    def vehicles(self, request, pk=None):
        route = get_object_or_404(Route, pk=pk)
        vehicles = route.vehicles.filter(active=True)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        vehicle = get_object_or_404(Vehicle, pk=pk)
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        passenger_count = request.data.get('passenger_count')
        if lat is not None and lng is not None:
            vehicle.last_lat = lat
            vehicle.last_lng = lng
            vehicle.last_seen = timezone.now()
        if passenger_count is not None:
            try:
                vehicle.current_passenger_count = int(passenger_count)
            except:
                pass
        vehicle.save()
        # optionally broadcast via channels
        return Response({'status':'ok'})

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class GPSReportViewSet(viewsets.ModelViewSet):
    queryset = GPSReport.objects.all()
    serializer_class = GPSReportSerializer
