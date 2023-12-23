# Portfolio\CEEDS-UACH\ceeds_uach\CampusEnergy\views.py

from django.shortcuts import render, redirect
import csv
from .models import School, EnergyConsumption
from django.core.exceptions import ObjectDoesNotExist
from .forms import CSVUploadForm
from .utils import import_data  # Assume import_data is moved to utils.py
from django.db.models import Sum, Avg, Min, Max
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

# Functions here

def home(request):
    return render(request, 'CampusEnergy/home.html')


def dashboard_view(request):
    # Existing filter captures
    year_filter = request.GET.get('year', 'All')
    school_filter = request.GET.get('school', 'All')
    sort_order = request.GET.get('sort', 'year')  # Default sorting by year
    # Capture the chart type
    chart_type = request.GET.get('chart_type', 'bar')  # Default to 'bar' if not specified

    # Capture and validate the sort order
    sort_order = request.GET.get('sort', 'year')  # Default sorting by year
    valid_sort_fields = {'year', '-year', 'school__name', '-school__name', 'total_consumption', '-total_consumption'}
    if sort_order not in valid_sort_fields:
        sort_order = 'year'  # Default to year if sort_order is invalid

    distinct_years = ['All'] + list(EnergyConsumption.objects.order_by('year').values_list('year', flat=True).distinct())
    schools = ['All', 'University Total'] + list(School.objects.values_list('name', flat=True))

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
        'labels': [],  # Will hold the years or school names based on the filter
        'data': [],    # Will hold the corresponding total consumption
    }

    # Adjust the chart data based on the filters
    if year_filter == 'All' and school_filter == 'All':
        # Total consumption by year for all schools
        chart_data_query = EnergyConsumption.objects.values('year').annotate(total_consumption=Sum('energy_consumed')).order_by('year')
    elif school_filter == 'University Total':
        # Total consumption by year across all schools
        chart_data_query = EnergyConsumption.objects.values('year').annotate(total_consumption=Sum('energy_consumed')).order_by('year')
    else:
        # Filter based on year and/or school
        chart_data_query = EnergyConsumption.objects
        if year_filter != 'All':
            chart_data_query = chart_data_query.filter(year=year_filter)
        if school_filter != 'All':
            chart_data_query = chart_data_query.filter(school__name=school_filter)
        chart_data_query = chart_data_query.values('year', 'school__name').annotate(total_consumption=Sum('energy_consumed')).order_by('year')

    for entry in chart_data_query:
        if school_filter == 'University Total':
            label = entry['year']
        else:
            label = entry['year'] if year_filter == 'All' else entry['school__name']
        chart_data['labels'].append(label)
        chart_data['data'].append(entry['total_consumption'])

# Commented out because the host (REPLIT) can't deal with scikit-learn library 

    # Initialize prediction result variable

    #prediction_result = None
    #data_view_active = True
    #prediction_view_active = False

    #if 'predict_year' in request.GET and 'predict_school' in request.GET:
        #predict_year = int(request.GET.get('predict_year'))
        #predict_school = request.GET.get('predict_school')
        #data_view_active = False
        #prediction_view_active = True

        #if predict_school == 'University Total':

            # Fetch historical data for the entire university (all schools)

            #historical_data = EnergyConsumption.objects \
                                #.values('year') \
                                #.annotate(total_energy_consumed=Sum('energy_consumed'))

            # Debug: Print the query and its count

            #print("Query:", historical_data.query)
            #print("Data Count:", historical_data.count())

            #if not historical_data:
                #prediction_result = "No historical data found."
            #else:
                #df = pd.DataFrame(list(historical_data))
                #print("Historical data:", df)

                #if len(df) > 1:
                    #model = LinearRegression()
                    #model.fit(df[['year']], df['total_energy_consumed'])
                    #prediction_result = model.predict([[predict_year]])[0]
                #else:
                    #prediction_result = "Not enough data for prediction."
        #else:
            #prediction_result = "Prediction available for University Total only."

# End of commented out section, and beggning of machine learning section but now using numpy:

    # Initialize prediction result variable
    prediction_result = None
    data_view_active = True
    prediction_view_active = False

    if 'predict_year' in request.GET and 'predict_school' in request.GET:
        predict_year = int(request.GET.get('predict_year'))
        predict_school = request.GET.get('predict_school')
        data_view_active = False
        prediction_view_active = True

        if predict_school == 'University Total':
            # Fetch historical data for the entire university (all schools)
            historical_data = EnergyConsumption.objects \
                                .values('year') \
                                .annotate(total_energy_consumed=Sum('energy_consumed'))

            if not historical_data:
                prediction_result = "No historical data found."
            else:
                df = pd.DataFrame(list(historical_data))

                if len(df) > 1:
                    # Convert year and total_energy_consumed to numpy arrays
                    X = df['year'].values
                    Y = df['total_energy_consumed'].values

                    # Mean of X and Y
                    mean_x = np.mean(X)
                    mean_y = np.mean(Y)

                    # Total number of values
                    n = len(X)

                    # Using the formula to calculate 'm' and 'c'
                    numer = 0
                    denom = 0
                    for i in range(n):
                        numer += (X[i] - mean_x) * (Y[i] - mean_y)
                        denom += (X[i] - mean_x) ** 2
                    m = numer / denom
                    c = mean_y - (m * mean_x)

                    # Making predictions
                    prediction_result = m * predict_year + c
                else:
                    prediction_result = "Not enough data for prediction."
        else:
            prediction_result = "Prediction available for University Total only."

    return render(request, 'CampusEnergy/dashboard.html', {
        'consumption_data': consumption_data,
        'schools': schools,
        'distinct_years': distinct_years,
        'uploaded_file_name': request.session.get('uploaded_file_name', 'No file uploaded'),
        'year_filter': year_filter,
        'school_filter': school_filter, 
        'chart_data': chart_data,
        'chart_type': chart_type,  
        'prediction_result': prediction_result,
        'predict_year': predict_year if 'predict_year' in request.GET else None,
        'data_view_active': data_view_active,
        'prediction_view_active': prediction_view_active,
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
