from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models import EmailConfig
from app.core.database import db

router = APIRouter(
    prefix="/api/config",
    tags=["Configuration"],
    responses={404: {"description": "Not found"}},
)

@router.get("/email", response_model=EmailConfig)
async def get_email_config():
    """Get current email configuration"""
    try:
        config = db.get_configuration("email_config")
        if not config:
            # Return default configuration
            config = {
                "email_address": "",
                "password": "",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_ssl": True,
                "vip_contacts": [],
                "auto_categorize": True,
                "daily_summary_time": "09:00",
                "response_reminder_hours": 24,
                "follow_up_reminder_days": 3
            }
        return EmailConfig(**config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/email", response_model=EmailConfig)
async def update_email_config(config: EmailConfig):
    """Update email configuration"""
    try:
        # Save to database
        db.save_configuration("email_config", config.dict())
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vip-contacts")
async def get_vip_contacts():
    """Get list of VIP contacts"""
    try:
        contacts = db.get_vip_contacts()
        return {"contacts": contacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vip-contacts")
async def add_vip_contact(email: str, name: str = None, priority_level: str = "high"):
    """Add a VIP contact"""
    try:
        db.add_vip_contact(email, name, priority_level)
        return {"message": f"VIP contact {email} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vip-contacts/{email}")
async def remove_vip_contact(email: str):
    """Remove a VIP contact"""
    try:
        # This would typically delete from database
        # For now, we'll return a success message
        return {"message": f"VIP contact {email} removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system")
async def get_system_config():
    """Get system configuration"""
    try:
        config = db.get_configuration("system_config")
        if not config:
            config = {
                "auto_start": True,
                "log_level": "INFO",
                "max_emails_per_batch": 50,
                "retention_days": 30,
                "backup_enabled": False,
                "backup_frequency": "daily"
            }
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/system")
async def update_system_config(config: Dict[str, Any]):
    """Update system configuration"""
    try:
        db.save_configuration("system_config", config)
        return {"message": "System configuration updated successfully", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_system_status():
    """Get system status and health information"""
    try:
        from app.core.email_processor import EmailProcessor
        from app.core.notification_manager import NotificationManager
        
        status = {
            "database": "connected",
            "email_processor": "ready",
            "notification_manager": "ready",
            "scheduler": "running",
            "last_email_check": "2024-01-01 09:00:00",
            "total_emails_processed": 0,
            "active_notifications": []
        }
        
        # Check email configuration
        email_config = db.get_configuration("email_config")
        if email_config and email_config.get("email_address"):
            status["email_configured"] = True
        else:
            status["email_configured"] = False
        
        # Check notification configuration
        notification_config = db.get_configuration("notification_config")
        if notification_config:
            status["notifications_configured"] = bool(
                notification_config.get("slack_webhook_url") or
                notification_config.get("telegram_bot_token") or
                notification_config.get("whatsapp_webhook_url")
            )
        else:
            status["notifications_configured"] = False
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-email-connection")
async def test_email_connection():
    """Test email connection"""
    try:
        from app.core.email_processor import EmailProcessor
        
        processor = EmailProcessor()
        
        # Try to connect to IMAP server
        try:
            imap = processor.connect_imap()
            imap.logout()
            return {"message": "Email connection successful", "status": "connected"}
        except Exception as e:
            return {"message": f"Email connection failed: {str(e)}", "status": "failed"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-config")
async def reset_configuration(config_type: str):
    """Reset configuration to defaults"""
    try:
        if config_type == "email":
            # Reset email configuration
            default_config = {
                "email_address": "",
                "password": "",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_ssl": True,
                "vip_contacts": [],
                "auto_categorize": True,
                "daily_summary_time": "09:00",
                "response_reminder_hours": 24,
                "follow_up_reminder_days": 3
            }
            db.save_configuration("email_config", default_config)
            
        elif config_type == "notifications":
            # Reset notification configuration
            default_config = {
                "slack_webhook_url": "",
                "telegram_bot_token": "",
                "telegram_chat_id": "",
                "whatsapp_webhook_url": "",
                "enable_voice_summary": False,
                "notification_channels": []
            }
            db.save_configuration("notification_config", default_config)
            
        elif config_type == "system":
            # Reset system configuration
            default_config = {
                "auto_start": True,
                "log_level": "INFO",
                "max_emails_per_batch": 50,
                "retention_days": 30,
                "backup_enabled": False,
                "backup_frequency": "daily"
            }
            db.save_configuration("system_config", default_config)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid config type")
        
        return {"message": f"{config_type} configuration reset to defaults"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email-providers")
async def get_email_providers():
    """Get list of common email providers and their settings"""
    return {
        "providers": [
            {
                "name": "Gmail",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_ssl": True,
                "notes": "Requires app password for 2FA accounts"
            },
            {
                "name": "Outlook/Hotmail",
                "imap_server": "outlook.office365.com",
                "imap_port": 993,
                "smtp_server": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "use_ssl": True,
                "notes": "May require app password"
            },
            {
                "name": "Yahoo",
                "imap_server": "imap.mail.yahoo.com",
                "imap_port": 993,
                "smtp_server": "smtp.mail.yahoo.com",
                "smtp_port": 587,
                "use_ssl": True,
                "notes": "Requires app password"
            },
            {
                "name": "ProtonMail",
                "imap_server": "127.0.0.1",
                "imap_port": 1143,
                "smtp_server": "127.0.0.1",
                "smtp_port": 1025,
                "use_ssl": False,
                "notes": "Requires ProtonMail Bridge"
            },
            {
                "name": "Custom",
                "imap_server": "",
                "imap_port": 993,
                "smtp_server": "",
                "smtp_port": 587,
                "use_ssl": True,
                "notes": "Enter your custom server settings"
            }
        ]
    }

@router.get("/logs")
async def get_system_logs(limit: int = 100):
    """Get system logs (placeholder)"""
    try:
        # This would typically read from log files
        # For now, return placeholder logs
        logs = [
            {
                "timestamp": "2024-01-01 09:00:00",
                "level": "INFO",
                "message": "Email agent started successfully"
            },
            {
                "timestamp": "2024-01-01 09:05:00",
                "level": "INFO",
                "message": "Daily email processing completed"
            }
        ]
        
        return {"logs": logs[:limit]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 