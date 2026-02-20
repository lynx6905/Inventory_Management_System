#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermart_project.settings')
django.setup()

from core.models import Product

prods = Product.objects.all()
print(f'Total products: {prods.count()}')
print()

for p in prods[:20]:
    img_status = p.image.name if p.image else "None"
    print(f'{p.name} (SKU: {p.sku}) - Image: {img_status}')
