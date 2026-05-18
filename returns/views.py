from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json

from sales.models import Sale, SaleItem
from products.models import Product
from .models import ReturnRecord, ReturnItem


@staff_member_required
def return_list(request):
    """List all returns"""
    returns = ReturnRecord.objects.all().order_by('-return_date')
    return render(request, 'returns/list.html', {'returns': returns})


@staff_member_required
def create_return(request, sale_id):
    """Create return for a sale"""
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Get sold items (non-zero price)
    sold_items = sale.items.filter(price__gt=0)
    
    context = {
        'sale': sale,
        'sold_items': sold_items,
    }
    return render(request, 'returns/create.html', context)


@staff_member_required
@transaction.atomic
def save_return(request):
    """Save return and process stock updates"""
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request"}, status=400)
    
    try:
        data = json.loads(request.body)
        sale_id = data.get('sale_id')
        return_type = data.get('return_type', 'refund')
        reason = data.get('reason', '')
        items = data.get('items', [])
        
        if not items:
            return JsonResponse({"message": "No items selected"}, status=400)
        
        sale = Sale.objects.get(id=sale_id)
        
        # Generate return number
        last_return = ReturnRecord.objects.order_by('-id').first()
        next_id = last_return.id + 1 if last_return else 1
        return_no = f"RET-{str(next_id).zfill(4)}"
        
        # Calculate total refund
        total_refund = Decimal('0.00')
        
        # Create return record
        return_record = ReturnRecord.objects.create(
            return_no=return_no,
            original_sale=sale,
            return_type=return_type,
            customer_name=sale.customer_name,
            customer_phone=sale.customer_phone,
            reason=reason,
            refund_amount=0,
            status='approved',
            approved_by=request.user.username,
            approved_date=timezone.now()
        )
        
        # Process each returned item
        for item in items:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            refund_price = Decimal(str(item.get('refund_price', 0)))
            
            if quantity <= 0:
                continue
            
            product = Product.objects.get(id=product_id)
            line_total = refund_price * quantity
            total_refund += line_total
            
            # Create return item
            ReturnItem.objects.create(
                return_record=return_record,
                product=product,
                quantity=quantity,
                refund_price=refund_price,
                line_total=line_total,
                reason_detail=item.get('reason', '')
            )
            
            # INCREASE stock (product is being returned)
            product.stock_quantity += quantity
            product.save()
        
        return_record.refund_amount = total_refund
        return_record.save()
        
        return JsonResponse({
            "message": f"Return processed - {return_no}",
            "return_id": return_record.id,
            "refund_amount": float(total_refund)
        })
        
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


@staff_member_required
def return_detail(request, return_id):
    """View return details"""
    return_record = get_object_or_404(ReturnRecord, id=return_id)
    return render(request, 'returns/detail.html', {'return': return_record})


@staff_member_required
def return_invoice(request, return_id):
    """Print return receipt"""
    return_record = get_object_or_404(ReturnRecord, id=return_id)
    return render(request, 'returns/invoice.html', {'return': return_record})