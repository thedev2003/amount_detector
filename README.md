Project: AI-Powered Amount Detection (PLUM Task 8)This project is a Python-based backend service that extracts and classifies financial amounts (total, paid, due) from text or images of medical documents, as per the assignment guidelines.ArchitectureThe service follows a clean, modular architecture:API Layer (FastAPI): A high-performance web server receives HTTP requests. It uses Pydantic for data validation and generates interactive documentation automatically.OCR Module (pytesseract): For image requests, the service uses the Tesseract-OCR engine to convert the image into a raw text string.NLP Module (spaCy): The core logic resides here. Text is processed by spaCy, and a rule-based Matcher identifies keywords (total, paid, due) in proximity to numbers to classify them. This approach is efficient and doesn't require model training.Shared Logic: Both the image and text endpoints funnel into a single analyze_text_for_amounts function, ensuring that the core logic is not repeated (DRY principle).Local Setup and InstallationTo run this project locally, please follow these steps:Prerequisites:Python 3.8+Google's Tesseract-OCR engine.Create Project Folder: Create a folder named amount_detector and place the main.py and requirements.txt files inside it.Setup Virtual Environment (in VS Code Terminal):# Navigate into your project folder
cd amount_detector

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
Install Dependencies:pip install -r requirements.txt
Run the Server:uvicorn main:app --reload
The API will now be live and accessible at http://127.0.0.1:8000.API Usage & Testing with PostmanYou can test the API using the interactive documentation automatically generated at http://127.0.0.1:8000/docs or by using Postman with the following sample cases.Test Case 1: Text InputEndpoint: POST /detect-from-textMethod: POSTIn Postman, set the body to raw and type to JSON.Request Body:{
  "text": "Your total bill is 4500.00 INR. Amount paid: 2000. The amount due is now 2500."
}
Expected Response (200 OK):{
    "currency": "INR",
    "amounts": [
        {
            "type": "total_bill",
            "value": 4500.0,
            "source_text": "total bill is 4500.00"
        },
        {
            "type": "paid",
            "value": 2000.0,
            "source_text": "paid: 2000"
        },
        {
            "type": "due",
            "value": 2500.0,
            "source_text": "due is now 2500"
        }
    ],
    "status": "ok"
}
Test Case 2: Handwritten Note ImageEndpoint: POST /detect-from-imageMethod: POSTIn Postman, set the body to form-data.Add a new key, change its type from "Text" to "File", and select your test image.Sample Image:Create a simple image file named test_note.png with text like this (handwritten style fonts work well for testing):Total: 2500Paid - 1000Due = 1500Disclaimer: Tesseract's accuracy with real, messy handwriting can be low. For testing, use a clear, digitally created image with a handwriting-style font for best results.Expected Response (200 OK):{
    "currency": "INR",
    "amounts": [
        {
            "type": "total_bill",
            "value": 2500.0,
            "source_text": "Total: 2500"
        },
        {
            "type": "paid",
            "value": 1000.0,
            "source_text": "Paid - 1000"
        },
        {
            "type": "due",
            "value": 1500.0,
            "source_text": "Due = 1500"
        }
    ],
    "status": "ok"
}
Known Issues & ImprovementsIssue: Tesseract OCR struggles with poor quality images, complex layouts, and messy handwriting.Improvement: Integrate a cloud-based OCR service (like Google Vision AI) for higher accuracy.Improvement: Train a custom spaCy NER (Named Entity Recognition) model to recognize amounts and their context more accurately than the current rule-based matcher.
  @media print {
    .ms-editor-squiggler {
        display:none !important;
    }
  }
  .ms-editor-squiggler {
    all: initial;
    display: block !important;
    height: 0px !important;
    width: 0px !important;
  }