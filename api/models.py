from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HabitTrack(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='tracks')
    count = models.PositiveIntegerField(default=0)
    last_incremented = models.DateTimeField(auto_now=True)

    def increment(self):
        self.count += 1
        self.save()

    def __str__(self):
        return f"{self.habit.name} - {self.count} times"

