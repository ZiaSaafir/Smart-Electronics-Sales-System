from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import json

from products.models import Product, Supplier
from .models import Purchase, PurchaseItem


def purchase_list(request):
    """Show all purchase orders"""
    purchases = Purchase.objects.all().order_by('-created_at')
    return render(request, 'purchase/list.html', {'purchases': purchases})


def add_purchase(request):
    """Form to add new purchase"""
    products = Product.objects.filter(is_active=True)
    suppliers = Supplier.objects.all()
    
    context = {
        'products': products,
        'suppliers': suppliers,
    }
    return render(request, 'purchase/add.html', context)


def save_purchase(request):
    """Save purchase and increase stock"""
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request"}, status=400)
    
    try:
        data = json.loads(request.body)
        cart = data.get('cart', [])
        supplier_id = data.get('supplier_id')
        
        if not cart:
            return JsonResponse({"message": "Cart is empty"}, status=400)
        
        with transaction.atomic():
            # Generate purchase invoice number
            last_purchase = Purchase.objects.order_by('-id').first()
            next_id = last_purchase.id + 1 if last_purchase else 1
            invoice_no = "PUR-" + str(next_id).zfill(4)
            
            # Get supplier
            supplier = None
            if supplier_id:
                try:
                    supplier = Supplier.objects.get(id=supplier_id)
                except Supplier.DoesNotExist:
                    pass
            
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
                product.cost_price = cost_price  # Update cost price
                product.save()
            
            purchase.total_amount = total_amount
            purchase.save()
            
            return JsonResponse({
                "message": f"Purchase Complete - {invoice_no}",
                "purchase_id": purchase.id
            })
            
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)