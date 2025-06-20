from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class EmailCategory(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    PROMOTIONS = "promotions"
    SOCIAL = "social"
    URGENT = "urgent"
    MEETINGS = "meetings"
    DEADLINES = "deadlines"
    OTHER = "other"

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class EmailSummary(BaseModel):
    id: str
    subject: str
    sender: str
    sender_email: EmailStr
    received_at: datetime
    category: EmailCategory
    priority: PriorityLevel
    summary: str
    is_read: bool = False
    is_replied: bool = False
    urgency_score: float = Field(ge=0, le=1)
    action_required: bool = False
    follow_up_suggestions: List[str] = []

class DailySummary(BaseModel):
    date: datetime
    total_emails: int
    categories: Dict[EmailCategory, int]
    urgent_emails: List[EmailSummary]
    unread_emails: List[EmailSummary]
    response_reminders: List[EmailSummary]
    priority_breakdown: Dict[PriorityLevel, int]

class EmailConfig(BaseModel):
    email_address: EmailStr
    password: str
    imap_server: str
    imap_port: int = 993
    smtp_server: str
    smtp_port: int = 587
    use_ssl: bool = True
    vip_contacts: List[EmailStr] = []
    auto_categorize: bool = True
    daily_summary_time: str = "09:00"
    response_reminder_hours: int = 24
    follow_up_reminder_days: int = 3

class NotificationConfig(BaseModel):
    slack_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    whatsapp_webhook_url: Optional[str] = None
    enable_voice_summary: bool = False
    notification_channels: List[str] = []

class AnalysisRequest(BaseModel):
    date_range: Optional[str] = "today"
    include_archived: bool = False
    categories_filter: Optional[List[EmailCategory]] = None
    priority_filter: Optional[List[PriorityLevel]] = None

class VoiceSummaryRequest(BaseModel):
    summary_id: str
    voice_type: str = "en-US"
    speed: float = 1.0

class FollowUpSuggestion(BaseModel):
    email_id: str
    suggestion: str
    confidence: float
    context: str 