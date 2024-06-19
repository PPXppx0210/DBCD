from django.contrib import admin
from .models import User
from .models import OceanCurrentData

admin.site.register(User)

@admin.register(OceanCurrentData)
class OceanCurrentDataAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'time', 'latitude', 'longitude', 'visibility', 'air_temperature', 'wind_direction', 'wind_speed', 'air_pressure', 'sea_temperature', 'wind_wave_height', 'wind_wave_period')
    search_fields = ('station', 'date', 'time')
