"""
Role-based access control decorators
"""
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def role_required(allowed_roles=[]):
    """Decorator to restrict access based on user role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator for admin-only views"""
    return role_required(['ADMIN'])(view_func)


def manager_required(view_func):
    """Decorator for manager and admin views"""
    return role_required(['ADMIN', 'MANAGER'])(view_func)


def staff_required(view_func):
    """Decorator for staff, manager and admin views"""
    return role_required(['ADMIN', 'MANAGER', 'STAFF'])(view_func)


def customer_required(view_func):
    """Decorator for customer views"""
    return role_required(['CUSTOMER'])(view_func)
