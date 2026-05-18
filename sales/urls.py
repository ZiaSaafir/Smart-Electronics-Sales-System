from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos_page, name='pos_page'),
    path('checkout/', views.checkout_sale, name='checkout_sale'),
    path('invoice/<int:sale_id>/', views.invoice_page, name='invoice_page'),
    path('history/', views.sales_history, name='sales_history'),
    path('detail/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('whatsapp-message/<int:sale_id>/', views.get_whatsapp_message, name='whatsapp_message'),
]