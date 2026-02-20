import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermart_project.settings')
django.setup()

from core.models import Category, Product

print(f'Categories: {Category.objects.count()}')
print(f'Products: {Product.objects.count()}')
print(f'Categories: {list(Category.objects.values_list("name", flat=True))}')
print(f'Sample Products:')
for p in Product.objects.all()[:5]:
    print(f'  - {p.name} (Image: {p.image})')
