# Portfolio\CEEDS-UACH\ceeds_uach\CampusEnergy\views.py

from django.shortcuts import render, redirect
import csv
from .models import School, EnergyConsumption
from django.core.exceptions import ObjectDoesNotExist
from .forms import CSVUploadForm
from .utils import import_data  # Assume import_data is moved to utils.py
from django.db.models import Sum

# Functions here

def home(request):
    return render(request, 'CampusEnergy/home.html')


def dashboard_view(request):
    year_filter = request.GET.get('year', 'All')
    school_filter = request.GET.get('school', 'All')
    sort_order = request.GET.get('sort', 'year')  # Default sorting by year

    distinct_years = ['All'] + list(EnergyConsumption.objects.order_by('year').values_list('year', flat=True).distinct())
    schools = ['University Total'] + ['All'] + list(School.objects.values_list('name', flat=True))

    # Determine the queryset based on filters
    if year_filter == 'All' and school_filter == 'All':
        # Show all records
        consumption_data = EnergyConsumption.objects.values('year', 'school__name').annotate(total_consumption=Sum('energy_consumed')).order_by(sort_order)
    elif school_filter == 'University Total':
        # Show totals for each year across all schools
        consumption_data = EnergyConsumption.objects.values('year').annotate(total_consumption=Sum('energy_consumed')).order_by(sort_order)
    else:
        # Filter based on year and/or school
        consumption_data = EnergyConsumption.objects
        if year_filter != 'All':
            consumption_data = consumption_data.filter(year=year_filter)
        if school_filter != 'All':
            consumption_data = consumption_data.filter(school__name=school_filter)
        consumption_data = consumption_data.values('year', 'school__name').annotate(total_consumption=Sum('energy_consumed')).order_by(sort_order)

    # Preparing data for the chart
    chart_data = {
        'labels': [],  # Will hold the years
        'data': [],    # Will hold the corresponding total consumption for each year
    }

    total_consumption_by_year = EnergyConsumption.objects.values('year').annotate(total_consumption=Sum('energy_consumed')).order_by('year')
    for entry in total_consumption_by_year:
        chart_data['labels'].append(entry['year'])
        chart_data['data'].append(entry['total_consumption'])


    return render(request, 'CampusEnergy/dashboard.html', {
        'consumption_data': consumption_data,
        'schools': schools,
        'distinct_years': distinct_years,
        'uploaded_file_name': request.session.get('uploaded_file_name', 'No file uploaded'),
        'year_filter': year_filter,
        'school_filter': school_filter, 
        'chart_data': chart_data, 
    })


def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            request.session['uploaded_file_name'] = csv_file.name  # Store the file name in the session
            decoded_file = csv_file.read().decode('utf-8').splitlines()  # Decoding the file
            import_data(decoded_file)  # Adjust this function to handle the decoded file
            return redirect('dashboard_view')  # Redirect to the dashboard view
    else:
        form = CSVUploadForm()
    
    return render(request, 'CampusEnergy/upload_csv.html', {'form': form})


def wipe_data_view(request):
    # Deletes all entries in the EnergyConsumption table
    EnergyConsumption.objects.all().delete()
    # Optionally, clear the filename in the session
    if 'uploaded_file_name' in request.session:
        del request.session['uploaded_file_name']
    return redirect('dashboard_view')
