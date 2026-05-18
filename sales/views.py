from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
import json
from django.db import transaction
from products.models import Product, Category
from .models import Sale, SaleItem
from accounts.decorators import cashier_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum


# ==================================
# POS PAGE
# ==================================
@cashier_required
def pos_page(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'sales/pos.html', context)


# ==================================
# CHECKOUT SALE
# ==================================
@cashier_required
def checkout_sale(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        cart = data.get('cart', [])
        
        customer_name = data.get('customer_name', '')
        customer_phone = data.get('customer_phone', '')
        payment_method = data.get('payment_method', 'cash')

        if not cart:
            return JsonResponse({"message": "Cart is empty"}, status=400)

        with transaction.atomic():
            last_sale = Sale.objects.order_by('-id').first()
            next_id = last_sale.id + 1 if last_sale else 1
            invoice_no = "INV-" + str(next_id).zfill(4)

            sale = Sale.objects.create(
                invoice_no=invoice_no,
                total_amount=0,
                customer_name=customer_name,
                customer_phone=customer_phone,
                payment_method=payment_method
            )

            grand_total = Decimal("0.00")

            for item in cart:
                product = Product.objects.get(id=item['id'])
                qty = int(item['qty'])

                if qty < 1:
                    return JsonResponse({"message": "Invalid quantity"}, status=400)

                if qty > product.stock_quantity:
                    return JsonResponse({
                        "message": f"Not enough stock for {product.name}"
                    }, status=400)

                price = Decimal(str(item['price']))
                line_total = price * qty
                grand_total += line_total

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=price,
                    line_total=line_total
                )

                product.stock_quantity -= qty
                product.save()

            sale.total_amount = grand_total
            sale.save()

            return JsonResponse({
                "message": f"Sale Complete - {invoice_no}",
                "sale_id": sale.id
            })

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


# ==================================
# INVOICE PAGE
# ==================================
def invoice_page(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    context = {'sale': sale}
    return render(request, 'sales/invoice.html', context)


# ==================================
# SALES HISTORY PAGE (ADD THIS)
# ==================================
@staff_member_required
def sales_history(request):
    """Custom sales history page with search, filters"""
    sales = Sale.objects.all().order_by('-id')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        sales = sales.filter(
            Q(invoice_no__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )
    
    # Filter by payment method
    payment_filter = request.GET.get('payment', '')
    if payment_filter:
        sales = sales.filter(payment_method=payment_filter)
    
    # Filter by date range
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    
    if from_date:
        sales = sales.filter(created_at__date__gte=from_date)
    if to_date:
        sales = sales.filter(created_at__date__lte=to_date)
    
    # Summary statistics
    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_invoices = sales.count()
    avg_sale = total_sales / total_invoices if total_invoices > 0 else 0
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_invoices': total_invoices,
        'avg_sale': avg_sale,
        'search_query': search_query,
        'payment_filter': payment_filter,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'sales/history.html', context)


# ==================================
# SALE DETAIL PAGE (ADD THIS)
# ==================================
@staff_member_required
def sale_detail(request, sale_id):
    """View detailed information about a specific sale"""
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'sales/detail.html', {'sale': sale})



from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_whatsapp_message(request, sale_id):
    """Return WhatsApp message for invoice"""
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Build message
    message = "🏪 FARMAN ELECTRONICS\n"
    message += "=" * 28 + "\n"
    message += f"Invoice: {sale.invoice_no}\n"
    message += f"Date: {sale.created_at.strftime('%d/%m/%Y %I:%M %p')}\n"
    message += f"Customer: {sale.customer_name or 'Walk-in'}\n"
    message += f"Payment: {sale.get_payment_method_display()}\n"
    message += "=" * 28 + "\n"
    message += "ITEMS PURCHASED:\n"
    
    # Add items
    for item in sale.items.all():
        message += f"\n{item.product.name}\n"
        message += f"   Qty: {item.quantity} x Rs {int(item.price)} = Rs {int(item.line_total)}"
    
    message += "\n" + "=" * 28 + "\n"
    message += f"TOTAL AMOUNT: Rs {int(sale.total_amount)}\n"
    message += "=" * 28 + "\n"
    message += "Thank you for shopping!\n"
    message += "Farman Electronics - Karkhano Market"
    
    return JsonResponse({'message': message})