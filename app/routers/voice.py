from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any
import os
import tempfile
from gtts import gTTS
from pydub import AudioSegment
import uuid

from app.models import VoiceSummaryRequest
from app.core.database import db

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate")
async def generate_voice_summary(request: VoiceSummaryRequest):
    """Generate voice summary from text"""
    try:
        # Get summary from database
        summary = db.get_daily_summary(request.summary_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        # Generate text content
        text_content = _generate_summary_text(summary)
        
        # Generate audio file
        audio_file_path = await _generate_audio(text_content, request.voice_type, request.speed)
        
        # Return audio file
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename=f"email_summary_{request.summary_id}.mp3"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/daily-summary")
async def generate_daily_voice_summary(
    date: str,
    voice_type: str = "en-US",
    speed: float = 1.0
):
    """Generate voice summary for daily emails"""
    try:
        # Get emails for the date
        emails = db.get_emails_by_date(date)
        
        if not emails:
            raise HTTPException(status_code=404, detail="No emails found for this date")
        
        # Generate text content
        text_content = _generate_daily_summary_text(emails, date)
        
        # Generate audio file
        audio_file_path = await _generate_audio(text_content, voice_type, speed)
        
        # Return audio file
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename=f"daily_summary_{date}.mp3"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/urgent-alert")
async def generate_urgent_voice_alert(
    voice_type: str = "en-US",
    speed: float = 1.0
):
    """Generate voice alert for urgent emails"""
    try:
        # Get today's urgent emails
        today = datetime.now().strftime('%Y-%m-%d')
        emails = db.get_emails_by_date(today)
        
        urgent_emails = [
            e for e in emails 
            if e['priority'] in ['high', 'urgent'] or e['urgency_score'] >= 0.7
        ]
        
        if not urgent_emails:
            raise HTTPException(status_code=404, detail="No urgent emails found")
        
        # Generate text content
        text_content = _generate_urgent_alert_text(urgent_emails)
        
        # Generate audio file
        audio_file_path = await _generate_audio(text_content, voice_type, speed)
        
        # Return audio file
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename=f"urgent_alert_{today}.mp3"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom")
async def generate_custom_voice(
    text: str,
    voice_type: str = "en-US",
    speed: float = 1.0
):
    """Generate voice from custom text"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Generate audio file
        audio_file_path = await _generate_audio(text, voice_type, speed)
        
        # Return audio file
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename=f"custom_voice_{uuid.uuid4().hex[:8]}.mp3"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_audio(text: str, voice_type: str, speed: float) -> str:
    """Generate audio file from text"""
    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex}.mp3")
        
        # Generate speech
        tts = gTTS(text=text, lang=voice_type, slow=False)
        tts.save(temp_file)
        
        # Adjust speed if needed
        if speed != 1.0:
            audio = AudioSegment.from_mp3(temp_file)
            # Speed up or slow down
            if speed > 1.0:
                # Speed up
                audio = audio.speedup(playback_speed=speed)
            else:
                # Slow down
                audio = audio.speedup(playback_speed=speed)
            
            audio.export(temp_file, format="mp3")
        
        return temp_file
        
    except Exception as e:
        raise Exception(f"Error generating audio: {str(e)}")

def _generate_summary_text(summary: Dict[str, Any]) -> str:
    """Generate text content from summary"""
    text = f"Email Summary for {summary.get('date', 'today')}. "
    text += f"You received {summary.get('total_emails', 0)} emails. "
    
    # Add category breakdown
    categories = summary.get('categories', {})
    if categories:
        text += "Emails are categorized as: "
        category_list = [f"{count} {cat}" for cat, count in categories.items()]
        text += ", ".join(category_list) + ". "
    
    # Add urgent emails
    urgent_emails = summary.get('urgent_emails', [])
    if urgent_emails:
        text += f"There are {len(urgent_emails)} urgent emails that need your attention. "
    
    # Add unread emails
    unread_emails = summary.get('unread_emails', [])
    if unread_emails:
        text += f"You have {len(unread_emails)} unread emails. "
    
    # Add response reminders
    response_reminders = summary.get('response_reminders', [])
    if response_reminders:
        text += f"There are {len(response_reminders)} emails that need responses. "
    
    return text

def _generate_daily_summary_text(emails: list, date: str) -> str:
    """Generate text content for daily email summary"""
    if not emails:
        return f"No emails found for {date}."
    
    text = f"Daily email summary for {date}. "
    text += f"You received {len(emails)} emails. "
    
    # Count categories
    categories = {}
    urgent_count = 0
    unread_count = 0
    
    for email in emails:
        category = email.get('category', 'other')
        categories[category] = categories.get(category, 0) + 1
        
        if email.get('priority') in ['high', 'urgent'] or email.get('urgency_score', 0) >= 0.7:
            urgent_count += 1
        
        if not email.get('is_read', False):
            unread_count += 1
    
    # Add category breakdown
    if categories:
        text += "Emails are categorized as: "
        category_list = [f"{count} {cat}" for cat, count in categories.items()]
        text += ", ".join(category_list) + ". "
    
    # Add urgent emails
    if urgent_count > 0:
        text += f"There are {urgent_count} urgent emails that need your attention. "
    
    # Add unread emails
    if unread_count > 0:
        text += f"You have {unread_count} unread emails. "
    
    return text

def _generate_urgent_alert_text(urgent_emails: list) -> str:
    """Generate text content for urgent email alert"""
    if not urgent_emails:
        return "No urgent emails found."
    
    text = f"Urgent email alert. You have {len(urgent_emails)} urgent emails. "
    
    # List top 3 urgent emails
    for i, email in enumerate(urgent_emails[:3]):
        text += f"Email {i+1}: {email.get('subject', 'No subject')} from {email.get('sender', 'Unknown')}. "
    
    if len(urgent_emails) > 3:
        text += f"And {len(urgent_emails) - 3} more urgent emails. "
    
    text += "Please review these emails immediately."
    
    return text

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for TTS"""
    return {
        "languages": [
            {"code": "en-US", "name": "English (US)"},
            {"code": "en-GB", "name": "English (UK)"},
            {"code": "es-ES", "name": "Spanish"},
            {"code": "fr-FR", "name": "French"},
            {"code": "de-DE", "name": "German"},
            {"code": "it-IT", "name": "Italian"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)"},
            {"code": "ru-RU", "name": "Russian"},
            {"code": "ja-JP", "name": "Japanese"},
            {"code": "ko-KR", "name": "Korean"},
            {"code": "zh-CN", "name": "Chinese (Simplified)"},
            {"code": "hi-IN", "name": "Hindi"},
            {"code": "ar-SA", "name": "Arabic"},
            {"code": "nl-NL", "name": "Dutch"},
            {"code": "sv-SE", "name": "Swedish"}
        ]
    }

from datetime import datetime 