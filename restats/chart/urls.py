from django.urls import path
from . import views

urlpatterns = [
    path('rental-price-chart/', views.rental_price_chart, name='rental_price_chart'),
]