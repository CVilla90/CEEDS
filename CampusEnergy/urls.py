from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('wipe-data/', views.wipe_data_view, name='wipe_data_view'),
    # Add more paths here as needed
]
