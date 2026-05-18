from django.contrib import admin
from .models import Category, Brand, Product, Supplier

# Admin Site Customization
admin.site.site_header = "Farman Electronics Admin"
admin.site.site_title = "Farman"
admin.site.index_title = "Management Panel"


# ============================================================
# CATEGORY ADMIN
# ============================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'created_at']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['-id']
    list_per_page = 25


# ============================================================
# BRAND ADMIN
# ============================================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'country', 'created_at']
    list_display_links = ['name']
    search_fields = ['name', 'country']
    ordering = ['name']
    list_per_page = 25


# ============================================================
# SUPPLIER ADMIN
# ============================================================
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'address', 'created_at']
    list_display_links = ['name']
    search_fields = ['name', 'phone']
    list_filter = ['created_at']
    ordering = ['name']
    list_per_page = 25


# ============================================================
# PRODUCT ADMIN
# ============================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'sku', 'category', 'brand', 
        'selling_price', 'stock_quantity', 'low_stock_status', 'is_active'
    ]
    list_display_links = ['name']
    list_filter = ['category', 'brand', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'barcode']
    list_editable = ['selling_price', 'stock_quantity', 'is_active']
    ordering = ['name']
    list_per_page = 25
    list_select_related = ['category', 'brand']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'barcode', 'category', 'brand')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price'),
            'classes': ('wide',)
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'reorder_level')
        }),
        ('Status', {
            'fields': ('is_active', 'image')
        }),
    )
    
    def low_stock_status(self, obj):
        """Display stock status with warning"""
        if obj.stock_quantity <= obj.reorder_level:
            return "⚠️ Low Stock"
        return "✅ OK"
    
    low_stock_status.short_description = "Stock Status"