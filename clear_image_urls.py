#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermart_project.settings')
django.setup()

from core.models import Product

# Clear image_url for all products
products = Product.objects.all()
count = 0

for product in products:
    if product.image_url:
        product.image_url = ''
        product.save(update_fields=['image_url'])
        count += 1

print(f"Cleared image_url for {count} products")
print(f"All products will now use local generated images")
