# This file defines the data shapes for API requests and responses using Pydantic.

from typing import List
from pydantic import BaseModel, Field

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
