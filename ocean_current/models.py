from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    UserID = models.AutoField(primary_key=True)
    Username = models.CharField(max_length=100)
    Password = models.CharField(max_length=100)
    Identity = models.CharField(max_length=100)
    Name = models.CharField(max_length=100)
    Gender = models.CharField(max_length=10)
    IDCard = models.CharField(max_length=20)
    PhoneNumber = models.CharField(max_length=20)
    Email = models.EmailField()

class OceanCurrentData(models.Model):
    CurrentID = models.AutoField(primary_key=True)
    station = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    visibility = models.FloatField()
    air_temperature = models.FloatField()
    wind_direction = models.FloatField()
    wind_speed = models.FloatField()
    air_pressure = models.FloatField()
    sea_temperature = models.FloatField()
    wind_wave_height = models.FloatField()
    wind_wave_period = models.FloatField()

    def __str__(self):
        return f"{self.station} - {self.date} {self.time}"