import logging
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    pass
except ImportError:
    pass
except Exception as e:
    pass

from .gemini_routes import router as gemini_router
from .openai_routes import router as openai_router
from .google_api_client import get_google_api_client

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initializes the Google API client.
    """
    get_google_api_client()

# Add CORS middleware for preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.options("/{full_path:path}")
async def handle_preflight(request: Request, full_path: str):
    """Handle CORS preflight requests without authentication."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Root endpoint - no authentication required
@app.get("/")
async def root():
    """
    Root endpoint providing project information.
    No authentication required.
    """
    return {
        "name": "geminicli2api",
        "description": "OpenAI-compatible API proxy for Google's Gemini models via gemini-cli",
        "purpose": "Provides both OpenAI-compatible endpoints (/v1/chat/completions) and native Gemini API endpoints for accessing Google's Gemini models",
        "version": "1.0.0",
        "endpoints": {
            "openai_compatible": {
                "chat_completions": "/v1/chat/completions",
                "models": "/v1/models"
            },
            "native_gemini": {
                "models": "/v1beta/models",
                "generate": "/v1beta/models/{model}/generateContent",
                "stream": "/v1beta/models/{model}/streamGenerateContent"
            },
            "health": "/health"
        },
        "authentication": "Required for all endpoints except root and health",
        "repository": "https://github.com/user/geminicli2api"
    }

# Health check endpoint for Docker/Hugging Face
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "geminicli2api"}

app.include_router(openai_router)
app.include_router(gemini_router)