# Portfolio\CEEDS-UACH\ceeds_uach\CampusEnergy\utils.py

import csv
from django.core.exceptions import ObjectDoesNotExist
from .models import School, EnergyConsumption

def import_data(file):
    # Decode file if necessary (file.read().decode('utf-8').splitlines()), depending on how the file is uploaded
    reader = csv.DictReader(file)
    for row in reader:
        school_name = row['School']
        month = row['Month']
        year = int(row['Year'])
        energy_consumed = float(row['Consumo_Energético'])  # Assuming data is in GWh

        # Convert the Spanish month abbreviations to numbers
        spanish_months = {
            'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
        }
        month_number = spanish_months.get(month.capitalize(), 0)

        try:
            school = School.objects.get(name=school_name)
        except ObjectDoesNotExist:
            print(f"School not found: {school_name}")
            continue

        # Assuming 'energy_cost' column exists in your CSV
        energy_cost = float(row['EnergyCost']) if 'EnergyCost' in row else 0.0

        EnergyConsumption.objects.create(
            school=school,
            month=month_number,
            year=year,
            energy_consumed=energy_consumed,
            energy_cost=energy_cost
        )

        print(f"Imported data for {school_name} - {month}/{year}")
