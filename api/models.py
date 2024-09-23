from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Resource(models.Model):
    name = models.CharField(max_length=100)
    # Другие поля для ресурса

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()  # Время начала слота (например, 09:00)
    end_time = models.TimeField()    # Время окончания слота (например, 10:00)
    date = models.DateField(default=timezone.now)  # Используем timezone.now для установки текущей даты
    max_people = models.IntegerField()  # Максимальное количество людей на слот

    class Meta:
        unique_together = ['resource', 'start_time', 'end_time', 'date']  # Уникальность слотов по дате и времени

    def __str__(self):
        return f'{self.resource.name} ({self.start_time} - {self.end_time} on {self.date})'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('queued', 'Queued'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Используем timezone.now для установки текущей даты
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
    queue_position = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return f'{self.user.username} - {self.time_slot} ({self.status})'


