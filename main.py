from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.routers import email_analysis, notifications, voice, config
from app.core.email_processor import EmailProcessor
from app.core.scheduler import EmailScheduler
from app.core.database import init_db

load_dotenv()

app = FastAPI(
    title="Intelligent Email Agent API",
    description="""
    ## Intelligent Email Agent

    A comprehensive API for intelligent email analysis, categorization, and management.

    ### Features
    - **Email Processing**: Connect to IMAP servers and process emails with AI analysis
    - **Smart Categorization**: Automatically categorize emails by type, urgency, and priority
    - **AI-Powered Summaries**: Generate intelligent summaries and follow-up suggestions
    - **Multi-Channel Notifications**: Send alerts via Slack, Telegram, and WhatsApp
    - **Voice Summaries**: Convert email summaries to speech using TTS
    - **VIP Management**: Prioritize emails from important contacts
    - **Automated Scheduling**: Daily summaries and response reminders

    ### Getting Started
    1. Configure your email settings using the `/api/config/configuration` endpoints
    2. Add VIP contacts for priority handling
    3. Process emails using `/api/email/process-emails`
    4. Set up notifications and voice preferences
    5. View daily summaries and manage your inbox intelligently

    ### Authentication
    This API uses email credentials for IMAP access. Ensure your email provider supports IMAP and has app passwords enabled for secure access.

    ### Rate Limits
    - Email processing: 10 requests per minute
    - Notifications: 50 requests per minute  
    - Voice generation: 20 requests per minute
    - Configuration: 100 requests per minute

    ### Support
    For issues and feature requests, please contact support@emailagent.com
    """,
    version="1.0.0",
    contact={
        "name": "Email Agent Support",
        "email": "support@emailagent.com",
        "url": "https://github.com/emailagent/support"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Email Analysis",
            "description": "Process, analyze, and manage emails with AI-powered insights",
        },
        {
            "name": "Notifications", 
            "description": "Send notifications across multiple channels (Slack, Telegram, WhatsApp)",
        },
        {
            "name": "Voice",
            "description": "Generate voice summaries using text-to-speech technology",
        },
        {
            "name": "Configuration",
            "description": "Manage system settings, email configurations, and VIP contacts",
        },
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(email_analysis.router)
app.include_router(notifications.router)
app.include_router(voice.router)
app.include_router(config.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks on startup"""
    await init_db()
    # Start the email scheduler
    scheduler = EmailScheduler()
    scheduler.start()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/v1/analyze-now")
async def analyze_emails_now(background_tasks: BackgroundTasks):
    """Trigger immediate email analysis"""
    try:
        processor = EmailProcessor()
        background_tasks.add_task(processor.process_inbox)
        return {"message": "Email analysis started", "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 