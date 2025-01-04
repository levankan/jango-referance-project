from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipments, name='shipments'),
    path('packing-list/', views.packing_list, name='packing_list')
 ]
