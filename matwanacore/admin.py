from django.contrib import admin
from .models import MatwanaUser, Route, RouteStop, Vehicle, VehicleDocument, Trip, Ticket, Payment, ConductorRecord, GPSReport

admin.site.register(MatwanaUser)
admin.site.register(Route)
admin.site.register(RouteStop)
admin.site.register(Vehicle)
admin.site.register(VehicleDocument)
admin.site.register(Trip)
admin.site.register(Ticket)
admin.site.register(Payment)
admin.site.register(ConductorRecord)
admin.site.register(GPSReport)
