

from django.contrib import admin
from .models import Category, Brand, Product,Supplier

admin.site.site_header = "Farman Electronics Admin"
admin.site.site_title = "Farman"
admin.site.index_title = "Management Panel"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    # Order newest first
    ordering = ['-id']
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'country', 'created_at']

    search_fields = ['name', 'country']

    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'name',
        'sku',
        'category',
        'brand',
        'selling_price',
        'stock_quantity',
        'low_stock_status',
        'is_active'
    ]
    search_fields = [
        'name',
        'sku',
        'barcode'
    ]
    list_filter = [
        'category',
        'brand',
        'is_active',
        'created_at'
    ]

    # Editable directly in table
    list_editable = [
        'selling_price',
        'stock_quantity',
        'is_active'
    ]
    ordering = ['name']
    list_per_page = 20

    list_select_related = ['category', 'brand']

    def low_stock_status(self, obj):
        if obj.stock_quantity <= obj.reorder_level:
            return "⚠ Low Stock"
        return "✅ OK"

    low_stock_status.short_description = "Stock Status"

# Add this at the bottom
admin.site.register(Supplier)