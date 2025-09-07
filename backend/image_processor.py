"""
Advanced Image Processing Module for Local Storage Optimization

This module provides comprehensive image processing capabilities including:
- Image compression and optimization
- Multiple variant generation (thumbnail, medium, large)
- Format conversion and optimization
- File validation and security checks
- Background processing for performance
"""

import os
import asyncio
from pathlib import Path
from typing import Tuple, Optional, Dict, List
from PIL import Image, ImageOps
from PIL.ExifTags import ORIENTATION
import hashlib
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Advanced image processor for local storage optimization"""
    
    # Image size configurations
    SIZES = {
        'thumbnail': (150, 150),
        'small': (300, 300), 
        'medium': (600, 600),
        'large': (1200, 1200),
        'original': None  # Keep original size
    }
    
    # Quality settings for different variants
    QUALITY_SETTINGS = {
        'thumbnail': 85,
        'small': 85,
        'medium': 90,
        'large': 92,
        'original': 95
    }
    
    # Supported formats and their optimal use cases
    SUPPORTED_FORMATS = {
        'JPEG': {'extensions': ['.jpg', '.jpeg'], 'quality_range': (75, 95)},
        'PNG': {'extensions': ['.png'], 'supports_transparency': True},
        'WEBP': {'extensions': ['.webp'], 'quality_range': (75, 95), 'modern': True}
    }
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_uploaded_image(
        self, 
        file_content: bytes, 
        filename: str, 
        entity_type: str,
        generate_variants: bool = True,
        optimize: bool = True
    ) -> Dict[str, str]:
        """
        Process an uploaded image with optimization and variant generation
        
        Args:
            file_content: Raw image bytes
            filename: Original filename
            entity_type: Type of entity (team, brand, player, etc.)
            generate_variants: Whether to generate multiple size variants
            optimize: Whether to apply optimization
            
        Returns:
            Dictionary containing paths to all generated variants
        """
        try:
            # Create entity-specific directory
            entity_dir = self.upload_dir / f"{entity_type}s"
            entity_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate base filename
            base_filename = self._generate_filename(filename, entity_type)
            
            # Open and validate image
            image = Image.open(io.BytesIO(file_content))
            image = self._fix_image_orientation(image)
            
            # Validate image
            self._validate_image(image)
            
            # Prepare results dictionary
            results = {}
            
            if generate_variants:
                # Generate multiple variants
                for size_name, dimensions in self.SIZES.items():
                    variant_path = await self._create_image_variant(
                        image, size_name, dimensions, entity_dir, base_filename, optimize
                    )
                    results[size_name] = f"uploads/{entity_type}s/{variant_path.name}"
            else:
                # Just optimize the original
                optimized_path = await self._save_optimized_image(
                    image, entity_dir, base_filename, optimize
                )
                results['original'] = f"uploads/{entity_type}s/{optimized_path.name}"
            
            # Generate image metadata
            metadata = self._extract_image_metadata(image, file_content)
            results['metadata'] = metadata
            
            logger.info(f"Successfully processed image: {base_filename}")
            return results
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
    
    def _generate_filename(self, original_filename: str, entity_type: str) -> str:
        """Generate a unique, SEO-friendly filename"""
        # Extract original extension
        original_ext = Path(original_filename).suffix.lower()
        
        # Use webp for optimization, fallback to jpg
        extension = '.webp' if self._supports_webp() else '.jpg'
        
        # Generate unique identifier
        timestamp = int(datetime.now().timestamp())
        unique_id = uuid.uuid4().hex[:8]
        
        return f"{entity_type}_{unique_id}_{timestamp}{extension}"
    
    def _supports_webp(self) -> bool:
        """Check if WebP format is supported"""
        try:
            Image.new('RGB', (1, 1)).save(io.BytesIO(), 'WEBP')
            return True
        except:
            return False
    
    def _fix_image_orientation(self, image: Image.Image) -> Image.Image:
        """Fix image orientation based on EXIF data"""
        try:
            if hasattr(image, '_getexif'):
                exif = image._getexif()
                if exif is not None:
                    orientation = exif.get(ORIENTATION)
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        except:
            # If EXIF processing fails, continue with original image
            pass
        
        return image
    
    def _validate_image(self, image: Image.Image) -> None:
        """Validate image properties and content"""
        # Check image dimensions
        max_dimension = 4096  # 4K max
        min_dimension = 32    # Minimum viable size
        
        width, height = image.size
        
        if max(width, height) > max_dimension:
            raise ValueError(f"Image too large: {width}x{height}. Max dimension: {max_dimension}px")
        
        if min(width, height) < min_dimension:
            raise ValueError(f"Image too small: {width}x{height}. Min dimension: {min_dimension}px")
        
        # Check if image has content (not just transparent/empty)
        if image.mode in ('RGBA', 'LA'):
            # For images with transparency, check if there's visible content
            if image.getbbox() is None:
                raise ValueError("Image appears to be empty or fully transparent")
    
    async def _create_image_variant(
        self, 
        image: Image.Image, 
        size_name: str, 
        dimensions: Optional[Tuple[int, int]], 
        output_dir: Path, 
        base_filename: str,
        optimize: bool = True
    ) -> Path:
        """Create a specific size variant of the image"""
        
        # Create the variant
        if dimensions and size_name != 'original':
            # Resize maintaining aspect ratio
            variant_image = self._resize_image(image, dimensions, size_name)
        else:
            variant_image = image.copy()
        
        # Generate variant filename
        name_parts = base_filename.rsplit('.', 1)
        variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
        variant_path = output_dir / variant_filename
        
        # Save with optimization
        await self._save_image_with_optimization(
            variant_image, variant_path, size_name, optimize
        )
        
        return variant_path
    
    def _resize_image(self, image: Image.Image, target_size: Tuple[int, int], size_name: str) -> Image.Image:
        """Resize image maintaining aspect ratio with different strategies"""
        
        if size_name == 'thumbnail':
            # For thumbnails, use crop to fill exact dimensions
            return ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
        else:
            # For other sizes, maintain aspect ratio
            image_copy = image.copy()
            image_copy.thumbnail(target_size, Image.Resampling.LANCZOS)
            return image_copy
    
    async def _save_image_with_optimization(
        self, 
        image: Image.Image, 
        file_path: Path, 
        size_name: str,
        optimize: bool = True
    ) -> None:
        """Save image with format-specific optimizations"""
        
        # Determine output format from extension
        extension = file_path.suffix.lower()
        
        # Convert RGBA to RGB if saving as JPEG
        if extension in ['.jpg', '.jpeg'] and image.mode in ('RGBA', 'LA'):
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
            else:
                background.paste(image)
            image = background
        
        # Get quality setting
        quality = self.QUALITY_SETTINGS.get(size_name, 85)
        
        # Save with format-specific options
        save_kwargs = {'optimize': optimize}
        
        if extension == '.webp':
            save_kwargs.update({
                'format': 'WEBP',
                'quality': quality,
                'method': 6  # Better compression
            })
        elif extension in ['.jpg', '.jpeg']:
            save_kwargs.update({
                'format': 'JPEG',
                'quality': quality,
                'progressive': True  # Progressive JPEG for better loading
            })
        elif extension == '.png':
            save_kwargs.update({
                'format': 'PNG',
                'optimize': True
            })
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the image
        image.save(str(file_path), **save_kwargs)
    
    async def _save_optimized_image(
        self, 
        image: Image.Image, 
        output_dir: Path, 
        filename: str,
        optimize: bool = True
    ) -> Path:
        """Save single optimized image"""
        file_path = output_dir / filename
        await self._save_image_with_optimization(image, file_path, 'original', optimize)
        return file_path
    
    def _extract_image_metadata(self, image: Image.Image, file_content: bytes) -> Dict:
        """Extract useful metadata from the image"""
        width, height = image.size
        
        # Calculate file size
        file_size = len(file_content)
        
        # Calculate aspect ratio
        aspect_ratio = round(width / height, 2) if height > 0 else 1.0
        
        # Determine if image is landscape, portrait, or square
        orientation = 'square'
        if width > height * 1.1:
            orientation = 'landscape'
        elif height > width * 1.1:
            orientation = 'portrait'
        
        return {
            'width': width,
            'height': height,
            'format': image.format,
            'mode': image.mode,
            'file_size': file_size,
            'aspect_ratio': aspect_ratio,
            'orientation': orientation,
            'has_transparency': image.mode in ('RGBA', 'LA', 'P')
        }
    
    async def cleanup_old_images(self, entity_type: str, days_old: int = 30) -> int:
        """Clean up old, unused images to free up storage space"""
        entity_dir = self.upload_dir / f"{entity_type}s"
        
        if not entity_dir.exists():
            return 0
        
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
        cleaned_count = 0
        
        try:
            for file_path in entity_dir.iterdir():
                if file_path.is_file():
                    # Check file modification time
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        return cleaned_count
    
    def get_image_variants(self, image_url: str) -> Dict[str, str]:
        """Get all available variants for a given image URL"""
        if not image_url:
            return {}
        
        # Parse the original URL
        path_parts = image_url.split('/')
        if len(path_parts) < 3:
            return {'original': image_url}
        
        directory = '/'.join(path_parts[:-1])
        filename = path_parts[-1]
        
        # Remove size suffix if present
        name_parts = filename.rsplit('_', 1)
        if len(name_parts) == 2 and name_parts[1].split('.')[0] in self.SIZES:
            base_filename = name_parts[0]
            extension = '.' + filename.split('.')[-1]
        else:
            base_filename = filename.rsplit('.', 1)[0]
            extension = '.' + filename.split('.')[-1]
        
        # Generate variant URLs
        variants = {}
        for size_name in self.SIZES.keys():
            variant_filename = f"{base_filename}_{size_name}{extension}"
            variant_url = f"{directory}/{variant_filename}"
            
            # Check if variant file exists
            variant_path = Path(variant_url)
            if variant_path.exists():
                variants[size_name] = variant_url
        
        # If no variants found, return original
        if not variants:
            variants['original'] = image_url
            
        return variants

# Global processor instance
image_processor = ImageProcessor()

# Import io at module level
import io