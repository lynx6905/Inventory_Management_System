"""
Management command to create products from existing image files
This ensures all products get matched with their corresponding images
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import User, Category, Product, StockEntry
from decimal import Decimal
import random
from pathlib import Path
import re


class Command(BaseCommand):
    help = 'Populate products using existing image filenames to ensure proper image matching'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing products before populating'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of products to create (for testing)'
        )

    def handle(self, *args, **options):
        clear_existing = options['clear_existing']
        limit = options['limit']
        
        self.stdout.write(self.style.SUCCESS('\n📦 Creating products from image files...\n'))
        
        # Get staff user
        staff_user = User.objects.filter(role='STAFF').first()
        if not staff_user:
            self.stdout.write(self.style.ERROR('❌ Staff user not found. Please create users first.'))
            return
        
        # Clear existing products if requested
        if clear_existing:
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING('✓ Cleared existing products'))
        
        # Get media path
        media_products_path = Path(settings.MEDIA_ROOT) / 'products'
        
        if not media_products_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Media products folder not found: {media_products_path}'))
            return
        
        # Get all image files
        image_files = list(media_products_path.glob('*.jpg')) + list(media_products_path.glob('*.png'))
        self.stdout.write(f'📁 Found {len(image_files)} image files\n')
        
        if limit:
            image_files = image_files[:limit]
            self.stdout.write(f'📌 Limited to {limit} products\n')
        
        # Category mapping based on file prefix
        category_map = {
            'ELE': 'Electronics',
            'FAS': 'Fashion',
            'GRO': 'Groceries',
            'HOM': 'Home & Kitchen',
            'BOO': 'Books & Stationery',
            'SPO': 'Sports & Fitness',
            'BEA': 'Beauty & Personal Care',
            'TOY': 'Toys & Games'
        }
        
        # Brand map based on file middle prefix
        brand_map = {
            'SAM': 'Samsung', 'APP': 'Apple', 'SON': 'Sony', 'LG': 'LG', 'DEL': 'Dell',
            'HP': 'HP', 'LEN': 'Lenovo', 'ASU': 'Asus', 'ONE': 'OnePlus', 'XIA': 'Xiaomi',
            'NIK': 'Nike', 'ADI': 'Adidas', 'PUM': 'Puma', 'REE': 'Reebok', 'LEV': 'Levi\'s',
            'ZAR': 'Zara', 'H&M': 'H&M', 'POL': 'Polo', 'TOM': 'Tommy', 'ARR': 'Arrow',
            'AMU': 'Amul', 'NES': 'Nestle', 'ITC': 'ITC', 'PAR': 'Parle', 'BRI': 'Britannia',
            'MOT': 'Mother Dairy', 'HAL': 'Haldiram\'s', 'PAT': 'Patanjali', 'DAB': 'Dabur',
            'FOR': 'Fortune',
            'PHI': 'Philips', 'PRE': 'Prestige', 'BAJ': 'Bajaj', 'BUT': 'Butterfly',
            'PIG': 'Pigeon', 'MIL': 'Milton', 'HAW': 'Hawkins', 'CEL': 'Cello',
            'TUP': 'Tupperware', 'BOR': 'Borosil',
            'CLA': 'Classmate', 'FAB': 'Faber-Castell', 'CAM': 'Camlin', 'APS': 'Apsara',
            'PEN': 'Reynolds', 'PAR': 'Parker', 'NAV': 'Navneet', 'OXF': 'Oxford',
            'BIC': 'Bic', 'REY': 'Penguin',
            'NIV': 'Nivia', 'COS': 'Cosco', 'YON': 'Yonex', 'DEC': 'Decathlon',
            'VEC': 'Vector X', 'SPA': 'Spartan', 'STR': 'Strauss', 'FIT': 'Fitness Mantra',
            'LAK': 'Lakme', 'MAY': 'Maybelline', 'DOV': 'Dove', 'GAR': 'Garnier',
            'L\'O': 'L\'Oreal', 'HIM': 'Himalaya', 'VAS': 'Vaseline', 'BIO': 'Biotique',
            'NEU': 'Neutrogena',
            'LEG': 'Lego', 'HOT': 'Hot Wheels', 'BAR': 'Barbie', 'FUN': 'Funskool',
            'HAS': 'Hasbro', 'MAT': 'Mattel', 'FIS': 'Fisher Price', 'PLA': 'Playmate',
            'WEB': 'Webby', 'CEN': 'Centy'
        }
        
        # Create/get categories
        categories = {}
        for prefix, cat_name in category_map.items():
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'Wide range of {cat_name.lower()} products'}
            )
            categories[prefix] = cat
        
        self.stdout.write(f'✓ Ensured {len(categories)} categories exist\n')
        
        # Create products from image files
        created_count = 0
        skipped_count = 0
        
        for idx, img_path in enumerate(image_files, 1):
            filename = img_path.stem  # Get filename without extension
            
            # Parse SKU: Format is CAT-BRA-NUMBER
            parts = filename.split('-')
            if len(parts) < 3:
                self.stdout.write(self.style.WARNING(f'⚠ Skipping invalid filename: {filename}'))
                skipped_count += 1
                continue
            
            cat_prefix = parts[0]
            brand_code = parts[1]
            sku_number = parts[2]
            
            # Get category
            if cat_prefix not in categories:
                self.stdout.write(self.style.WARNING(f'⚠ Unknown category: {cat_prefix}'))
                skipped_count += 1
                continue
            
            category = categories[cat_prefix]
            
            # Get brand name
            brand = brand_map.get(brand_code, brand_code)
            
            # Create SKU
            sku = f'{cat_prefix}-{brand_code}-{sku_number}'
            
            # Skip if product already exists
            if Product.objects.filter(sku=sku).exists():
                skipped_count += 1
                continue
            
            # Generate product name
            product_types = {
                'ELE': ['Smartphone', 'Laptop', 'Tablet', 'Watch', 'Earbuds', 'Monitor', 'Keyboard', 'Mouse'],
                'FAS': ['T-Shirt', 'Jeans', 'Shoes', 'Jacket', 'Hoodie', 'Shorts', 'Dress', 'Shirt'],
                'GRO': ['Milk', 'Bread', 'Biscuits', 'Rice', 'Oil', 'Tea', 'Coffee', 'Butter'],
                'HOM': ['Mixer', 'Cooker', 'Bottle', 'Lunch Box', 'Kettle', 'Toaster', 'Pan', 'Container'],
                'BOO': ['Notebook', 'Pen', 'Pencil', 'Eraser', 'Sharpener', 'Book', 'Diary', 'Markers'],
                'SPO': ['Football', 'Cricket Bat', 'Racket', 'Yoga Mat', 'Dumbbells', 'Rope', 'Ball', 'Shoes'],
                'BEA': ['Face Cream', 'Shampoo', 'Conditioner', 'Body Wash', 'Lotion', 'Face Wash', 'Lipstick', 'Sunscreen'],
                'TOY': ['Building Blocks', 'RC Car', 'Doll', 'Board Game', 'Puzzle', 'Action Figure', 'Soft Toy', 'Car Set']
            }
            
            product_type = random.choice(product_types.get(cat_prefix, ['Product']))
            variants = ['Pro', 'Max', 'Ultra', 'Plus', 'Lite', 'Air', 'Premium', 'Standard']
            variant = random.choice(variants)
            name = f'{brand} {product_type} {variant}'
            
            # Generate price based on category
            price_ranges = {
                'ELE': (5000, 150000),
                'FAS': (500, 15000),
                'GRO': (20, 2000),
                'HOM': (200, 12000),
                'BOO': (10, 2000),
                'SPO': (200, 15000),
                'BEA': (100, 3000),
                'TOY': (150, 8000)
            }
            price_range = price_ranges.get(cat_prefix, (100, 5000))
            price = Decimal(random.randint(price_range[0], price_range[1]))
            
            # Generate quantity
            stock_rand = random.random()
            if stock_rand < 0.7:
                quantity = random.randint(50, 500)
            elif stock_rand < 0.9:
                quantity = random.randint(1, 49)
            else:
                quantity = 0
            
            # Select supplier
            suppliers = ['ABC Distributors', 'XYZ Wholesale', 'Prime Suppliers', 'Elite Traders', 'Global Imports']
            supplier = random.choice(suppliers)
            
            # Create product with image
            image_path = f'products/{img_path.name}'
            
            try:
                product = Product.objects.create(
                    name=name,
                    sku=sku,
                    category=category,
                    description=f'High quality {product_type.lower()} from {brand}. {variant} variant.',
                    price=price,
                    quantity=quantity,
                    supplier=supplier,
                    image=image_path
                )
                
                # Create stock entry
                if quantity > 0:
                    StockEntry.objects.create(
                        product=product,
                        entry_type='IN',
                        quantity=quantity,
                        notes=f'Initial stock for {name}',
                        created_by=staff_user
                    )
                
                created_count += 1
                if idx % 100 == 0:
                    self.stdout.write(f'  ✓ Created {idx} products...')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error creating product for {filename}: {e}'))
                skipped_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('\n✅ PRODUCT CREATION COMPLETED!\n'))
        self.stdout.write(f'  ✓ Created:  {created_count} products')
        self.stdout.write(f'  ⊘ Skipped: {skipped_count} files')
        self.stdout.write(f'  Total:     {created_count + skipped_count} images processed')
        self.stdout.write(f'\n  ✨ All {created_count} products have matching images!')
        self.stdout.write('\n' + '='*70 + '\n')
