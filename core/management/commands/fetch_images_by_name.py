"""
Management command to fetch product images based on product names
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Product
from core.utils.real_image_fetcher import RealImageFetcher
from time import sleep


class Command(BaseCommand):
    help = 'Fetch real product images from free stock photo services based on product name'

    def add_arguments(self, parser):
        parser.add_argument(
            '--service',
            type=str,
            default='unsplash',
            choices=['unsplash', 'picsum', 'placeholder'],
            help='Which service to use for images (default: unsplash)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of products to process'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay between requests in seconds (default: 0.5)'
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Replace existing images'
        )
        parser.add_argument(
            '--no-matching',
            action='store_true',
            help='Skip products that already have matching images'
        )

    def handle(self, *args, **options):
        service = options['service']
        limit = options['limit']
        delay = options['delay']
        replace = options['replace']
        skip_matching = options['no_matching']
        
        self.stdout.write(self.style.SUCCESS(f'\n🖼️  Fetching images by product name from {service.upper()}...'))
        self.stdout.write(f'Delay between requests: {delay}s\n')
        
        # Initialize image fetcher
        fetcher = RealImageFetcher(settings.MEDIA_ROOT, use_service=service)
        
        # Get products
        if replace:
            products = Product.objects.all()
            self.stdout.write(f'Processing all {products.count()} products (replacing existing)...\n')
        else:
            products = Product.objects.all()
            self.stdout.write(f'Processing {products.count()} products...\n')
        
        if limit:
            products = products[:limit]
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('No products to process.'))
            fetcher.close()
            return
        
        # Fetch images
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        self.stdout.write('Starting download...\n')
        
        for i, product in enumerate(products, 1):
            try:
                # Skip if already has image and not replacing
                if not replace and product.image and not skip_matching:
                    skipped_count += 1
                    if i % 20 == 0:
                        self.stdout.write(f'  [{i}/{products.count()}] Skipped: {skipped_count}')
                    continue
                
                # Fetch and save image based on product name
                image_path = fetcher.download_and_save_image(
                    product.name,
                    product.category.name,
                    f'{product.sku}_by_name'  # Use name-based filename
                )
                
                if image_path:
                    # Update product
                    product.image = image_path
                    product.save(update_fields=['image'])
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ {product.name}')
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ✗ Failed to fetch: {product.name}')
                    )
                
                # Progress indicator
                if i % 20 == 0:
                    self.stdout.write(
                        f'\n  Progress: [{i}/{products.count()}] '
                        f'Success: {success_count}, Errors: {error_count}, Skipped: {skipped_count}\n'
                    )
                
                # Rate limiting
                if delay > 0 and i < products.count():
                    sleep(delay)
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error processing {product.name}: {str(e)}')
                )
        
        # Close session
        fetcher.close()
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS(f'\n✅ IMAGE FETCH COMPLETED!\n'))
        self.stdout.write(f'Service used: {service.upper()}')
        self.stdout.write(f'Total products processed: {products.count()}')
        self.stdout.write(self.style.SUCCESS(f'Successfully fetched: {success_count}'))
        if skipped_count > 0:
            self.stdout.write(f'Skipped (already have images): {skipped_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        total_with_images = Product.objects.filter(image__gt='').count()
        total_products = Product.objects.count()
        match_percentage = (total_with_images / total_products * 100) if total_products > 0 else 0
        
        self.stdout.write(f'\n📊 Total products with images: {total_with_images}/{total_products} ({match_percentage:.1f}%)')
        self.stdout.write('\n' + '='*70 + '\n')
