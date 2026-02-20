"""
Management command to populate product image URLs from Unsplash with proper product images
"""
from django.core.management.base import BaseCommand
from core.models import Product
import requests
from time import sleep
from urllib.parse import quote


class Command(BaseCommand):
    help = 'Populate product image_url from Unsplash with proper product images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of products to process'
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Replace existing image URLs'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.2,
            help='Delay between requests in seconds'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        replace = options['replace']
        delay = options['delay']
        
        self.stdout.write(self.style.SUCCESS('Populating product image URLs from Unsplash...'))
        
        # Category to search term mapping
        CATEGORY_KEYWORDS = {
            'Electronics': ['smartphone', 'laptop', 'tablet', 'smartwatch', 'headphones', 'monitor', 'keyboard', 'mouse', 'camera'],
            'Fashion': ['tshirt', 'jeans', 'shoes', 'jacket', 'dress', 'sneakers', 'boots', 'clothing'],
            'Groceries': ['vegetables', 'fruits', 'bread', 'milk', 'fresh food', 'organic produce'],
            'Home & Kitchen': ['kitchen', 'cookware', 'furniture', 'home decor', 'blender', 'mixer'],
            'Books & Stationery': ['books', 'notebook', 'pen', 'stationery', 'diary'],
            'Sports & Fitness': ['sports', 'fitness', 'gym', 'yoga', 'exercise', 'football'],
            'Beauty & Personal Care': ['cosmetics', 'skincare', 'beauty', 'perfume', 'lotion'],
            'Toys & Games': ['toys', 'games', 'puzzle', 'dolls', 'action figures'],
        }
        
        # Get products
        if replace:
            products = Product.objects.all()
            self.stdout.write(f'Processing all {products.count()} products...\n')
        else:
            products = Product.objects.filter(image_url='')
            self.stdout.write(f'Processing {products.count()} products without image URLs...\n')
        
        if limit:
            products = products[:limit]
            self.stdout.write(f'Limited to {limit} products\n')
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('No products to process.'))
            return
        
        success_count = 0
        error_count = 0
        
        self.stdout.write('\nStarting image fetch...\n')
        
        for i, product in enumerate(products, 1):
            try:
                # Skip if image_url exists and not replacing
                if product.image_url and not replace:
                    continue
                
                # Extract search term from product name and category
                search_term = self.get_search_term(product.name, product.category.name, CATEGORY_KEYWORDS)
                
                # Fetch image URL from Unsplash
                image_url = self.fetch_unsplash_image_url(search_term)
                
                if image_url:
                    product.image_url = image_url
                    product.save(update_fields=['image_url'])
                    success_count += 1
                    self.stdout.write(f'  ✓ {product.name} -> {search_term}')
                else:
                    error_count += 1
                    self.stdout.write(self.style.WARNING(f'  ✗ {product.name} -> {search_term} (failed)'))
                
                # Progress indicator
                if i % 20 == 0:
                    self.stdout.write(f'\n  Progress: [{i}/{products.count()}] Success: {success_count}, Errors: {error_count}\n')
                
                sleep(delay)
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'  Error: {product.name}: {str(e)}'))
        
        # Final summary
        self.stdout.write(f'\n\n========== SUMMARY ==========')
        self.stdout.write(self.style.SUCCESS(f'Success: {success_count}'))
        if error_count:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        self.stdout.write(f'Total Processed: {success_count + error_count}')
        self.stdout.write(f'=============================\n')

    def get_search_term(self, product_name, category_name, category_keywords):
        """
        Extract best search term from product name and category
        Returns the most specific search term for the product
        """
        product_lower = product_name.lower()
        
        # Get category keywords
        keywords = category_keywords.get(category_name, ['product'])
        
        # Try to find matching keywords in product name
        for keyword in keywords:
            if keyword.lower() in product_lower:
                return keyword
        
        # If no keyword matches, try to extract brand and product name
        # E.g., "Sony Mouse Lite" -> "Sony mouse"
        parts = product_name.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}".lower()
        
        # Fall back to first category keyword with product name
        return f"{parts[0]} {keywords[0]}".lower() if parts else keywords[0]

    def fetch_unsplash_image_url(self, search_term, width=800, height=600):
        """
        Fetch image URL from Unsplash Source API
        Returns the direct image URL
        """
        try:
            # Use Unsplash Source API - returns a redirect to actual image
            # Format: https://source.unsplash.com/[width]x[height]/?[search-term]
            url = f'https://source.unsplash.com/{width}x{height}/?{quote(search_term)}'
            
            # For Unsplash Source, the URL itself is the image URL
            # No need to make a request to validate - the URL is static based on search term
            return url
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error fetching from Unsplash: {e}'))
        
        return None

