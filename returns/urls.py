from django.urls import path
from . import views

urlpatterns = [
    path('', views.return_list, name='return_list'),
    path('create/<int:sale_id>/', views.create_return, name='create_return'),
    path('save/', views.save_return, name='save_return'),
    path('<int:return_id>/', views.return_detail, name='return_detail'),
    path('invoice/<int:return_id>/', views.return_invoice, name='return_invoice'),
]