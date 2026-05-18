from django.db import models
from django.core.validators import MinValueValidator
from sales.models import Sale, SaleItem
from products.models import Product


class ReturnRecord(models.Model):
    """Records product returns and exchanges"""
    
    RETURN_TYPES = [
        ('refund', 'Refund Only'),
        ('exchange', 'Exchange Product'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    # Return information
    return_no = models.CharField(max_length=20, unique=True)
    original_sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='returns')
    return_type = models.CharField(max_length=20, choices=RETURN_TYPES, default='refund')
    
    # Customer information
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Return details
    reason = models.TextField()
    return_date = models.DateTimeField(auto_now_add=True)
    
    # Financial
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Exchange information (if exchange)
    exchange_sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='exchange_from')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.return_no} - {self.original_sale.invoice_no}"
    
    class Meta:
        ordering = ['-return_date']


class ReturnItem(models.Model):
    """Individual items being returned"""
    
    return_record = models.ForeignKey(ReturnRecord, on_delete=models.CASCADE, related_name='items')
    original_sale_item = models.ForeignKey(SaleItem, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    refund_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    reason_detail = models.CharField(max_length=200, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.refund_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"