from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect


def cashier_required(function=None):
    """
    Decorator that allows access only to:
    - Admin users (superuser/staff)
    - Cashier users (with role='cashier')
    """
    def check(user):
        # Not logged in
        if not user.is_authenticated:
            return False
        
        # Superuser always has access
        if user.is_superuser:
            return True
        
        # Staff users have access
        if user.is_staff:
            return True
        
        # Check if user has profile with cashier or admin role
        if hasattr(user, 'userprofile'):
            return user.userprofile.role in ['admin', 'cashier']
        
        # If no profile, deny access
        return False
    
    actual_decorator = user_passes_test(
        check,
        login_url='/accounts/login/',
        redirect_field_name='next'
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None):
    """
    Decorator that allows access only to:
    - Admin users (superuser/staff)
    - Users with role='admin'
    """
    def check(user):
        if not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        if user.is_staff:
            return True
        
        if hasattr(user, 'userprofile'):
            return user.userprofile.role == 'admin'
        
        return False
    
    actual_decorator = user_passes_test(
        check,
        login_url='/accounts/login/',
        redirect_field_name='next'
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator