from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Habit, HabitTrack


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'description', 'created_at']

class HabitTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTrack
        fields = ['id', 'habit', 'count', 'last_incremented']