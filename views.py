"""
Stable Views for Supermart Application
"""

import json
import uuid
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q, F
from django.views.decorators.csrf import csrf_exempt

from .models import (
    User, Product, Category,
    Cart, CartItem, Order, OrderItem,
    StockEntry
)
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    CheckoutForm
)
from .decorators import (
    admin_required,
    manager_required,
    staff_required,
    customer_required
)

logger = logging.getLogger(__name__)

# ================= HOME =================

def home(request):
    featured_products = Product.objects.filter(quantity__gt=0)[:8]
    categories = Category.objects.all()

    return render(request, "home.html", {
        "featured_products": featured_products,
        "categories": categories,
    })


# ================= AUTH =================

def user_register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = UserRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("home")

    return render(request, "register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = UserLoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        # Try to find user by email first
        try:
            user_obj = User.objects.get(email__iexact=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            login(request, user)

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            elif user.role == "MANAGER":
                return redirect("manager_dashboard")
            elif user.role == "STAFF":
                return redirect("staff_dashboard")
            else:
                return redirect("customer_dashboard")

        messages.error(request, "Invalid email or password.")

    return render(request, "login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("home")


# ================= PRODUCTS =================

def products_list(request):
    logger.debug("Fetching products and categories")
    products = Product.objects.filter(quantity__gt=0)
    categories = Category.objects.all()

    category_id = request.GET.get("category")
    search = request.GET.get("search")

    if category_id:
        logger.debug(f"Filtering products by category: {category_id}")
        products = products.filter(category_id=category_id)

    if search:
        logger.debug(f"Filtering products by search term: {search}")
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    logger.debug(f"Products count: {products.count()}, Categories count: {categories.count()}")
    return render(request, "products.html", {
        "products": products,
        "categories": categories,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product_detail.html", {"product": product})


# ================= CART =================

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart_view")


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart.html", {"cart": cart})


@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(
        CartItem,
        pk=pk,
        cart__user=request.user
    )

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        if 0 < quantity <= cart_item.product.quantity:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated.")
        else:
            messages.error(request, "Invalid quantity.")

    return redirect("cart_view")


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(
        CartItem,
        pk=pk,
        cart__user=request.user
    )
    cart_item.delete()
    messages.success(request, "Item removed.")
    return redirect("cart_view")


# ================= CHECKOUT =================

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if cart.items.count() == 0:
        messages.warning(request, "Cart is empty.")
        return redirect("cart_view")

    form = CheckoutForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        order = Order.objects.create(
            order_id=f"ORD{uuid.uuid4().hex[:8].upper()}",
            user=request.user,
            total_amount=cart.total_amount,
            shipping_address=form.cleaned_data["shipping_address"],
            payment_status="SUCCESS",
            order_status="CONFIRMED"
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            item.product.quantity -= item.quantity
            item.product.save()

        cart.delete()
        return redirect("customer_dashboard")

    return render(request, "checkout.html", {
        "cart": cart,
        "form": form
    })


# ================= ROLE DASHBOARDS =================

@login_required
@customer_required
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if not orders.exists() and cart.items.exists():
        return render(request, "customer/dashboard.html", {"cart": cart})

    return render(request, "customer/dashboard.html", {"orders": orders})


@login_required
@staff_required
def staff_dashboard(request):
    low_stock = Product.objects.filter(
        quantity__lte=F("low_stock_threshold")
    )
    return render(request, "staff/dashboard.html", {"low_stock": low_stock})


@login_required
@manager_required
def manager_dashboard(request):
    total_products = Product.objects.count()
    low_stock = Product.objects.filter(quantity__lte=F('low_stock_threshold'))
    pending_orders = Order.objects.filter(order_status='PENDING').count()
    total_revenue = Order.objects.filter(
        payment_status="SUCCESS"
    ).aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    
    return render(request, "manager/dashboard.html", {
        "total_products": total_products,
        "low_stock_count": low_stock.count(),
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
    })


@login_required
@admin_required
def admin_dashboard(request):
    total_revenue = Order.objects.filter(
        payment_status="SUCCESS"
    ).aggregate(Sum("total_amount"))["total_amount__sum"] or 0

    return render(request, "admin/dashboard.html", {
        "total_users": User.objects.count(),
        "total_revenue": total_revenue,
    })


# ================= CUSTOMER VIEWS =================

@login_required
@customer_required
def order_history(request):
    """Display customer's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "customer/order_history.html", {"orders": orders})


@login_required
@customer_required
def customer_profile(request):
    """Display and edit customer profile"""
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('customer_profile')
    
    return render(request, "customer/profile.html", {"user": user})


# ================= STAFF VIEWS =================

@login_required
@staff_required
def stock_entry_view(request):
    """Staff stock entry view"""
    from .forms import StockEntryForm
    
    products = Product.objects.all()
    recent_entries = StockEntry.objects.all().order_by('-created_at')[:10]
    
    if request.method == "POST":
        form = StockEntryForm(request.POST)
        if form.is_valid():
            stock_entry = form.save(commit=False)
            stock_entry.created_by = request.user
            stock_entry.save()
            
            # Update product quantity
            product = stock_entry.product
            if stock_entry.entry_type == 'IN':
                product.quantity += stock_entry.quantity
            elif stock_entry.entry_type == 'OUT':
                product.quantity = max(0, product.quantity - stock_entry.quantity)
            product.save()
            
            messages.success(request, f"Stock {stock_entry.entry_type} recorded successfully!")
            return redirect('stock_entry_view')
    else:
        form = StockEntryForm()
    
    return render(request, "staff/stock_entry.html", {
        "form": form,
        "products": products,
        "entries": recent_entries,
    })


# ================= MANAGER VIEWS =================

@login_required
@manager_required
def manager_inventory(request):
    """Manager inventory management view"""
    products = Product.objects.all()
    low_stock = products.filter(quantity__lte=F('low_stock_threshold'))
    
    return render(request, "manager/inventory.html", {
        "products": products,
        "low_stock_count": low_stock.count(),
        "low_stock": low_stock,
    })


@login_required
@manager_required
def manager_approvals(request):
    """Manager approvals view"""
    return render(request, "manager/approvals.html", {})


# ================= ADMIN VIEWS =================

@login_required
@admin_required
def user_management(request):
    """Admin user management view"""
    users = User.objects.all()
    
    if request.method == "POST":
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        if action == 'delete':
            user.delete()
            messages.success(request, f"User {user.username} deleted!")
        elif action == 'role_change':
            new_role = request.POST.get('new_role')
            user.role = new_role
            user.save()
            messages.success(request, f"User role updated to {new_role}!")
        
        return redirect('user_management')
    
    return render(request, "admin/user_management.html", {"users": users})


@login_required
@admin_required
def inventory_dashboard(request):
    """Admin inventory dashboard"""
    total_products = Product.objects.count()
    low_stock = Product.objects.filter(quantity__lte=F('low_stock_threshold'))
    out_of_stock = Product.objects.filter(quantity=0)
    
    return render(request, "admin/inventory_dashboard.html", {
        "total_products": total_products,
        "low_stock_count": low_stock.count(),
        "out_of_stock_count": out_of_stock.count(),
        "low_stock": low_stock,
    })


@login_required
@admin_required
def purchase_reports(request):
    """Admin purchase reports view"""
    orders = Order.objects.all().order_by('-created_at')
    total_orders = orders.count()
    total_revenue = orders.filter(
        payment_status="SUCCESS"
    ).aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    
    return render(request, "admin/purchase_reports.html", {
        "orders": orders,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
    })


@login_required
@admin_required
def analytics_view(request):
    """Admin analytics view"""
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(
        payment_status="SUCCESS"
    ).aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    
    return render(request, "admin/analytics.html", {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
    })


# ================= CHATBOT =================

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "").lower()

        response = "I'm your Supermart assistant. Ask me about products, prices, or categories!"

        if "category" in message:
            categories = Category.objects.all()
            response = "Available Categories:\n"
            for cat in categories:
                response += f"- {cat.name}\n"

        elif "price" in message:
            response = "Please mention the product name to check price."

        elif "stock" in message:
            response = "Tell me the product name to check stock."

        return JsonResponse({"response": response})

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def payment_callback(request):
    return JsonResponse({"status": "success", "message": "Payment callback received."})

def payment_success(request, order_id):
    return render(request, "payment_success.html", {"order_id": order_id})

def payment_failure(request):
    return render(request, "payment_failure.html")
