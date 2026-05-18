"""
Dashboard Views for Farman Electronics POS System
==================================================
Handles all dashboard analytics and backup operations.
NOTE: Only backup creation and download - no restore functionality
to prevent accidental data loss.
"""

from django.shortcuts import render
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from datetime import datetime, timedelta
import pytz
import os
import subprocess
import glob

from products.models import Product
from sales.models import Sale, SaleItem


# ============================================================
# MAIN DASHBOARD VIEW
# ============================================================
def dashboard_home(request):
    """
    Main dashboard showing:
    - Today's sales, profit, and invoice count
    - Monthly profit calculation
    - Low stock alerts
    - Top selling products
    - Sales chart for last 7 days
    - Recent transactions
    """
    
    # Timezone Handling
    # Set Pakistan timezone for accurate date filtering
    pakistan_tz = pytz.timezone('Asia/Karachi')
    now_pakistan = timezone.now().astimezone(pakistan_tz)
    today_pakistan = now_pakistan.date()

    # Optimized Queries
    # Use select_related and prefetch_related to reduce database queries
    all_sales = Sale.objects.select_related().prefetch_related('items__product').order_by('-created_at')

    # Today's Data
    today_sales_list = []
    today_sales_total = 0
    today_profit = 0

    for sale in all_sales:
        # Convert UTC to Pakistan timezone for accurate date comparison
        sale_pakistan = sale.created_at.astimezone(pakistan_tz)

        if sale_pakistan.date() == today_pakistan:
            today_sales_list.append(sale)
            today_sales_total += float(sale.total_amount)

            # Calculate profit for each item in the sale
            for item in sale.items.all():
                profit = (float(item.price) - float(item.product.cost_price)) * item.quantity
                today_profit += profit

    today_invoices = len(today_sales_list)

    # Calculations
    avg_ticket = today_sales_total / today_invoices if today_invoices else 0
    profit_margin = (today_profit / today_sales_total * 100) if today_sales_total else 0

    # Monthly Profit
    monthly_profit = 0
    for sale in all_sales:
        sale_pakistan = sale.created_at.astimezone(pakistan_tz)
        if sale_pakistan.year == today_pakistan.year and sale_pakistan.month == today_pakistan.month:
            for item in sale.items.all():
                profit = (float(item.price) - float(item.product.cost_price)) * item.quantity
                monthly_profit += profit

    # Statistics
    total_invoices = Sale.objects.count()
    total_products = Product.objects.filter(is_active=True).count()

    # Count unique customers (excluding empty names)
    total_customers = Sale.objects.exclude(
        customer_name__isnull=True
    ).exclude(customer_name='').values('customer_name').distinct().count()

    # New customers this month
    new_customers = Sale.objects.filter(
        created_at__year=today_pakistan.year,
        created_at__month=today_pakistan.month
    ).exclude(customer_name__isnull=True).exclude(customer_name='').values('customer_name').distinct().count()

    # Low Stock Alerts
    # Products where stock is less than or equal to reorder level
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('reorder_level'),
        is_active=True
    ).order_by('stock_quantity')

    low_stock = low_stock_products.count()

    # Top Selling Products
    top_products = SaleItem.objects.values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('line_total')
    ).order_by('-total_quantity')[:5]

    # Recent Sales
    recent_sales = Sale.objects.order_by('-id')[:5]

    # Sales Chart (Last 7 Days)
    chart_labels = []
    chart_data = []

    for i in range(6, -1, -1):
        check_date = today_pakistan - timedelta(days=i)
        chart_labels.append(check_date.strftime('%d %b'))

        daily_total = 0
        for sale in all_sales:
            sale_pakistan = sale.created_at.astimezone(pakistan_tz)
            if sale_pakistan.date() == check_date:
                daily_total += float(sale.total_amount)

        chart_data.append(round(daily_total, 2))

    # Context for Template
    context = {
        # Today's data
        'today_sales': round(today_sales_total, 2),
        'today_profit': round(today_profit, 2),
        'today_invoices': today_invoices,
        'today_transactions': today_sales_list,
        'profit_margin': round(profit_margin, 1),
        'avg_ticket': round(avg_ticket, 2),

        # Monthly data
        'monthly_profit': round(monthly_profit, 2),

        # Statistics
        'total_invoices': total_invoices,
        'total_products': total_products,
        'low_stock': low_stock,
        'low_stock_products': low_stock_products[:10],

        # Customer statistics
        'total_customers': total_customers,
        'new_customers': new_customers,
        'top_products': top_products,

        # Recent activity
        'recent_sales': recent_sales,

        # Chart data
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'dashboard/home.html', context)


# ============================================================
# BACKUP SYSTEM (SAFE VERSION - NO RESTORE)
# ============================================================

# Database Configuration - Update these with your actual credentials
BACKUP_DIR = 'backups'
BACKUP_RETENTION_DAYS = 7


