from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse

def cashier_required(function=None):
    """Allow only cashier or admin access to POS"""
    def check(user):
        if not user.is_authenticated:
            return False
        # Superuser always has access
        if user.is_superuser:
            return True
        # Check if user has profile with cashier or admin role
        if hasattr(user, 'userprofile'):
            return user.userprofile.role in ['admin', 'cashier']
        return False
    
    actual_decorator = user_passes_test(
        check,
        login_url='/accounts/login/'
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None):
    """Allow only admin access"""
    def check(user):
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if hasattr(user, 'userprofile'):
            return user.userprofile.role == 'admin'
        return False
    
    actual_decorator = user_passes_test(
        check,
        login_url='/accounts/login/'
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator