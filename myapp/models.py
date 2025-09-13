from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(models.Model):
    name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_conductor = models.BooleanField(default=False)  # 👈 new field

    def __str__(self):
        return f"{self.name} ({'Conductor' if self.is_conductor else 'Passenger'})"



class Journey(models.Model):
    conductor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"is_conductor": True})
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    stop_points = models.TextField(help_text="Comma separated stop names", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.start_location} → {self.end_location} ({self.conductor.name})"


class BusLocation(models.Model):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="locations")
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)