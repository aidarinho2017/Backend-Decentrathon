from django.contrib import admin

from api.models import Resource, Booking, TimeSlot

# Register your models here.
admin.site.register(Resource)
admin.site.register(Booking)
admin.site.register(TimeSlot)