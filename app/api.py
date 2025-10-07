# This file defines the API routes/endpoints.

from fastapi import APIRouter, File, UploadFile

# Import the core logic functions from the services module
from . import services

# Import the Pydantic models from the schemas module
from .schemas import AnalysisResponse, TextRequest

# Create a new router object. This helps in modularizing the API.
router = APIRouter()

@router.post("/detect-from-image", response_model=AnalysisResponse)
async def detect_from_image(file: UploadFile = File(..., description="An image file (e.g., receipt, invoice).")):
    """
    Processes an image to extract and classify financial amounts.
    """
    image_bytes = await file.read()
    
    # Step 1: Perform OCR using the service function
    raw_text = services.extract_text_from_image(image_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="OCR could not detect any text in the image.")
    
    # Step 2: Analyze the extracted text using the service function
    return services.analyze_text_for_amounts(raw_text)


@router.post("/detect-from-text", response_model=AnalysisResponse)
async def detect_from_text(request: TextRequest):
    """
    Processes a raw text string to extract and classify financial amounts.
    """
    # Directly call the core analysis service function
    return services.analyze_text_for_amounts(request.text)
