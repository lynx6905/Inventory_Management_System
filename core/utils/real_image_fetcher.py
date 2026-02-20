"""
Utility to fetch real product images from free stock photo services
"""
import os
import requests
import hashlib
from pathlib import Path
from time import sleep
from urllib.parse import quote


class RealImageFetcher:
    """Fetch real product images from Unsplash Source and other free services"""
    
    # Category to search term mapping for better image results
    CATEGORY_SEARCH_TERMS = {
        'Electronics': [
            'smartphone', 'laptop', 'tablet', 'smartwatch', 'headphones',
            'monitor', 'keyboard', 'mouse', 'camera', 'speaker'
        ],
        'Fashion': [
            'tshirt', 'jeans', 'shoes', 'jacket', 'dress',
            'sneakers', 'boots', 'hoodie', 'clothing', 'fashion'
        ],
        'Groceries': [
            'vegetables', 'fruits', 'bread', 'milk', 'food',
            'grocery', 'organic food', 'fresh produce', 'pantry', 'snacks'
        ],
        'Home & Kitchen': [
            'kitchen appliances', 'cookware', 'utensils', 'home decor', 'furniture',
            'mixer', 'blender', 'pots', 'pans', 'home'
        ],
        'Books & Stationery': [
            'books', 'notebook', 'pen', 'stationery', 'office supplies',
            'diary', 'pencil', 'study', 'writing', 'reading'
        ],
        'Sports & Fitness': [
            'sports equipment', 'fitness', 'gym', 'yoga', 'exercise',
            'football', 'basketball', 'workout', 'athletic', 'sports'
        ],
        'Beauty & Personal Care': [
            'cosmetics', 'skincare', 'beauty products', 'makeup', 'perfume',
            'lotion', 'shampoo', 'beauty', 'personal care', 'wellness'
        ],
        'Toys & Games': [
            'toys', 'games', 'kids toys', 'board games', 'puzzles',
            'dolls', 'action figures', 'play', 'children toys', 'fun'
        ],
    }
    
    def __init__(self, media_root, use_service='unsplash'):
        """
        Initialize the image fetcher
        
        Args:
            media_root: Path to media directory
            use_service: Which service to use ('unsplash', 'picsum', 'placeholder')
        """
        self.media_root = Path(media_root)
        self.products_dir = self.media_root / 'products'
        self.products_dir.mkdir(parents=True, exist_ok=True)
        self.use_service = use_service
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_search_term(self, product_name, category_name):
        """Extract best search term from product name and category"""
        # Try to match product type from name
        product_lower = product_name.lower()
        
        # Get category search terms
        category_terms = self.CATEGORY_SEARCH_TERMS.get(category_name, ['product'])
        
        # Check if any category term appears in product name
        for term in category_terms:
            if term.lower() in product_lower:
                return term
        
        # Otherwise return first category term
        return category_terms[0] if category_terms else category_name.lower()
    
    def fetch_unsplash_image(self, search_term, width=800, height=800):
        """
        Fetch image from Unsplash Source (no API key needed)
        
        Args:
            search_term: What to search for
            width: Image width
            height: Image height
            
        Returns:
            bytes: Image data or None
        """
        try:
            # Unsplash Source API - free, no auth required
            url = f'https://source.unsplash.com/{width}x{height}/?{quote(search_term)}'
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return response.content
            
        except Exception as e:
            print(f"Error fetching from Unsplash: {e}")
        
        return None
    
    def fetch_picsum_image(self, width=800, height=800, seed=None):
        """
        Fetch image from Lorem Picsum (random photos)
        
        Args:
            width: Image width
            height: Image height
            seed: Seed for consistent random image
            
        Returns:
            bytes: Image data or None
        """
        try:
            if seed:
                url = f'https://picsum.photos/seed/{seed}/{width}/{height}'
            else:
                url = f'https://picsum.photos/{width}/{height}'
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return response.content
                
        except Exception as e:
            print(f"Error fetching from Picsum: {e}")
        
        return None
    
    def fetch_placeholder_image(self, text, width=800, height=800, category_name=''):
        """
        Fetch image from placeholder service with text
        
        Args:
            text: Text to display
            width: Image width
            height: Image height
            category_name: Category for color selection
            
        Returns:
            bytes: Image data or None
        """
        try:
            # placehold.co - clean placeholder service
            # Choose color based on category
            colors = {
                'Electronics': '3B82F6',  # Blue
                'Fashion': 'EC4899',      # Pink
                'Groceries': '10B981',    # Green
                'Home & Kitchen': 'EF4444',  # Red
                'Books & Stationery': '8B5CF6',  # Purple
                'Sports & Fitness': 'F59E0B',  # Amber
                'Beauty & Personal Care': 'F472B6',  # Pink
                'Toys & Games': 'F97316',  # Orange
            }
            color = colors.get(category_name, '6B7280')
            
            encoded_text = quote(text[:50])  # Limit text length
            url = f'https://placehold.co/{width}x{height}/{color}/white?text={encoded_text}'
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.content
                
        except Exception as e:
            print(f"Error fetching placeholder: {e}")
        
        return None
    
    def download_and_save_image(self, product_name, category_name, sku):
        """
        Download and save a real product image
        
        Args:
            product_name: Name of the product
            category_name: Category name
            sku: Product SKU
            
        Returns:
            str: Relative path to saved image or None
        """
        # Create filename from SKU
        filename = f"{sku.replace('/', '-')}.jpg"
        filepath = self.products_dir / filename
        
        # If file already exists, skip
        if filepath.exists():
            return f'products/{filename}'
        
        # Get search term
        search_term = self.get_search_term(product_name, category_name)
        
        # Try to fetch image based on selected service
        image_data = None
        
        if self.use_service == 'unsplash':
            image_data = self.fetch_unsplash_image(search_term)
            
        elif self.use_service == 'picsum':
            # Use SKU as seed for consistent images
            seed = hashlib.md5(sku.encode()).hexdigest()[:8]
            image_data = self.fetch_picsum_image(seed=seed)
        
        elif self.use_service == 'placeholder':
            # Truncate product name for display
            display_name = product_name[:30] + '...' if len(product_name) > 30 else product_name
            image_data = self.fetch_placeholder_image(display_name, category_name=category_name)
        
        # If fetch failed, try placeholder as fallback
        if not image_data:
            print(f"Failed to fetch image for {product_name}, using placeholder")
            display_name = product_name[:30] + '...' if len(product_name) > 30 else product_name
            image_data = self.fetch_placeholder_image(display_name, category_name=category_name)
        
        # Save image if we got data
        if image_data:
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                return f'products/{filename}'
            except Exception as e:
                print(f"Error saving image for {product_name}: {e}")
        
        return None
    
    def close(self):
        """Close the session"""
        self.session.close()
