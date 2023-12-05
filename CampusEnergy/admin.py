from django.contrib import admin
from .models import School, EnergyConsumption

# Register your models here.

admin.site.register(School)
admin.site.register(EnergyConsumption)
