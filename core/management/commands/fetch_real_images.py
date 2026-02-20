"""
Management command to fetch real product images from stock photo services
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Product
from core.utils.real_image_fetcher import RealImageFetcher
from time import sleep


class Command(BaseCommand):
    help = 'Fetch real product images from free stock photo services'

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

    def handle(self, *args, **options):
        service = options['service']
        limit = options['limit']
        delay = options['delay']
        replace = options['replace']
        
        self.stdout.write(self.style.SUCCESS(f'Fetching real product images from {service.upper()}...'))
        self.stdout.write(f'Delay between requests: {delay}s\n')
        
        # Initialize image fetcher
        fetcher = RealImageFetcher(settings.MEDIA_ROOT, use_service=service)
        
        # Get products
        if replace:
            products = Product.objects.all()
            self.stdout.write(f'Processing all {products.count()} products...\n')
        else:
            products = Product.objects.filter(image='')
            self.stdout.write(f'Processing {products.count()} products without images...\n')
        
        if limit:
            products = products[:limit]
            self.stdout.write(f'Limited to {limit} products\n')
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('No products to process.'))
            fetcher.close()
            return
        
        # Fetch images
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        self.stdout.write('\nStarting download...\n')
        
        for i, product in enumerate(products, 1):
            try:
                # Skip if image exists and not replacing
                if product.image and not replace:
                    skipped_count += 1
                    continue
                
                # Fetch and save image
                image_path = fetcher.download_and_save_image(
                    product.name,
                    product.category.name,
                    product.sku
                )
                
                if image_path:
                    # Update product
                    product.image = image_path
                    product.save(update_fields=['image'])
                    success_count += 1
                    
                    # Progress indicator
                    if i % 10 == 0:
                        self.stdout.write(
                            f'  [{i}/{products.count()}] Downloaded images... '
                            f'(Success: {success_count}, Errors: {error_count})'
                        )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ✗ Failed to fetch image for: {product.name}')
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
        self.stdout.write(self.style.SUCCESS(f'\n✅ IMAGE DOWNLOAD COMPLETED!\n'))
        self.stdout.write(f'Service used: {service.upper()}')
        self.stdout.write(f'Total products processed: {products.count()}')
        self.stdout.write(self.style.SUCCESS(f'Successfully downloaded: {success_count}'))
        if skipped_count > 0:
            self.stdout.write(f'Skipped (already have images): {skipped_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        self.stdout.write('\n' + '='*70)
        
        # Service-specific notes
        if service == 'unsplash':
            self.stdout.write('\n📸 Using Unsplash Source - high quality stock photos')
            self.stdout.write('   Images are category-relevant and professionally shot')
        elif service == 'picsum':
            self.stdout.write('\n📸 Using Lorem Picsum - random beautiful photos')
            self.stdout.write('   Images are consistent per product (same SKU = same image)')
        elif service == 'placeholder':
            self.stdout.write('\n📸 Using placeholder service - clean colored backgrounds')
            self.stdout.write('   Category-specific colors with product names')
        
        self.stdout.write('\n')
