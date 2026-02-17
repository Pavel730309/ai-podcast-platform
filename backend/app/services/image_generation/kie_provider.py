"""
KIE.ai provider for image generation
"""
from typing import Optional, Dict, Any
import httpx
from app.services.image_generation.image_generator import ImageGenerator


class KIEImageProvider:
    """Service for generating podcast cover images using KIE.ai"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://kie.ai/api"
        self.default_generator = ImageGenerator()
    
    async def is_available(self) -> bool:
        """Check if KIE.ai API is available"""
        return bool(self.api_key)
    
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
        Generate a podcast cover image using KIE.ai
        
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
        if not self.api_key:
            # Fallback to default generator
            return await self.default_generator.generate_cover(
                title=title,
                description=description,
                style=style,
                color_scheme=color_scheme,
                width=width,
                height=height
            )
        
        try:
            # Call KIE.ai image generation API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": f"Podcast cover art for: {title}. Description: {description}. Style: {style}. Professional, modern design.",
                        "n": 1,
                        "size": "1024x1024",
                        "quality": "standard"
                    }
                )
                
                if response.status_code != 200:
                    # Fallback to default generator on error
                    return await self.default_generator.generate_cover(
                        title=title,
                        description=description,
                        style=style,
                        color_scheme=color_scheme,
                        width=width,
                        height=height
                    )
                
                data = response.json()
                image_url = data["data"][0]["url"]
                
                # Download the generated image
                async with httpx.AsyncClient() as download_client:
                    download_response = await download_client.get(image_url)
                    
                    if download_response.status_code == 200:
                        return download_response.content
                    else:
                        # Fallback to default generator
                        return await self.default_generator.generate_cover(
                            title=title,
                            description=description,
                            style=style,
                            color_scheme=color_scheme,
                            width=width,
                            height=height
                        )
                
        except Exception as e:
            # Fallback to default generator on error
            return await self.default_generator.generate_cover(
                title=title,
                description=description,
                style=style,
                color_scheme=color_scheme,
                width=width,
                height=height
            )
    
    async def generate_from_prompt(
        self,
        prompt: str,
        width: int = 1400,
        height: int = 1400,
        provider: str = "kie"
    ) -> bytes:
        """
        Generate image from text prompt using KIE.ai
        
        Args:
            prompt: Text description for image generation
            width: Image width
            height: Image height
            provider: AI provider to use
            
        Returns:
            Generated image as bytes
        """
        if not self.api_key:
            # Fallback to default generator
            return await self.default_generator.generate_from_prompt(
                prompt=prompt,
                width=width,
                height=height,
                provider=provider
            )
        
        try:
            # Call KIE.ai image generation API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": prompt,
                        "n": 1,
                        "size": "1024x1024",
                        "quality": "standard"
                    }
                )
                
                if response.status_code != 200:
                    # Fallback to default generator
                    return await self.default_generator.generate_from_prompt(
                        prompt=prompt,
                        width=width,
                        height=height,
                        provider=provider
                    )
                
                data = response.json()
                image_url = data["data"][0]["url"]
                
                # Download the generated image
                async with httpx.AsyncClient() as download_client:
                    download_response = await download_client.get(image_url)
                    
                    if download_response.status_code == 200:
                        return download_response.content
                    else:
                        # Fallback to default generator
                        return await self.default_generator.generate_from_prompt(
                            prompt=prompt,
                            width=width,
                            height=height,
                            provider=provider
                        )
                
        except Exception as e:
            # Fallback to default generator
            return await self.default_generator.generate_from_prompt(
                prompt=prompt,
                width=width,
                height=height,
                provider=provider
            )
    
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
        return await self.default_generator.resize_image(
            image_data=image_data,
            width=width,
            height=height,
            maintain_aspect_ratio=maintain_aspect_ratio
        )
    
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
        return await self.default_generator.add_border(
            image_data=image_data,
            border_width=border_width,
            border_color=border_color
        )
