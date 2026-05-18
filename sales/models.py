from django.db import models
from products.models import Product


class Sale(models.Model):
    invoice_no = models.CharField(max_length=20, unique=True)
    
    # Customer fields (NEW)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Payment method (NEW)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('easypaisa', 'EasyPaisa'),
            ('card', 'Card'),
        ],
        default='cash'
    )
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        customer = self.customer_name if self.customer_name else "Walk-in"
        return f"{self.invoice_no} - {customer}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.sale.invoice_no} - {self.product.name}"



