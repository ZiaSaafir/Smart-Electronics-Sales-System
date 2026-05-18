from django.urls import path
from . import views

urlpatterns=[
    path('',views.low_stock_report,name='low_stock'),
]