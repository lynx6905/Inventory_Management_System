"""
Management command to generate simple product images based on product names
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Product
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


class Command(BaseCommand):
    help = 'Generate simple product images based on product names'

    # Category-specific colors for better visual appeal
    CATEGORY_COLORS = {
        'Electronics': {
            'bg': (41, 128, 185),      # Blue
            'accent': (52, 152, 219),
            'text': (255, 255, 255)
        },
        'Fashion': {
            'bg': (231, 76, 60),        # Red
            'accent': (192, 57, 43),
            'text': (255, 255, 255)
        },
        'Groceries': {
            'bg': (46, 204, 113),       # Green
            'accent': (39, 174, 96),
            'text': (255, 255, 255)
        },
        'Home & Kitchen': {
            'bg': (149, 165, 166),      # Gray
            'accent': (127, 140, 141),
            'text': (255, 255, 255)
        },
        'Books & Stationery': {
            'bg': (155, 89, 182),       # Purple
            'accent': (142, 68, 173),
            'text': (255, 255, 255)
        },
        'Sports & Fitness': {
            'bg': (230, 126, 34),       # Orange
            'accent': (211, 84, 0),
            'text': (255, 255, 255)
        },
        'Beauty & Personal Care': {
            'bg': (236, 100, 75),       # Coral
            'accent': (203, 67, 53),
            'text': (255, 255, 255)
        },
        'Toys & Games': {
            'bg': (52, 211, 153),       # Teal
            'accent': (16, 185, 129),
            'text': (255, 255, 255)
        },
    }

    # Product type keywords to extract from product names
    PRODUCT_KEYWORDS = {
        'Electronics': ['mouse', 'keyboard', 'laptop', 'monitor', 'smartphone', 'tablet', 'headphones', 'speaker', 'camera', 'smartwatch', 'earbuds', 'webcam'],
        'Fashion': ['shirt', 'jeans', 'shoes', 'jacket', 'dress', 'sneakers', 'boots', 'hoodie', 'coat', 'pants'],
        'Groceries': ['fruit', 'vegetable', 'bread', 'milk', 'cheese', 'cereal', 'snack', 'juice', 'coffee', 'tea'],
        'Home & Kitchen': ['blender', 'toaster', 'mixer', 'kettle', 'pan', 'pot', 'utensil', 'furniture', 'lamp', 'chair'],
        'Books & Stationery': ['book', 'notebook', 'pen', 'pencil', 'diary', 'stationery', 'paper', 'marker', 'desk'],
        'Sports & Fitness': ['ball', 'yoga', 'dumbbell', 'bicycle', 'racket', 'equipment', 'mat', 'weights', 'shoes'],
        'Beauty & Personal Care': ['lotion', 'shampoo', 'cream', 'perfume', 'soap', 'cosmetics', 'skincare', 'makeup'],
        'Toys & Games': ['toy', 'game', 'puzzle', 'doll', 'action', 'board', 'card', 'lego'],
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerate images for all products, even those with existing images'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of products to process'
        )

    def get_category_colors(self, category_name):
        """Get colors for a category, default to blue if not found"""
        return self.CATEGORY_COLORS.get(category_name, {
            'bg': (52, 73, 94),
            'accent': (44, 62, 80),
            'text': (255, 255, 255)
        })

    def extract_product_type(self, product_name, category_name):
        """Extract product type from product name"""
        product_lower = product_name.lower()
        
        # Try to find a matching keyword
        keywords = self.PRODUCT_KEYWORDS.get(category_name, [])
        for keyword in keywords:
            if keyword in product_lower:
                return keyword.title()
        
        # Extract first meaningful word
        words = product_name.split()
        if words:
            return words[0]
        return "Product"

    def create_product_image(self, product, image_path):
        """Create a simple product image"""
        try:
            # Get category colors
            colors = self.get_category_colors(product.category.name)
            bg_color = colors['bg']
            accent_color = colors['accent']
            text_color = colors['text']
            
            # Create image
            width, height = 400, 400
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Draw accent bar
            bar_height = 60
            draw.rectangle([(0, 0), (width, bar_height)], fill=accent_color)
            
            # Try to use a nice font, fall back to default
            try:
                title_font = ImageFont.truetype("arial.ttf", 32)
                subtitle_font = ImageFont.truetype("arial.ttf", 20)
                product_font = ImageFont.truetype("arial.ttf", 28)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                product_font = ImageFont.load_default()
            
            # Draw product type in accent bar
            product_type = self.extract_product_type(product.name, product.category.name)
            type_bbox = draw.textbbox((0, 0), product_type, font=title_font)
            type_width = type_bbox[2] - type_bbox[0]
            type_x = (width - type_width) // 2
            draw.text((type_x, 12), product_type, fill=text_color, font=title_font)
            
            # Draw category
            cat_bbox = draw.textbbox((0, 0), product.category.name, font=subtitle_font)
            cat_width = cat_bbox[2] - cat_bbox[0]
            cat_x = (width - cat_width) // 2
            draw.text((cat_x, height - 80), product.category.name, fill=accent_color, font=subtitle_font)
            
            # Draw product name (main content)
            # Wrap text if needed
            product_name = product.name
            if len(product_name) > 25:
                # Truncate and add ellipsis
                product_name = product_name[:25] + "..."
            
            name_bbox = draw.textbbox((0, 0), product_name, font=product_font)
            name_width = name_bbox[2] - name_bbox[0]
            name_x = (width - name_width) // 2
            draw.text((name_x, height // 2 - 30), product_name, fill=text_color, font=product_font)
            
            # Draw decorative elements (dots)
            dot_radius = 15
            dot_color = accent_color
            
            # Left dot
            draw.ellipse(
                [(30, height // 2 - dot_radius), (30 + dot_radius * 2, height // 2 + dot_radius)],
                fill=dot_color
            )
            
            # Right dot
            draw.ellipse(
                [(width - 30 - dot_radius * 2, height // 2 - dot_radius), (width - 30, height // 2 + dot_radius)],
                fill=dot_color
            )
            
            # Draw SKU at bottom
            sku_text = f"SKU: {product.sku}"
            sku_bbox = draw.textbbox((0, 0), sku_text, font=subtitle_font)
            sku_width = sku_bbox[2] - sku_bbox[0]
            sku_x = (width - sku_width) // 2
            draw.text((sku_x, height - 30), sku_text, fill=(150, 150, 150), font=subtitle_font)
            
            # Save image
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            img.save(image_path, 'JPEG', quality=90)
            
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating image: {str(e)}'))
            return False

    def handle(self, *args, **options):
        regenerate_all = options['all']
        limit = options.get('limit')
        
        self.stdout.write(self.style.SUCCESS('\n🎨 Generating product images based on product names...\n'))
        
        # Get products
        if regenerate_all:
            products = Product.objects.all()
            self.stdout.write(f'Regenerating images for all {products.count()} products...\n')
        else:
            products = Product.objects.all()
            self.stdout.write(f'Generating images for {products.count()} products...\n')
        
        if limit:
            products = products[:limit]
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('No products to process.'))
            return
        
        success_count = 0
        error_count = 0
        
        media_root = Path(settings.MEDIA_ROOT)
        
        for i, product in enumerate(products, 1):
            try:
                # Create filename based on SKU
                image_filename = f'{product.sku}_generated.jpg'
                image_path = media_root / 'products' / image_filename
                image_url = f'products/{image_filename}'
                
                # Create image
                full_path = str(image_path)
                if self.create_product_image(product, full_path):
                    # Update product
                    product.image = image_url
                    product.save(update_fields=['image'])
                    success_count += 1
                else:
                    error_count += 1
                
                # Progress indicator
                if i % 25 == 0:
                    self.stdout.write(f'  ✓ Generated {i}/{products.count()} images...')
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error generating image for {product.name}: {str(e)}')
                )
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS(f'\n✅ IMAGE GENERATION COMPLETED!\n'))
        self.stdout.write(f'Successfully generated: {success_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        total_with_images = Product.objects.filter(image__gt='').count()
        total_products = Product.objects.count()
        match_percentage = (total_with_images / total_products * 100) if total_products > 0 else 0
        
        self.stdout.write(f'\n📊 Total products with images: {total_with_images}/{total_products} ({match_percentage:.1f}%)')
        self.stdout.write('\n' + '='*70 + '\n')
        self.stdout.write(self.style.SUCCESS('✨ All product images have been generated and are ready to display!\n'))
