import io
import re
from typing import List, Optional

import pytesseract
import spacy
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel, Field

# --- 1. Application and Model Initialization ---
# These objects are created once when the application starts up,
# making the API efficient as we don't reload models on every request.

app = FastAPI(
    title="AI-Powered Amount Detection API",
    description="Extracts financial amounts from images and text.",
    version="1.0.0",
)

# Load the spaCy NLP model. This is a powerful, pre-trained model.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- 2. Pydantic Models (API Data Shapes) ---
# These models define the structure of the API's inputs and outputs.
# FastAPI uses them for automatic validation and documentation.

class Amount(BaseModel):
    type: str = Field(..., description="The classified type of the amount (e.g., 'total_bill', 'paid', 'due').")
    value: float = Field(..., description="The numeric value of the amount.")
    source_text: str = Field(..., description="The original text snippet from which the amount was extracted.")

class AnalysisResponse(BaseModel):
    currency: str = Field(default="INR", description="The detected or default currency.")
    amounts: List[Amount] = Field(..., description="A list of all detected amounts.")
    status: str = Field(default="ok", description="The status of the analysis.")

class TextRequest(BaseModel):
    text: str = Field(..., description="The raw text to be analyzed.", example="Invoice Total: 5000 INR. Paid amount 2000, balance due is 3000.")

# --- 3. Core Logic (The "Brain") ---
# This is the central function that performs the analysis.
# It's kept separate to abide by the DRY principle, as both API endpoints use it.

def analyze_text_for_amounts(text: str) -> AnalysisResponse:
    """
    Analyzes a raw text string to find and classify financial amounts using spaCy.
    """
    doc = nlp(text)
    matcher = spacy.matcher.Matcher(nlp.vocab)

    # Define patterns to find keywords near numbers. This is more robust
    # as it looks for numbers before or after the keyword.
    pattern = [
        {"LOWER": {"IN": ["total", "paid", "due", "balance", "amount"]}, "OP": "?"},
        {"IS_PUNCT": True, "OP": "?"},
        {"LIKE_NUM": True},
        {"LOWER": {"IN": ["total", "paid", "due", "balance", "amount"]}, "OP": "?"},
    ]
    matcher.add("AmountPattern", [pattern])

    matches = matcher(doc)
    
    found_amounts = []
    # Use a set to avoid processing the same text span multiple times
    processed_spans = set()

    for _, start, end in matches:
        span = doc[start:end]
        
        if span.text in processed_spans:
            continue
        processed_spans.add(span.text)

        amount_type = "unknown"
        value = None

        # Extract the type and numeric value from the matched text
        for token in span:
            if token.lower_ in ["total", "balance"]:
                amount_type = "total_bill" if token.lower_ == "total" else "due"
            elif token.lower_ in ["paid", "due"]:
                amount_type = token.lower_
            
            if token.like_num:
                # Clean the token text to get a pure number string, then convert to float
                cleaned_num = re.sub(r"[^0-9.]", "", token.text)
                if cleaned_num:
                    value = float(cleaned_num)
        
        if amount_type != "unknown" and value is not None:
            found_amounts.append(Amount(
                type=amount_type,
                value=value,
                source_text=span.text
            ))
            
    if not found_amounts:
        raise HTTPException(
            status_code=404, 
            detail="No classifiable amounts were found in the provided text."
        )

    return AnalysisResponse(amounts=found_amounts)

# --- 4. Helper Functions ---

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Performs OCR on an image provided as bytes.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        # Raise an HTTP exception if the image is invalid or processing fails
        raise HTTPException(status_code=400, detail=f"Image processing failed: {e}")

# --- 5. API Endpoints (The "Controllers") ---

@app.post("/detect-from-image", response_model=AnalysisResponse, tags=["Detection"])
async def detect_from_image(file: UploadFile = File(..., description="An image file (e.g., receipt, invoice).")):
    """
    Processes an image to extract and classify financial amounts.
    This is the full OCR -> NLP pipeline.
    """
    image_bytes = await file.read()
    
    # Step 1: Perform OCR
    raw_text = extract_text_from_image(image_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="OCR could not detect any text in the image.")
    
    # Step 2: Analyze the extracted text (reusing the core logic)
    return analyze_text_for_amounts(raw_text)


@app.post("/detect-from-text", response_model=AnalysisResponse, tags=["Detection"])
async def detect_from_text(request: TextRequest):
    """
    Processes a raw text string to extract and classify financial amounts.
    This endpoint gives direct access to the NLP analysis logic.
    """
    # Directly call the core analysis function
    return analyze_text_for_amounts(request.text)