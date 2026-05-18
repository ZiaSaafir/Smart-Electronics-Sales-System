from django.contrib import admin
from .models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    """Display purchase items inline within purchase form"""
    model = PurchaseItem
    extra = 1
    fields = ['product', 'quantity', 'cost_price', 'line_total']
    readonly_fields = ['line_total']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin configuration for Purchase model"""
    list_display = ['invoice_no', 'supplier', 'total_amount', 'created_at']
    list_filter = ['created_at', 'supplier']
    search_fields = ['invoice_no', 'supplier__name']
    readonly_fields = ['created_at']
    inlines = [PurchaseItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 25


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    """Admin configuration for PurchaseItem model"""
    list_display = ['purchase', 'product', 'quantity', 'cost_price', 'line_total']
    list_filter = ['purchase__supplier']
    search_fields = ['product__name', 'purchase__invoice_no']
    readonly_fields = ['line_total']
    list_per_page = 25