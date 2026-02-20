"""
Utility to generate beautiful product placeholder images
"""
from PIL import Image, ImageDraw, ImageFont
import os
import random
from pathlib import Path


class ProductImageGenerator:
    """Generate attractive product placeholder images with gradients and text"""
    
    # Category-specific color schemes (gradient pairs)
    CATEGORY_COLORS = {
        'Electronics': [
            ((30, 58, 138), (59, 130, 246)),  # Blue gradient
            ((55, 48, 163), (129, 140, 248)),  # Indigo gradient
            ((17, 24, 39), (75, 85, 99)),     # Dark gray gradient
        ],
        'Fashion': [
            ((219, 39, 119), (244, 114, 182)),  # Pink gradient
            ((157, 23, 77), (236, 72, 153)),    # Rose gradient
            ((124, 58, 237), (196, 181, 253)),  # Purple gradient
        ],
        'Groceries': [
            ((22, 163, 74), (134, 239, 172)),   # Green gradient
            ((217, 119, 6), (253, 186, 116)),   # Orange gradient
            ((190, 18, 60), (251, 113, 133)),   # Rose-red gradient
        ],
        'Home & Kitchen': [
            ((225, 29, 72), (248, 113, 113)),   # Red gradient
            ((194, 65, 12), (251, 146, 60)),    # Orange gradient
            ((161, 98, 7), (250, 204, 21)),     # Amber gradient
        ],
        'Books & Stationery': [
            ((109, 40, 217), (167, 139, 250)),  # Violet gradient
            ((79, 70, 229), (165, 180, 252)),   # Indigo gradient
            ((6, 95, 70), (110, 231, 183)),     # Teal gradient
        ],
        'Sports & Fitness': [
            ((220, 38, 38), (252, 165, 165)),   # Red gradient
            ((234, 88, 12), (253, 186, 116)),   # Orange gradient
            ((4, 120, 87), (52, 211, 153)),     # Emerald gradient
        ],
        'Beauty & Personal Care': [
            ((236, 72, 153), (251, 207, 232)),  # Pink gradient
            ((168, 85, 247), (233, 213, 255)),  # Purple gradient
            ((251, 113, 133), (254, 205, 211)), # Rose gradient
        ],
        'Toys & Games': [
            ((249, 115, 22), (254, 215, 170)),  # Orange gradient
            ((236, 72, 153), (251, 207, 232)),  # Pink gradient
            ((14, 165, 233), (186, 230, 253)),  # Sky gradient
        ],
    }
    
    def __init__(self, media_root):
        """Initialize the image generator"""
        self.media_root = Path(media_root)
        self.products_dir = self.media_root / 'products'
        self.products_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to load a font, fall back to default if not available
        self.font_large = None
        self.font_small = None
        try:
            # Try common font paths
            font_paths = [
                'C:/Windows/Fonts/Arial.ttf',
                'C:/Windows/Fonts/arialbd.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/System/Library/Fonts/Helvetica.ttc',
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.font_large = ImageFont.truetype(font_path, 48)
                    self.font_small = ImageFont.truetype(font_path, 24)
                    break
        except Exception:
            pass  # Use default font
    
    def create_gradient(self, width, height, color_start, color_end):
        """Create a vertical gradient image"""
        base = Image.new('RGB', (width, height), color_start)
        top = Image.new('RGB', (width, height), color_end)
        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base
    
    def generate_product_image(self, product_name, category_name, sku):
        """Generate a beautiful product image with gradient and text"""
        width, height = 800, 800
        
        # Get color scheme for category
        colors = self.CATEGORY_COLORS.get(category_name, [
            ((107, 114, 128), (209, 213, 219))  # Default gray gradient
        ])
        color_start, color_end = random.choice(colors)
        
        # Create gradient background
        image = self.create_gradient(width, height, color_start, color_end)
        draw = ImageDraw.Draw(image)
        
        # Add decorative shapes
        # Top-right circle
        circle_color = tuple(min(255, c + 30) for c in color_end)
        draw.ellipse([width-300, -100, width+100, 300], fill=circle_color)
        
        # Bottom-left circle with transparency effect
        circle_color2 = tuple(max(0, c - 30) for c in color_start)
        draw.ellipse([-100, height-300, 300, height+100], fill=circle_color2)
        
        # Add subtle pattern lines
        line_color = tuple(min(255, c + 20) for c in color_start)
        for i in range(0, width, 80):
            draw.line([(i, 0), (i + height, height)], fill=line_color, width=2)
        
        # Prepare text
        # Truncate product name if too long
        display_name = product_name
        if len(display_name) > 30:
            display_name = display_name[:27] + '...'
        
        # Split name into multiple lines if needed
        words = display_name.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 20:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw category badge
        category_badge_height = 60
        badge_color = tuple(max(0, c - 40) for c in color_start)
        draw.rectangle([0, 0, width, category_badge_height], fill=badge_color)
        
        # Draw category text
        if self.font_small:
            bbox = draw.textbbox((0, 0), category_name, font=self.font_small)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, 18), category_name, 
                     fill=(255, 255, 255), font=self.font_small)
        else:
            draw.text((width // 2 - 50, 20), category_name, fill=(255, 255, 255))
        
        # Draw product name (centered, multiple lines)
        start_y = height // 2 - (len(lines) * 60) // 2
        for i, line in enumerate(lines):
            if self.font_large:
                bbox = draw.textbbox((0, 0), line, font=self.font_large)
                text_width = bbox[2] - bbox[0]
                text_x = (width - text_width) // 2
            else:
                text_x = width // 2 - len(line) * 10
            
            # Draw shadow
            shadow_color = tuple(max(0, c - 50) for c in color_start)
            if self.font_large:
                draw.text((text_x + 3, start_y + i * 60 + 3), line, 
                         fill=shadow_color, font=self.font_large)
                draw.text((text_x, start_y + i * 60), line, 
                         fill=(255, 255, 255), font=self.font_large)
            else:
                draw.text((text_x + 2, start_y + i * 60 + 2), line, 
                         fill=shadow_color)
                draw.text((text_x, start_y + i * 60), line, 
                         fill=(255, 255, 255))
        
        # Draw SKU at bottom
        sku_y = height - 80
        if self.font_small:
            bbox = draw.textbbox((0, 0), f"SKU: {sku}", font=self.font_small)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, sku_y), f"SKU: {sku}", 
                     fill=(255, 255, 255, 200), font=self.font_small)
        else:
            draw.text((width // 2 - 60, sku_y), f"SKU: {sku}", 
                     fill=(255, 255, 255))
        
        # Add a subtle border
        border_color = tuple(min(255, c + 40) for c in color_end)
        draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=4)
        
        return image
    
    def save_product_image(self, product_name, category_name, sku):
        """Generate and save a product image, return the relative path"""
        # Create safe filename from SKU
        filename = f"{sku.replace('/', '-')}.jpg"
        filepath = self.products_dir / filename
        
        # Generate image
        image = self.generate_product_image(product_name, category_name, sku)
        
        # Save with high quality
        image.save(filepath, 'JPEG', quality=90, optimize=True)
        
        # Return relative path for Django models
        return f'products/{filename}'
