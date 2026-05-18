from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product, Category, Brand

@staff_member_required
def product_list(request):
    """Custom product management page that extends base.html"""
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'total_products': products.count(),
    }
    return render(request, 'products/list.html', context)