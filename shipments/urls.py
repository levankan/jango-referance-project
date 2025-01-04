#urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipments, name='shipments'),
    path('packing-list/', views.packing_list, name='packing_list'),
    path('clear-database/', views.clear_database, name='clear_database'),  # Correct URL
    path('packing-list/pdf/<str:pallet_id>/', views.packing_list_pdf, name='packing_list_pdf'),  # New URL to export PDF
    path('save_dimensions/', views.save_dimensions, name='save_dimensions'),
 ]





