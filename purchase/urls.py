from django.urls import path
from . import views

urlpatterns = [
    path('', views.purchase_list, name='purchase_list'),
    path('add/', views.add_purchase, name='add_purchase'),
    path('save/', views.save_purchase, name='save_purchase'),
]