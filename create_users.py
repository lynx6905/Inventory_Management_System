#!/usr/bin/env python
"""Script to create users in the database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermart_project.settings')
django.setup()

from core.models import User

users_to_create = [
    {
        'email': 'admin@supermart.com',
        'username': 'admin',
        'first_name': 'Super',
        'last_name': 'Admin',
        'role': 'ADMIN',
        'phone': '9876543210',
        'password': 'admin123'
    },
    {
        'email': 'manager@supermart.com',
        'username': 'manager',
        'first_name': 'Store',
        'last_name': 'Manager',
        'role': 'MANAGER',
        'phone': '9876543211',
        'password': 'manager123'
    },
    {
        'email': 'staff@supermart.com',
        'username': 'staff',
        'first_name': 'Store',
        'last_name': 'Staff',
        'role': 'STAFF',
        'phone': '9876543212',
        'password': 'staff123'
    },
    {
        'email': 'customer@supermart.com',
        'username': 'customer',
        'first_name': 'John',
        'last_name': 'Doe',
        'role': 'CUSTOMER',
        'phone': '9876543213',
        'password': 'customer123'
    },
]

print("\n📝 Creating users in database...\n")

for user_data in users_to_create:
    password = user_data.pop('password')
    email = user_data['email']
    
    # Delete any existing users with this email (to avoid duplicates)
    deleted_count, _ = User.objects.filter(email=email).delete()
    if deleted_count > 0:
        print(f"  ⚠ Removed {deleted_count} duplicate user(s) with email: {email}")
    
    # Create new user
    user = User.objects.create_user(**user_data, password=password)
    print(f"  ✓ Created {user.role}: {user.email}")

print("\n✅ All users created successfully!")
print("\nLogin Credentials:")
print("  Admin:    admin@supermart.com / admin123")
print("  Manager:  manager@supermart.com / manager123")
print("  Staff:    staff@supermart.com / staff123")
print("  Customer: customer@supermart.com / customer123\n")
