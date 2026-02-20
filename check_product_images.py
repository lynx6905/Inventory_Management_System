#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermart_project.settings')
django.setup()

from core.models import Product

print("=" * 70)
print("PRODUCT IMAGES CHECK")
print("=" * 70)

products = Product.objects.all()[:10]

print(f"\nTotal Products: {Product.objects.count()}")
print(f"\nSample Products with Images:")

for i, product in enumerate(products, 1):
    print(f"\n{i}. {product.name}")
    print(f"   SKU: {product.sku}")
    print(f"   Image: {product.image}")
    print(f"   Category: {product.category.name}")

# Check for products without images
no_image = Product.objects.filter(image='').count()
print(f"\n\nProducts without images: {no_image}")
print(f"Products with images: {Product.objects.exclude(image='').count()}")

print("\n" + "=" * 70 + "\n")
