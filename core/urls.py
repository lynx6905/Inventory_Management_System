"""
URL Configuration for core app
"""
from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Auth
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Products
    path('products/', views.products_list, name='products_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # Role Dashboards
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Customer Views
    path('customer/orders/', views.order_history, name='order_history'),
    path('customer/profile/', views.customer_profile, name='customer_profile'),

    # Staff Views
    path('staff/stock-entry/', views.stock_entry_view, name='stock_entry_view'),

    # Manager Views
    path('manager/inventory/', views.manager_inventory, name='manager_inventory'),
    path('manager/approvals/', views.manager_approvals, name='manager_approvals'),

    # Admin Views
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/inventory/', views.inventory_dashboard, name='inventory_dashboard'),
    path('admin/reports/', views.purchase_reports, name='purchase_reports'),
    path('admin/analytics/', views.analytics_view, name='analytics'),

    # Chatbot
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]
