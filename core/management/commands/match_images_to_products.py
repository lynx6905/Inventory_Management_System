"""
Management command to match product images with products based on SKU names
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Product
from pathlib import Path


class Command(BaseCommand):
    help = 'Match product images to products based on SKU filenames'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verify-only',
            action='store_true',
            help='Only show what would be matched without making changes'
        )

    def handle(self, *args, **options):
        verify_only = options['verify_only']
        
        self.stdout.write(self.style.SUCCESS('\n🖼️  Starting image-to-product matching...\n'))
        
        # Get media path
        media_products_path = Path(settings.MEDIA_ROOT) / 'products'
        
        if not media_products_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Media products folder not found: {media_products_path}'))
            return
        
        # Get all available images
        available_images = {}
        for ext in ['*.jpg', '*.png', '*.jpeg']:
            for img_path in media_products_path.glob(ext):
                sku = img_path.stem  # Filename without extension
                available_images[sku] = f'products/{img_path.name}'
        
        self.stdout.write(f'📁 Found {len(available_images)} images in media/products/\n')
        
        # Get all products
        all_products = Product.objects.all()
        self.stdout.write(f'📦 Found {all_products.count()} products in database\n')
        
        # Match images to products
        matched = 0
        already_matched = 0
        not_found = 0
        skipped = 0
        
        for product in all_products:
            sku = product.sku
            
            if sku in available_images:
                image_path = available_images[sku]
                
                # Check if already has correct image
                if product.image and product.image.name == image_path:
                    already_matched += 1
                    self.stdout.write(f'  ✓ Already matched: {sku}')
                else:
                    if verify_only:
                        self.stdout.write(f'  → Would match: {sku} → {image_path}')
                        matched += 1
                    else:
                        product.image = image_path
                        product.save()
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Matched: {sku} → {image_path}'))
                        matched += 1
            else:
                not_found += 1
                self.stdout.write(self.style.WARNING(f'  ⚠ No image found for SKU: {sku}'))
        
        # Summary
        self.stdout.write('\n' + '='*70)
        
        if verify_only:
            self.stdout.write(self.style.WARNING('\n📋 VERIFY MODE - No changes made\n'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ MATCHING COMPLETED!\n'))
        
        self.stdout.write(f'  Newly Matched:     {matched}')
        self.stdout.write(f'  Already Matched:   {already_matched}')
        self.stdout.write(f'  Images Not Found:  {not_found}')
        self.stdout.write(f'  Total Products:    {all_products.count()}')
        self.stdout.write(f'  Total Images:      {len(available_images)}')
        
        total_matched = matched + already_matched
        match_percentage = (total_matched / all_products.count() * 100) if all_products.count() > 0 else 0
        self.stdout.write(f'\n  ✨ Match Rate: {match_percentage:.1f}% ({total_matched}/{all_products.count()})')
        
        self.stdout.write('\n' + '='*70 + '\n')
        
        if not_found > 0:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Note: {not_found} products have no matching images.'))
            self.stdout.write('  These products might need images generated or manually assigned.\n')
