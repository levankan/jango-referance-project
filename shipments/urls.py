#urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipments, name='shipments'),
    path('packing-list/', views.packing_list, name='packing_list'),
    path('clear-database/', views.clear_database, name='clear_database'),  # Correct URL
 ]
