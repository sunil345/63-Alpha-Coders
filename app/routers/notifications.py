from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from app.models import NotificationConfig
from app.core.notification_manager import NotificationManager
from app.core.database import db

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
    responses={404: {"description": "Not found"}},
)

@router.get("/config", response_model=NotificationConfig)
async def get_notification_config():
    """Get current notification configuration"""
    try:
        config = db.get_configuration("notification_config")
        if not config:
            config = {
                "slack_webhook_url": "",
                "telegram_bot_token": "",
                "telegram_chat_id": "",
                "whatsapp_webhook_url": "",
                "enable_voice_summary": False,
                "notification_channels": []
            }
        return NotificationConfig(**config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config", response_model=NotificationConfig)
async def update_notification_config(config: NotificationConfig):
    """Update notification configuration"""
    try:
        notification_manager = NotificationManager()
        notification_manager.update_config(config.dict())
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_notifications():
    """Test all configured notification channels"""
    try:
        notification_manager = NotificationManager()
        results = notification_manager.test_notifications()
        return {
            "message": "Test notifications sent",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_custom_notification(
    title: str,
    message: str,
    priority: str = "normal"
):
    """Send a custom notification"""
    try:
        notification_manager = NotificationManager()
        results = notification_manager.send_notification(title, message, priority)
        return {
            "message": "Notification sent",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/daily-summary")
async def send_daily_summary(background_tasks: BackgroundTasks):
    """Send daily email summary notification"""
    try:
        from app.core.email_processor import EmailProcessor
        from app.core.scheduler import EmailScheduler
        
        # Process today's emails
        processor = EmailProcessor()
        today = datetime.now().strftime('%Y-%m-%d')
        email_summaries = processor.process_inbox(today)
        
        if email_summaries:
            # Generate daily summary
            scheduler = EmailScheduler()
            daily_summary = scheduler._generate_daily_summary(email_summaries)
            
            # Send notifications
            notification_manager = NotificationManager()
            results = notification_manager.send_daily_summary(daily_summary)
            
            return {
                "message": "Daily summary sent",
                "results": results,
                "total_emails": len(email_summaries)
            }
        else:
            return {
                "message": "No emails to summarize",
                "total_emails": 0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/urgent-alert")
async def send_urgent_alert():
    """Send urgent email alert"""
    try:
        from app.core.email_processor import EmailProcessor
        
        # Get urgent emails
        processor = EmailProcessor()
        today = datetime.now().strftime('%Y-%m-%d')
        emails = db.get_emails_by_date(today)
        
        urgent_emails = [
            e for e in emails 
            if e['priority'] in ['high', 'urgent'] or e['urgency_score'] >= 0.7
        ]
        
        if urgent_emails:
            notification_manager = NotificationManager()
            results = notification_manager.send_urgent_alert(urgent_emails)
            
            return {
                "message": "Urgent alert sent",
                "results": results,
                "urgent_count": len(urgent_emails)
            }
        else:
            return {
                "message": "No urgent emails found",
                "urgent_count": 0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/response-reminders")
async def send_response_reminders():
    """Send response reminder notifications"""
    try:
        from app.core.email_processor import EmailProcessor
        
        # Get emails that need responses
        processor = EmailProcessor()
        today = datetime.now().strftime('%Y-%m-%d')
        emails = db.get_emails_by_date(today)
        
        reminder_emails = [
            e for e in emails 
            if not e['is_replied'] and e['action_required']
        ]
        
        if reminder_emails:
            notification_manager = NotificationManager()
            results = notification_manager.send_response_reminder(reminder_emails)
            
            return {
                "message": "Response reminders sent",
                "results": results,
                "reminder_count": len(reminder_emails)
            }
        else:
            return {
                "message": "No response reminders needed",
                "reminder_count": 0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channels")
async def get_available_channels():
    """Get list of available notification channels"""
    return {
        "channels": [
            {
                "name": "slack",
                "description": "Send notifications to Slack channel",
                "config_required": ["slack_webhook_url"]
            },
            {
                "name": "telegram",
                "description": "Send notifications to Telegram chat",
                "config_required": ["telegram_bot_token", "telegram_chat_id"]
            },
            {
                "name": "whatsapp",
                "description": "Send notifications to WhatsApp",
                "config_required": ["whatsapp_webhook_url"]
            }
        ]
    }

@router.get("/status")
async def get_notification_status():
    """Get status of notification channels"""
    try:
        notification_manager = NotificationManager()
        config = notification_manager.get_config()
        
        status = {
            "slack": {
                "configured": bool(config.get("slack_webhook_url")),
                "webhook_url": "***" if config.get("slack_webhook_url") else None
            },
            "telegram": {
                "configured": bool(config.get("telegram_bot_token") and config.get("telegram_chat_id")),
                "bot_token": "***" if config.get("telegram_bot_token") else None,
                "chat_id": config.get("telegram_chat_id")
            },
            "whatsapp": {
                "configured": bool(config.get("whatsapp_webhook_url")),
                "webhook_url": "***" if config.get("whatsapp_webhook_url") else None
            }
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from datetime import datetime  # Add this import at the top 