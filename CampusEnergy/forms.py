# Portfolio\CEEDS-UACH\ceeds_uach\CampusEnergy\forms.py

from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()
