#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermart_project.settings')
django.setup()

from core.models import Product
from django.conf import settings

print("=" * 70)
print("IMAGE FIELD DEBUG")
print("=" * 70)

product = Product.objects.first()

print(f"\nProduct: {product.name}")
print(f"Image field type: {type(product.image)}")
print(f"Image field value: {product.image}")
print(f"Image field repr: {repr(product.image)}")

# Try to access .url
try:
    url = product.image.url
    print(f"Image .url: {url}")
except Exception as e:
    print(f"Error accessing .url: {e}")

# Check what URLs should look like
print(f"\nMEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

# Check if file exists
if product.image:
    full_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
    print(f"Full path: {full_path}")
    print(f"File exists: {os.path.exists(full_path)}")

print("\n" + "=" * 70 + "\n")
