from django.db import models


class Category(models.Model):
    # Example: Fans, Lights, Kitchen Appliances
    name = models.CharField(max_length=100, unique=True)

    # Optional details
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    # Example: Dawlance, PEL, GFC
    name = models.CharField(max_length=100, unique=True)

    # Example: Pakistan, China, Japan
    country = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    # Full product name
    name = models.CharField(max_length=200)

    # Unique internal code
    sku = models.CharField(max_length=50, unique=True)

    # Barcode for scanner future use
    barcode = models.CharField(max_length=100, blank=True, null=True)

    # If category deleted, keep product
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    # If brand deleted, keep product
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True
    )

    # Purchase cost
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Sale price
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Available quantity
    stock_quantity = models.PositiveIntegerField(default=0)

    # Low stock alert level
    reorder_level = models.PositiveIntegerField(default=2)

    # Product image
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Hide old products without deleting
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    """Wholesaler/Supplier information"""
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name