"""
Database initialization script
Run this script to set up initial data for the Supermart application
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermart_project.settings')
django.setup()

from core.models import User, Category, Product


def create_users():
    """Create default users for each role"""
    print("Creating default users...")
    
    # Admin user
    if not User.objects.filter(email='admin@supermart.com').exists():
        User.objects.create_user(
            username='admin',
            email='admin@supermart.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
            phone='9999999999',
            address='Admin Office, Supermart HQ'
        )
        print("✓ Admin user created")
    
    # Manager user
    if not User.objects.filter(email='manager@supermart.com').exists():
        User.objects.create_user(
            username='manager',
            email='manager@supermart.com',
            password='manager123',
            first_name='Manager',
            last_name='User',
            phone='8888888888',
            address='Manager Office, Supermart'
        )
        print("✓ Manager user created")
    
    # Staff user
    if not User.objects.filter(email='staff@supermart.com').exists():
        User.objects.create_user(
            username='staff',
            email='staff@supermart.com',
            password='staff123',
            first_name='Staff',
            last_name='User',
            phone='7777777777',
            address='Staff Quarters, Supermart'
        )
        print("✓ Staff user created")
    
    # Customer user
    if not User.objects.filter(email='customer@example.com').exists():
        User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customer123',
            first_name='Customer',
            last_name='User',
            phone='6666666666',
            address='123 Customer Street, City'
        )
        print("✓ Customer user created")


def create_categories():
    """Create sample categories"""
    print("\nCreating categories...")
    
    categories = [
        {'name': 'Electronics', 'description': 'Electronic items, gadgets, and accessories'},
        {'name': 'Groceries', 'description': 'Daily grocery items and food products'},
        {'name': 'Clothing', 'description': 'Fashion, apparel, and accessories'},
        {'name': 'Home & Kitchen', 'description': 'Home essentials and kitchen items'},
        {'name': 'Books & Stationery', 'description': 'Books, office supplies, and stationery'},
        {'name': 'Sports & Fitness', 'description': 'Sports equipment and fitness items'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"✓ Category created: {category.name}")


def create_sample_products():
    """Create sample products"""
    print("\nCreating sample products...")
    
    # Get categories
    electronics = Category.objects.get(name='Electronics')
    groceries = Category.objects.get(name='Groceries')
    clothing = Category.objects.get(name='Clothing')
    home = Category.objects.get(name='Home & Kitchen')
    
    products = [
        # Electronics
        {'name': 'Samsung LED TV 43"', 'sku': 'ELEC001', 'category': electronics, 
         'description': '43 inch Full HD LED TV with smart features', 
         'price': 35999.00, 'quantity': 25, 'supplier': 'Samsung India', 'low_stock_threshold': 5},
        
        {'name': 'Sony Bluetooth Headphones', 'sku': 'ELEC002', 'category': electronics,
         'description': 'Wireless Bluetooth headphones with noise cancellation',
         'price': 2999.00, 'quantity': 50, 'supplier': 'Sony Electronics', 'low_stock_threshold': 10},
        
        {'name': 'HP Laptop i5 8GB', 'sku': 'ELEC003', 'category': electronics,
         'description': 'HP Laptop with Intel i5, 8GB RAM, 512GB SSD',
         'price': 45999.00, 'quantity': 15, 'supplier': 'HP India', 'low_stock_threshold': 5},
        
        # Groceries
        {'name': 'Basmati Rice 5kg', 'sku': 'GROC001', 'category': groceries,
         'description': 'Premium quality basmati rice',
         'price': 450.00, 'quantity': 100, 'supplier': 'India Gate', 'low_stock_threshold': 20},
        
        {'name': 'Fortune Sunflower Oil 1L', 'sku': 'GROC002', 'category': groceries,
         'description': 'Refined sunflower oil',
         'price': 150.00, 'quantity': 80, 'supplier': 'Adani Wilmar', 'low_stock_threshold': 15},
        
        {'name': 'Tata Tea Premium 1kg', 'sku': 'GROC003', 'category': groceries,
         'description': 'Premium quality tea leaves',
         'price': 425.00, 'quantity': 60, 'supplier': 'Tata Consumer', 'low_stock_threshold': 15},
        
        # Clothing
        {'name': 'Mens Cotton T-Shirt', 'sku': 'CLOT001', 'category': clothing,
         'description': 'Comfortable cotton t-shirt in various colors',
         'price': 499.00, 'quantity': 120, 'supplier': 'Raymond', 'low_stock_threshold': 20},
        
        {'name': 'Womens Kurti', 'sku': 'CLOT002', 'category': clothing,
         'description': 'Designer kurti with beautiful prints',
         'price': 899.00, 'quantity': 75, 'supplier': 'Fabindia', 'low_stock_threshold': 15},
        
        # Home & Kitchen
        {'name': 'Prestige Pressure Cooker 5L', 'sku': 'HOME001', 'category': home,
         'description': 'Stainless steel pressure cooker',
         'price': 1899.00, 'quantity': 40, 'supplier': 'Prestige', 'low_stock_threshold': 10},
        
        {'name': 'Philips Air Fryer', 'sku': 'HOME002', 'category': home,
         'description': 'Digital air fryer with multiple cooking modes',
         'price': 8999.00, 'quantity': 20, 'supplier': 'Philips India', 'low_stock_threshold': 5},
    ]
    
    for prod_data in products:
        product, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults=prod_data
        )
        if created:
            print(f"✓ Product created: {product.name}")


def main():
    """Main function to run all setup"""
    print("=" * 60)
    print("SUPERMART - Database Initialization")
    print("=" * 60)
    
    try:
        create_users()
        create_categories()
        create_sample_products()
        
        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully!")
        print("=" * 60)
        print("\nDefault Login Credentials:")
        print("-" * 60)
        print("Admin:    Username: admin    | Password: admin123")
        print("Manager:  Username: manager  | Password: manager123")
        print("Staff:    Username: staff    | Password: staff123")
        print("Customer: Username: customer | Password: customer123")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        print("Make sure you have run migrations first:")
        print("  python manage.py makemigrations")
        print("  python manage.py migrate")


if __name__ == '__main__':
    main()
