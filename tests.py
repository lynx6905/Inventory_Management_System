"""
Tests for core app
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Product, Category, Cart, CartItem, Order

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def test_admin_role_assignment(self):
        """Test admin role is auto-assigned"""
        user = User.objects.create_user(
            username='testadmin',
            email='admin@supermart.com',
            password='testpass123'
        )
        self.assertEqual(user.role, 'ADMIN')
    
    def test_customer_role_assignment(self):
        """Test customer role is auto-assigned"""
        user = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123'
        )
        self.assertEqual(user.role, 'CUSTOMER')


class ProductModelTest(TestCase):
    """Test Product model"""
    
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST001',
            category=self.category,
            description='Test description',
            price=100.00,
            quantity=50,
            supplier='Test Supplier',
            low_stock_threshold=10
        )
    
    def test_product_creation(self):
        """Test product is created correctly"""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.sku, 'TEST001')
    
    def test_in_stock_property(self):
        """Test in_stock property"""
        self.assertTrue(self.product.in_stock)
        self.product.quantity = 0
        self.assertFalse(self.product.in_stock)
    
    def test_is_low_stock_property(self):
        """Test is_low_stock property"""
        self.assertFalse(self.product.is_low_stock)
        self.product.quantity = 5
        self.assertTrue(self.product.is_low_stock)


class CartTest(TestCase):
    """Test Cart functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST001',
            category=self.category,
            description='Test',
            price=100.00,
            quantity=50,
            supplier='Test Supplier'
        )
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_total_amount(self):
        """Test cart total calculation"""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(self.cart.total_amount, 200.00)
    
    def test_cart_total_items(self):
        """Test cart item count"""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(self.cart.total_items, 3)


class ViewsTest(TestCase):
    """Test views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_products_page(self):
        """Test products page loads"""
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
    
    def test_cart_requires_login(self):
        """Test cart page requires authentication"""
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_user_login(self):
        """Test user can login"""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
