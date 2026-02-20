"""
Management command to populate database with sample data
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import User, Category, Product, StockEntry
from decimal import Decimal
import random
from datetime import datetime, timedelta
from pathlib import Path
import os

class Command(BaseCommand):
    help = 'Populate database with sample categories and products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--items-per-category',
            type=int,
            default=100,
            help='Number of items to create per category (default: 100)'
        )

    def handle(self, *args, **options):
        items_per_category = options['items_per_category']
        
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Get available local images from media/products folder
        media_products_path = Path(settings.MEDIA_ROOT) / 'products'
        available_images = list(media_products_path.glob('*.jpg')) + list(media_products_path.glob('*.png'))
        image_filenames = ['products/' + img.name for img in available_images]
        
        if not image_filenames:
            self.stdout.write(self.style.WARNING('⚠ No images found in media/products folder'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Found {len(image_filenames)} local images'))
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@supermart.com',
            defaults={
                'username': 'admin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'ADMIN',
                'phone': '9876543210'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))
        
        # Create manager user
        manager_user, created = User.objects.get_or_create(
            email='manager@supermart.com',
            defaults={
                'username': 'manager',
                'first_name': 'Store',
                'last_name': 'Manager',
                'role': 'MANAGER',
                'phone': '9876543211'
            }
        )
        if created:
            manager_user.set_password('manager123')
            manager_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created manager user'))
        
        # Create staff user
        staff_user, created = User.objects.get_or_create(
            email='staff@supermart.com',
            defaults={
                'username': 'staff',
                'first_name': 'Store',
                'last_name': 'Staff',
                'role': 'STAFF',
                'phone': '9876543212'
            }
        )
        if created:
            staff_user.set_password('staff123')
            staff_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created staff user'))
        
        # Create customer user
        customer_user, created = User.objects.get_or_create(
            email='customer@supermart.com',
            defaults={
                'username': 'customer',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'CUSTOMER',
                'phone': '9876543213'
            }
        )
        if created:
            customer_user.set_password('customer123')
            customer_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created customer user'))
        
        # Define categories with sample products
        categories_data = {
            'Electronics': {
                'brands': ['Samsung', 'Apple', 'Sony', 'LG', 'Dell', 'HP', 'Lenovo', 'Asus', 'OnePlus', 'Xiaomi'],
                'products': ['Smartphone', 'Laptop', 'Tablet', 'Smartwatch', 'Earbuds', 'Monitor', 'Keyboard', 'Mouse', 'Webcam', 'Speaker'],
                'models': ['Pro', 'Max', 'Ultra', 'Plus', 'Lite', 'Air', 'Prime', 'Edge', 'Note', 'Series'],
                'price_range': (5000, 150000)
            },
            'Fashion': {
                'brands': ['Nike', 'Adidas', 'Puma', 'Reebok', 'Levi\'s', 'Zara', 'H&M', 'Polo', 'Tommy', 'Arrow'],
                'products': ['T-Shirt', 'Jeans', 'Shoes', 'Jacket', 'Hoodie', 'Shorts', 'Dress', 'Shirt', 'Sneakers', 'Boots'],
                'models': ['Classic', 'Premium', 'Sport', 'Casual', 'Formal', 'Slim Fit', 'Regular', 'Stretch', 'Cotton', 'Denim'],
                'price_range': (500, 15000)
            },
            'Groceries': {
                'brands': ['Amul', 'Nestle', 'ITC', 'Parle', 'Britannia', 'Mother Dairy', 'Haldiram\'s', 'Patanjali', 'Dabur', 'Fortune'],
                'products': ['Milk', 'Bread', 'Biscuits', 'Rice', 'Oil', 'Tea', 'Coffee', 'Butter', 'Cheese', 'Noodles'],
                'models': ['1kg', '500g', '1L', '2L', '500ml', 'Pack of 6', 'Family Pack', 'Economy', 'Premium', 'Organic'],
                'price_range': (20, 2000)
            },
            'Home & Kitchen': {
                'brands': ['Philips', 'Prestige', 'Bajaj', 'Butterfly', 'Pigeon', 'Milton', 'Hawkins', 'Cello', 'Tupperware', 'Borosil'],
                'products': ['Mixer Grinder', 'Pressure Cooker', 'Water Bottle', 'Lunch Box', 'Kettle', 'Toaster', 'Frying Pan', 'Cooker', 'Container Set', 'Spice Box'],
                'models': ['2L', '3L', '5L', '750ml', '1L', 'Set of 3', 'Set of 6', 'Stainless Steel', 'Non-Stick', 'Glass'],
                'price_range': (200, 12000)
            },
            'Books & Stationery': {
                'brands': ['Classmate', 'Faber-Castell', 'Camlin', 'Apsara', 'Reynolds', 'Parker', 'Penguin', 'Oxford', 'Navneet', 'Bic'],
                'products': ['Notebook', 'Pen', 'Pencil', 'Eraser', 'Sharpener', 'Book', 'Diary', 'Markers', 'Highlighter', 'Calculator'],
                'models': ['Single Line', 'Four Line', 'Unruled', 'A4', 'A5', 'Pack of 10', 'Set of 5', 'Blue', 'Black', 'Multicolor'],
                'price_range': (10, 2000)
            },
            'Sports & Fitness': {
                'brands': ['Nivia', 'Cosco', 'Yonex', 'Reebok', 'Adidas', 'Decathlon', 'Vector X', 'Spartan', 'Strauss', 'Fitness Mantra'],
                'products': ['Football', 'Cricket Bat', 'Badminton Racket', 'Yoga Mat', 'Dumbbells', 'Skipping Rope', 'Tennis Ball', 'Gym Bag', 'Sports Shoes', 'Resistance Band'],
                'models': ['5kg', '10kg', 'Size 5', 'Professional', 'Beginner', 'Junior', 'Senior', 'Standard', 'Premium', 'Pro'],
                'price_range': (200, 15000)
            },
            'Beauty & Personal Care': {
                'brands': ['Lakme', 'Maybelline', 'Nivea', 'Dove', 'Garnier', 'L\'Oreal', 'Himalaya', 'Vaseline', 'Biotique', 'Neutrogena'],
                'products': ['Face Cream', 'Shampoo', 'Conditioner', 'Body Wash', 'Lotion', 'Face Wash', 'Lipstick', 'Kajal', 'Sunscreen', 'Moisturizer'],
                'models': ['50ml', '100ml', '200ml', 'For Dry Skin', 'For Oily Skin', 'Anti-Aging', 'Whitening', 'Natural', 'Herbal', 'SPF 30'],
                'price_range': (100, 3000)
            },
            'Toys & Games': {
                'brands': ['Lego', 'Hot Wheels', 'Barbie', 'Funskool', 'Hasbro', 'Mattel', 'Fisher Price', 'Playmate', 'Webby', 'Centy'],
                'products': ['Building Blocks', 'Remote Control Car', 'Doll', 'Board Game', 'Puzzle', 'Action Figure', 'Soft Toy', 'Car Set', 'Educational Toy', 'Musical Toy'],
                'models': ['Age 3+', 'Age 5+', 'Age 8+', 'Set of 100', 'Large', 'Medium', 'Small', 'Battery Operated', 'Manual', 'Interactive'],
                'price_range': (150, 8000)
            }
        }
        
        self.stdout.write('\nCreating categories and products...\n')
        
        total_products = 0
        
        for category_name, data in categories_data.items():
            # Create category
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'description': f'Wide range of {category_name.lower()} products at best prices'
                }
            )
            
            if created:
                self.stdout.write(f'✓ Created category: {category_name}')
            
            # Create products for this category
            products_created = 0
            
            for i in range(items_per_category):
                # Generate product name
                brand = random.choice(data['brands'])
                product = random.choice(data['products'])
                model = random.choice(data['models'])
                
                name = f'{brand} {product} {model}'
                if i > 0:  # Add variant number for duplicates
                    name = f'{name} - V{i//10 + 1}'
                
                # Generate SKU
                sku = f'{category_name[:3].upper()}-{brand[:3].upper()}-{random.randint(10000, 99999)}'
                
                # Check if SKU already exists
                if Product.objects.filter(sku=sku).exists():
                    continue
                
                # Generate random price
                price = Decimal(random.randint(data['price_range'][0], data['price_range'][1]))
                
                # Generate random quantity (70% in stock, 30% low/out of stock)
                stock_status = random.random()
                if stock_status < 0.7:
                    quantity = random.randint(50, 500)
                elif stock_status < 0.9:
                    quantity = random.randint(1, 49)  # Low stock
                else:
                    quantity = 0  # Out of stock
                
                # Random supplier
                suppliers = ['ABC Distributors', 'XYZ Wholesale', 'Prime Suppliers', 'Elite Traders', 'Global Imports']
                supplier = random.choice(suppliers)
                
                # Assign a random local image
                image_path = random.choice(image_filenames) if image_filenames else None
                
                # Create product
                product_obj = Product.objects.create(
                    name=name,
                    sku=sku,
                    category=category,
                    description=f'High quality {product.lower()} from {brand}. {model} variant with excellent features and durability.',
                    price=price,
                    quantity=quantity,
                    supplier=supplier,
                    image=image_path
                )
                
                # Create stock entry for initial stock
                if quantity > 0:
                    StockEntry.objects.create(
                        product=product_obj,
                        entry_type='IN',
                        quantity=quantity,
                        notes=f'Initial stock for {name}',
                        created_by=staff_user
                    )
                
                products_created += 1
            
            total_products += products_created
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created {products_created} products in {category_name}'))
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'\n🎉 DATA POPULATION COMPLETED!\n'))
        self.stdout.write(f'Categories: {len(categories_data)}')
        self.stdout.write(f'Products: {total_products}')
        self.stdout.write(f'Users: 4 (Admin, Manager, Staff, Customer)')
        self.stdout.write(f'Images: {len(image_filenames)} local images used')
        self.stdout.write('\n' + '='*60)
        
        self.stdout.write('\n📝 LOGIN CREDENTIALS:\n')
        self.stdout.write('  Admin:    admin@supermart.com / admin123')
        self.stdout.write('  Manager:  manager@supermart.com / manager123')
        self.stdout.write('  Staff:    staff@supermart.com / staff123')
        self.stdout.write('  Customer: customer@supermart.com / customer123')
        self.stdout.write('\n' + '='*60 + '\n')
