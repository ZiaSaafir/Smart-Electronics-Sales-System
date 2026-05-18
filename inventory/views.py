from django.shortcuts import render
from django.db import models
from products.models import Product


def low_stock_report(request):
    """Show products that need reordering"""
    
    # Find products with stock <= reorder level
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=models.F('reorder_level'),
        is_active=True
    ).order_by('stock_quantity')
    
    # Count critical (zero stock)
    critical_count = low_stock_products.filter(stock_quantity=0).count()
    
    # Count low warning (1 to reorder level)
    low_warning_count = low_stock_products.filter(stock_quantity__gt=0).count()
    
    # Total active products
    total_products = Product.objects.filter(is_active=True).count()
    
    context = {
        'products': low_stock_products,
        'count': low_stock_products.count(),
        'critical_count': critical_count,
        'low_warning_count': low_warning_count,
        'total_products': total_products,
    }
    
    return render(request, 'inventory/low_stock.html', context)


import datetime
import subprocess
import os
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def simple_backup(request):
    # Database credentials
    db_name = 'farman_pos_db'
    db_user = 'root'
    db_password = '12345'  # Change to your password
    
    # Create filename with date
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backups/backup_{timestamp}.sql'
    
    # Create backups folder
    os.makedirs('backups', exist_ok=True)
    
    # Create backup
    cmd = f'mysqldump -u {db_user} -p{db_password} {db_name} > {backup_file}'
    subprocess.run(cmd, shell=True)
    
    return HttpResponse(f"""
    <html>
    <head><title>Backup Complete</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h2>✅ Backup Complete!</h2>
        <p>File: {backup_file}</p>
        <p>Size: {os.path.getsize(backup_file) / 1024:.2f} KB</p>
        <a href="/dashboard/">Back to Dashboard</a>
    </body>
    </html>
    """)