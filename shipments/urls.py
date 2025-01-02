from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipments, name='shipments'),
]
