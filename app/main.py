# This is the main entry point of the application.

from fastapi import FastAPI

# Import the router from the api module
from .api import router

# Create the FastAPI app instance
app = FastAPI(
    title="AI-Powered Amount Detection API",
    description="Extracts financial amounts from images and text.",
    version="1.0.0",
)

# Include the API router.
# All routes defined in app/api.py will now be part of the application.
# We also add a prefix, which is a good practice for versioning.
app.include_router(router, prefix="/api/v1", tags=["Detection"])

# A simple root endpoint for health checks
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API is running"}