@staff_member_required
def create_backup(request):
    """
    Create a database backup and automatically delete old backups.
    
    Features:
    - Creates timestamped backup file with readable format
    - Automatically deletes backups older than BACKUP_RETENTION_DAYS
    - Shows file size and creation date
    - No restore option (safe for shop owner)
    """
    
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate filename with date and time (readable format)
    now = datetime.now()
    filename = now.strftime("Farman_POS_Backup_%d_%B_%Y_%I_%M_%p.sql")
    backup_file = os.path.join(BACKUP_DIR, filename)
    
    try:
        # Execute MySQL dump command
        cmd = f'mysqldump -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} > "{backup_file}"'
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        # Get file size for display
        file_size_kb = os.path.getsize(backup_file) / 1024
        
        # Auto cleanup old backups
        deleted_count = cleanup_old_backups()
        
        success_message = f"""
        <html>
        <head><title>Backup Complete - Farman POS</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f2f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; }}
            .info {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: left; }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
            .btn:hover {{ background: #0056b3; }}
        </style>
        </head>
        <body>
            <div class="container">
                <h2 class="success">Database Backup Complete</h2>
                <div class="info">
                    <p><strong>File Name:</strong><br>{filename}</p>
                    <p><strong>File Size:</strong><br>{file_size_kb:.2f} KB</p>
                    <p><strong>Created:</strong><br>{now.strftime('%A, %B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Old Backups Deleted:</strong><br>{deleted_count} files (older than {BACKUP_RETENTION_DAYS} days)</p>
                    <p><strong>Location:</strong><br>{os.path.abspath(BACKUP_DIR)}</p>
                </div>
                <div>
                    <a href="/dashboard/" class="btn">Back to Dashboard</a>
                    <a href="/backup-list/" class="btn" style="background: #28a745;">View All Backups</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(success_message)
        
    except subprocess.CalledProcessError as e:
        error_message = f"""
        <html>
        <head><title>Backup Failed</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2 style="color: #dc3545;">Backup Failed</h2>
            <p>Error: {e.stderr}</p>
            <a href="/dashboard/">Back to Dashboard</a>
        </body>
        </html>
        """
        return HttpResponse(error_message, status=500)


def cleanup_old_backups():
    """
    Automatically delete backup files older than BACKUP_RETENTION_DAYS.
    Keeps only recent backups to save disk space.
    
    Returns:
        int: Number of files deleted
    """
    if not os.path.exists(BACKUP_DIR):
        return 0
    
    deleted_count = 0
    
    # Get all .sql files in backup directory
    backup_files = glob.glob(os.path.join(BACKUP_DIR, '*.sql'))
    
    for file_path in backup_files:
        # Get file creation/modification time
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        file_age_days = (datetime.now() - file_mtime).days
        
        # Delete if older than retention period
        if file_age_days > BACKUP_RETENTION_DAYS:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception:
                pass
    
    return deleted_count


@staff_member_required
def list_backups(request):
    """
    Display all available backup files with their details.
    Only DOWNLOAD option - NO RESTORE to prevent accidental data loss.
    """
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)
    
    backups = []
    backup_files = glob.glob(os.path.join(BACKUP_DIR, '*.sql'))
    
    for file_path in sorted(backup_files, key=os.path.getmtime, reverse=True):
        file_stat = os.stat(file_path)
        backups.append({
            'name': os.path.basename(file_path),
            'size_kb': round(file_stat.st_size / 1024, 2),
            'created': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    # Generate HTML response
    html = """
    <html>
    <head><title>Backup Manager - Farman POS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body style="background: #f0f2f5;">
        <div class="container mt-4">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h3 class="mb-0">Backup Manager</h3>
                    <small>All backups are safe to download. No restore option to prevent data loss.</small>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <a href="/backup/" class="btn btn-success">Create New Backup</a>
                        <a href="/dashboard/" class="btn btn-secondary">Back to Dashboard</a>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>File Name</th>
                                    <th>Size (KB)</th>
                                    <th>Created Date</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
    """
    
    for backup in backups:
        html += f"""
                            <tr>
                                <td><small>{backup['name']}</small></td>
                                <td>{backup['size_kb']} KB</small></td>
                                <td><small>{backup['created']}</small></td>
                                <td>
                                    <a href="/download-backup/{backup['name']}/" class="btn btn-sm btn-primary">
                                        Download
                                    </a>
                                </small></td>
                            </tr>
        """
    
    if not backups:
        html += """
                            <tr>
                                <td colspan="4" class="text-center">No backups found. Click "Create New Backup" to start.</td>
                            </tr>
        """
    
    html += """
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="alert alert-info mt-3 small">
                        <strong>Note:</strong> Backups are saved in the 'backups' folder. 
                        To restore data, please contact the system administrator.
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)


@staff_member_required
def download_backup(request, filename):
    """
    Download a specific backup file to local computer.
    Safe operation - does not modify database.
    
    Args:
        filename: Name of the backup file to download
    """
    file_path = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(file_path):
        return HttpResponse("Backup file not found", status=404)
    
    # Read file and return as download
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    response = HttpResponse(file_data, content_type='application/sql')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@staff_member_required
def backup_info(request):
    """
    Get backup system information (API endpoint).
    Returns JSON with backup statistics.
    """
    info = {
        'backup_dir': BACKUP_DIR,
        'retention_days': BACKUP_RETENTION_DAYS,
        'total_backups': 0,
        'total_size_mb': 0,
        'last_backup': None,
        'oldest_backup': None,
    }
    
    if os.path.exists(BACKUP_DIR):
        backup_files = glob.glob(os.path.join(BACKUP_DIR, '*.sql'))
        info['total_backups'] = len(backup_files)
        
        if backup_files:
            # Calculate total size
            total_bytes = sum(os.path.getsize(f) for f in backup_files)
            info['total_size_mb'] = round(total_bytes / (1024 * 1024), 2)
            
            # Get last backup time
            last_backup = max(backup_files, key=os.path.getmtime)
            info['last_backup'] = datetime.fromtimestamp(os.path.getmtime(last_backup)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Get oldest backup time
            oldest_backup = min(backup_files, key=os.path.getmtime)
            info['oldest_backup'] = datetime.fromtimestamp(os.path.getmtime(oldest_backup)).strftime('%Y-%m-%d %H:%M:%S')
    
    return JsonResponse(info)