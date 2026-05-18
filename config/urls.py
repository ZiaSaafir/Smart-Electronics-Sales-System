from django.contrib import admin
from django.urls import path, include
from dashboard.views import create_backup, list_backups, download_backup, backup_info

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('pos/', include('sales.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('low-stock/', include('inventory.urls')),
    path('purchase/', include('purchase.urls')),
    path('returns/', include('returns.urls')),
    path('products/', include('products.urls')),  
    path('sales/', include('sales.urls')),  
    
    # Safe Backup URLs - No restore function to prevent data loss
    path('backup/', create_backup, name='backup'),
    path('backup-list/', list_backups, name='backup_list'),
    path('download-backup/<str:filename>/', download_backup, name='download_backup'),
    path('backup-info/', backup_info, name='backup_info'),
]