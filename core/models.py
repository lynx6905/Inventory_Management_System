"""
Core models for Supermart application
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User Model with role-based access"""
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('STAFF', 'Staff'),
        ('CUSTOMER', 'Customer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Auto-assign role based on email domain and prefix
        # Only @supermart.com users can be ADMIN, MANAGER, or STAFF
        # All other emails are CUSTOMER
        
        if self.email and '@supermart.com' in self.email:
            email_prefix = self.email.split('@')[0].lower()
            
            if email_prefix == 'admin':
                self.role = 'ADMIN'
            elif email_prefix == 'manager':
                self.role = 'MANAGER'
            elif email_prefix == 'staff':
                self.role = 'STAFF'
            else:
                # Other @supermart.com emails are staff by default
                self.role = 'STAFF'
        else:
            # All non-supermart.com emails are customers
            self.role = 'CUSTOMER'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Category(models.Model):
    """Product Category"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product/Inventory Model"""
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    supplier = models.CharField(max_length=200)
    low_stock_threshold = models.IntegerField(default=10)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="External image URL if not using local image.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold
    
    @property
    def in_stock(self):
        return self.quantity > 0


class Cart(models.Model):
    """Shopping Cart"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Cart Items"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Purchase Order"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    
    order_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_id}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Order Items"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity


class ChatMessage(models.Model):
    """Advanced AI Chatbot Message Model with Intent and Sentiment Analysis"""
    INTENT_CHOICES = [
        ('greeting', 'Greeting'),
        ('farewell', 'Farewell'),
        ('thanks', 'Thanks'),
        ('product_search', 'Product Search'),
        ('price_inquiry', 'Price Inquiry'),
        ('stock_inquiry', 'Stock Inquiry'),
        ('recommendation', 'Recommendation'),
        ('order_tracking', 'Order Tracking'),
        ('category_browse', 'Category Browse'),
        ('help', 'Help'),
        ('complaint', 'Complaint'),
        ('comparison', 'Comparison'),
        ('general', 'General'),
    ]
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    session_id = models.CharField(max_length=100, db_index=True)
    message = models.TextField()
    response = models.TextField()
    intent = models.CharField(max_length=50, choices=INTENT_CHOICES, default='general')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat - {self.session_id} ({self.intent})"
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'AI Chat Message'
        verbose_name_plural = 'AI Chat Messages'


class StockEntry(models.Model):
    """Stock Entry Log"""
    ENTRY_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Adjustment'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.entry_type} - {self.quantity}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stock Entries'
