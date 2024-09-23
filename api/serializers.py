from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Resource, Booking, TimeSlot


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name']

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'resource', 'start_time', 'end_time', 'date', 'max_people']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'time_slot', 'date', 'status', 'queue_position']