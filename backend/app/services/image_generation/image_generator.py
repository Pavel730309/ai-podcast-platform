"""
Image generation service for podcast covers
"""
import os
import io
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

from app.config import settings


class ImageGenerator:
    """Service for generating podcast cover images"""
    
    def __init__(self):
        self.default_font_size = 36
        self.default_font_color = (255, 255, 255)  # White
        self.default_bg_color = (30, 30, 30)  # Dark gray
        self.supported_formats = ['png', 'jpg', 'jpeg']
    
    async def generate_cover(
        self,
        title: str,
        description: str = "",
        style: str = "modern",
        color_scheme: Optional[Dict[str, Any]] = None,
        width: int = 1400,
        height: int = 1400
    ) -> bytes:
        """
        Generate a podcast cover image
        
        Args:
            title: Podcast title
            description: Podcast description
            style: Cover style (modern, classic, vibrant)
            color_scheme: Custom color scheme
            width: Image width
            height: Image height
            
        Returns:
            Generated image as bytes
        """
        try:
            # Create base image
            img = Image.new('RGB', (width, height), color=color_scheme.get('background', self.default_bg_color) if color_scheme else self.default_bg_color)
            draw = ImageDraw.Draw(img)
            
            # Load font (try to use system font)
            font = None
            try:
                # Try to load a system font
                font_path = self._get_font_path()
                if font_path:
                    font = ImageFont.truetype(font_path, self.default_font_size)
            except:
                # Fallback to default font
                pass
            
            if not font:
                font = ImageFont.load_default()
            
            # Calculate text positions
            title_bbox = draw.textbbox((0, 0), title, font=font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            # Draw title
            title_x = (width - title_width) // 2
            title_y = (height - title_height) // 3
            draw.text((title_x, title_y), title, fill=color_scheme.get('text', self.default_font_color) if color_scheme else self.default_font_color, font=font)
            
            # Draw description if provided
            if description:
                desc_font = ImageFont.load_default()  # Smaller font for description
                desc_bbox = draw.textbbox((0, 0), description, font=desc_font)
                desc_width = desc_bbox[2] - desc_bbox[0]
                desc_x = (width - desc_width) // 2
                desc_y = title_y + title_height + 30
                draw.text((desc_x, desc_y), description, fill=color_scheme.get('text', self.default_font_color) if color_scheme else self.default_font_color, font=desc_font)
            
            # Add decorative elements based on style
            self._add_decorative_elements(draw, img.size, style)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Error generating cover image: {str(e)}")
    
    async def generate_from_prompt(
        self,
        prompt: str,
        width: int = 1400,
        height: int = 1400,
        provider: str = "dalle"
    ) -> bytes:
        """
        Generate image from text prompt using AI provider
        
        Args:
            prompt: Text description for image generation
            width: Image width
            height: Image height
            provider: AI provider to use
            
        Returns:
            Generated image as bytes
        """
        # For now, we'll return a placeholder - in real implementation this would integrate with AI APIs
        # like DALL-E, Stable Diffusion, etc.
        
        # Placeholder implementation
        img = Image.new('RGB', (width, height), color=(50, 50, 50))
        draw = ImageDraw.Draw(img)
        
        # Draw placeholder text
        draw.text((50, 50), f"AI Generated: {prompt[:50]}...", fill=(255, 255, 255))
        draw.text((50, 100), f"Width: {width}px, Height: {height}px", fill=(200, 200, 200))
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
    
    async def resize_image(
        self,
        image_data: bytes,
        width: int,
        height: int,
        maintain_aspect_ratio: bool = True
    ) -> bytes:
        """
        Resize an image
        
        Args:
            image_data: Image data as bytes
            width: Target width
            height: Target height
            maintain_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            Resized image as bytes
        """
        try:
            # Load image
            img = Image.open(io.BytesIO(image_data))
            
            # Resize
            if maintain_aspect_ratio:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Error resizing image: {str(e)}")
    
    async def add_border(
        self,
        image_data: bytes,
        border_width: int = 20,
        border_color: tuple = (255, 255, 255)
    ) -> bytes:
        """
        Add border to image
        
        Args:
            image_data: Image data as bytes
            border_width: Border width in pixels
            border_color: Border color tuple (R, G, B)
            
        Returns:
            Image with border as bytes
        """
        try:
            # Load image
            img = Image.open(io.BytesIO(image_data))
            
            # Create bordered image
            bordered_img = Image.new('RGB', (img.width + 2*border_width, img.height + 2*border_width), border_color)
            bordered_img.paste(img, (border_width, border_width))
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            bordered_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Error adding border: {str(e)}")
    
    def _get_font_path(self) -> Optional[str]:
        """Get system font path (platform dependent)"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            return "C:/Windows/Fonts/arial.ttf"
        elif system == "Darwin":  # macOS
            return "/System/Library/Fonts/Arial.ttf"
        else:  # Linux
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    def _add_decorative_elements(self, draw, size, style: str):
        """Add decorative elements based on style"""
        width, height = size
        
        if style == "modern":
            # Add subtle geometric shapes
            draw.rectangle([width//4, height//4, width//2, height//2], outline=(100, 100, 100), width=2)
        elif style == "classic":
            # Add subtle gradient effect
            pass
        elif style == "vibrant":
            # Add colorful circles
            draw.ellipse([width//6, height//6, width//3, height//3], fill=(255, 100, 100))
            draw.ellipse([2*width//3, 2*height//3, 5*width//6, 5*height//6], fill=(100, 255, 100))
