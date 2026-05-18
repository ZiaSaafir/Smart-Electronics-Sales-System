from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import json

from products.models import Product, Supplier, Category, Brand
from .models import Purchase, PurchaseItem


def purchase_list(request):
    """Show all purchase orders"""
    purchases = Purchase.objects.all().order_by('-created_at')
    return render(request, 'purchase/list.html', {'purchases': purchases})


def add_purchase(request):
    """Form to add new purchase"""
    products = Product.objects.filter(is_active=True)
    suppliers = Supplier.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'suppliers': suppliers,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'purchase/add.html', context)


def create_product(request):
    """Create a new product (AJAX)"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
    
    try:
        data = json.loads(request.body)
        
        # Create new product
        product = Product.objects.create(
            name=data.get('name'),
            sku=data.get('sku'),
            category_id=data.get('category_id') if data.get('category_id') else None,
            brand_id=data.get('brand_id') if data.get('brand_id') else None,
            cost_price=Decimal(str(data.get('cost_price', 0))),
            selling_price=Decimal(str(data.get('selling_price', 0))),
            stock_quantity=0,  # Will be increased by purchase
            reorder_level=data.get('reorder_level', 5),
            is_active=True
        )
        
        return JsonResponse({
            "success": True,
            "product_id": product.id,
            "message": "Product created successfully"
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


def save_purchase(request):
    """Save purchase and increase stock"""
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request"}, status=400)
    
    try:
        data = json.loads(request.body)
        cart = data.get('cart', [])
        supplier_data = data.get('supplier')
        
        if not cart:
            return JsonResponse({"message": "Cart is empty"}, status=400)
        
        with transaction.atomic():
            # Create or get supplier
            supplier = None
            if supplier_data:
                if supplier_data.get('is_new'):
                    # Create new supplier
                    supplier = Supplier.objects.create(
                        name=supplier_data.get('name'),
                        phone=supplier_data.get('phone', ''),
                        address=supplier_data.get('address', '')
                    )
                elif supplier_data.get('id'):
                    try:
                        supplier = Supplier.objects.get(id=supplier_data.get('id'))
                    except Supplier.DoesNotExist:
                        pass
            
            # Generate purchase invoice number
            last_purchase = Purchase.objects.order_by('-id').first()
            next_id = last_purchase.id + 1 if last_purchase else 1
            invoice_no = "PUR-" + str(next_id).zfill(4)
            
            # Create purchase
            purchase = Purchase.objects.create(
                invoice_no=invoice_no,
                supplier=supplier,
                total_amount=0
            )
            
            total_amount = Decimal('0.00')
            
            for item in cart:
                product = Product.objects.get(id=item['id'])
                qty = int(item['qty'])
                cost_price = Decimal(str(item['price']))
                line_total = cost_price * qty
                total_amount += line_total
                
                # Save purchase item
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=qty,
                    cost_price=cost_price,
                    line_total=line_total
                )
                
                # INCREASE stock
                product.stock_quantity += qty
                product.cost_price = cost_price  # Update cost price to latest purchase price
                product.save()
            
            purchase.total_amount = total_amount
            purchase.save()
            
            return JsonResponse({
                "message": f"Purchase Complete - {invoice_no}",
                "purchase_id": purchase.id
            })
            
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)