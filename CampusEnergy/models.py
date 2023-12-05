from django.db import models

# Create your views here.

class School(models.Model):
    name = models.CharField(max_length=100)
    # Add other fields as necessary

    def __str__(self):
        return self.name

class EnergyConsumption(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    month = models.IntegerField()  # 1 to 12 for January to December
    year = models.IntegerField()
    energy_consumed = models.FloatField()  # e.g., in kWh
    energy_cost = models.FloatField()  # e.g., in USD

    def __str__(self):
        return f"{self.school.name} - {self.month}/{self.year}"

class RenewableEnergyModel(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=100)  # e.g., 'Solar', 'Wind'
    capacity = models.FloatField()  # e.g., in kW
    installation_date = models.DateField()

    def __str__(self):
        return f"{self.school.name} - {self.source_type}"