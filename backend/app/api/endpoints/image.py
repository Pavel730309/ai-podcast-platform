"""
API endpoints for image generation
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import uuid
from pathlib import Path
import io

from app.schemas import FileUploadResponse
from app.services.image_generation import ImageGenerator

router = APIRouter(prefix="/image", tags=["image"])

# Initialize service
image_generator = ImageGenerator()


@router.post("/generate", response_model=FileUploadResponse)
async def generate_cover(
    title: str,
    description: Optional[str] = None,
    style: str = "modern",
    width: int = 1400,
    height: int = 1400
):
    """
    Generate podcast cover image
    
    - **title**: Podcast title
    - **description**: Podcast description
    - **style**: Cover style (modern, classic, vibrant)
    - **width**: Image width
    - **height**: Image height
    """
    try:
        # Generate image
        image_data = await image_generator.generate_cover(
            title=title,
            description=description or "",
            style=style,
            width=width,
            height=height
        )
        
        # Save to file
        image_id = str(uuid.uuid4())
        image_dir = Path("uploads/images")
        image_dir.mkdir(parents=True, exist_ok=True)
        
        image_file = image_dir / f"{image_id}.png"
        with open(image_file, "wb") as f:
            f.write(image_data)
        
        return FileUploadResponse(
            file_id=image_id,
            filename=f"cover_{image_id}.png",
            file_type="png",
            file_size=len(image_data)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover: {str(e)}")


@router.post("/generate-from-prompt", response_model=FileUploadResponse)
async def generate_cover_from_prompt(
    prompt: str,
    width: int = 1400,
    height: int = 1400
):
    """
    Generate cover from text prompt using AI
    
    - **prompt**: Text description for image
    - **width**: Image width
    - **height**: Image height
    """
    try:
        # Generate image from prompt
        image_data = await image_generator.generate_from_prompt(
            prompt=prompt,
            width=width,
            height=height
        )
        
        # Save to file
        image_id = str(uuid.uuid4())
        image_dir = Path("uploads/images")
        image_dir.mkdir(parents=True, exist_ok=True)
        
        image_file = image_dir / f"{image_id}.png"
        with open(image_file, "wb") as f:
            f.write(image_data)
        
        return FileUploadResponse(
            file_id=image_id,
            filename=f"generated_{image_id}.png",
            file_type="png",
            file_size=len(image_data)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover from prompt: {str(e)}")


@router.post("/resize", response_model=FileUploadResponse)
async def resize_image(
    image_file: UploadFile = File(...),
    width: int = 1400,
    height: int = 1400,
    maintain_aspect_ratio: bool = True
):
    """
    Resize an image
    
    - **image_file**: Image file to resize
    - **width**: Target width
    - **height**: Target height
    - **maintain_aspect_ratio**: Whether to maintain aspect ratio
    """
    try:
        # Read image data
        image_data = await image_file.read()
        
        # Resize image
        resized_image = await image_generator.resize_image(
            image_data,
            width,
            height,
            maintain_aspect_ratio
        )
        
        # Save to file
        image_id = str(uuid.uuid4())
        image_dir = Path("uploads/images")
        image_dir.mkdir(parents=True, exist_ok=True)
        
        image_file = image_dir / f"{image_id}_resized.png"
        with open(image_file, "wb") as f:
            f.write(resized_image)
        
        return FileUploadResponse(
            file_id=image_id,
            filename=f"resized_{image_id}.png",
            file_type="png",
            file_size=len(resized_image)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resizing image: {str(e)}")


@router.post("/add-border", response_model=FileUploadResponse)
async def add_border(
    image_file: UploadFile = File(...),
    border_width: int = 20,
    border_color: str = "#FFFFFF"
):
    """
    Add border to image
    
    - **image_file**: Image file to add border to
    - **border_width**: Border width in pixels
    - **border_color**: Border color in hex format
    """
    try:
        # Read image data
        image_data = await image_file.read()
        
        # Convert hex color to RGB tuple
        if border_color.startswith('#'):
            border_color_rgb = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
        else:
            border_color_rgb = (255, 255, 255)  # Default white
        
        # Add border
        bordered_image = await image_generator.add_border(
            image_data,
            border_width,
            border_color_rgb
        )
        
        # Save to file
        image_id = str(uuid.uuid4())
        image_dir = Path("uploads/images")
        image_dir.mkdir(parents=True, exist_ok=True)
        
        image_file = image_dir / f"{image_id}_bordered.png"
        with open(image_file, "wb") as f:
            f.write(bordered_image)
        
        return FileUploadResponse(
            file_id=image_id,
            filename=f"bordered_{image_id}.png",
            file_type="png",
            file_size=len(bordered_image)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding border: {str(e)}")
