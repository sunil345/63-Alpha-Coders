# Intelligent Email Agent API Documentation

## Overview

The Intelligent Email Agent API provides comprehensive email analysis, categorization, and management capabilities powered by artificial intelligence. This RESTful API enables developers to integrate intelligent email processing into their applications.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.emailagent.com`

## Interactive Documentation

- **Swagger UI**: `{BASE_URL}/docs`
- **ReDoc**: `{BASE_URL}/redoc`
- **OpenAPI Spec**: `{BASE_URL}/openapi.json`

## Authentication

The API uses email credentials for IMAP access. Ensure your email provider supports IMAP and has app passwords enabled for secure access.

## Rate Limits

| Endpoint Category | Requests per Minute |
|-------------------|-------------------|
| Email Processing  | 10                |
| Notifications     | 50                |
| Voice Generation  | 20                |
| Configuration     | 100               |

## API Endpoints

### Email Analysis

#### Process Emails
```http
POST /api/email/process-emails
```

Process emails from IMAP server with AI analysis and categorization.

**Request Body:**
```json
{
  "email_address": "user@example.com",
  "password": "app-password",
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "use_ssl": true,
  "limit": 50
}
```

**Response:**
```json
{
  "total_processed": 25,
  "total_saved": 25,
  "errors": [],
  "processing_time": 15.5
}
```

#### Get Daily Summary
```http
GET /api/email/daily-summary/{date}
```

Retrieve comprehensive email summary for a specific date.

**Parameters:**
- `date` (path): Date in YYYY-MM-DD format

**Response:**
```json
{
  "date": "2024-01-15",
  "total_emails": 25,
  "categories": {
    "work": 15,
    "personal": 5,
    "promotions": 3,
    "social": 2
  },
  "urgent_emails": [],
  "unread_emails": [],
  "response_reminders": [],
  "priority_breakdown": {
    "low": 8,
    "medium": 12,
    "high": 5
  }
}
```

#### Get Emails by Date
```http
GET /api/email/emails/{date}
```

Retrieve processed emails for a specific date with optional filtering.

**Parameters:**
- `date` (path): Date in YYYY-MM-DD format
- `category` (query, optional): Filter by category
- `priority` (query, optional): Filter by priority
- `limit` (query, optional): Maximum emails to return (default: 50)

**Response:**
```json
[
  {
    "id": "email-1",
    "subject": "Project Update",
    "sender": "John Doe",
    "sender_email": "john@company.com",
    "received_at": "2024-01-15T10:30:00",
    "category": "work",
    "priority": "medium",
    "summary": "Project status update with timeline",
    "is_read": false,
    "is_replied": false,
    "urgency_score": 0.6,
    "action_required": true,
    "follow_up_suggestions": [
      "Reply with status update",
      "Schedule follow-up meeting"
    ]
  }
]
```

#### Mark Email as Read
```http
PUT /api/email/emails/{email_id}/mark-read
```

Mark a specific email as read.

**Response:**
```json
{
  "success": true,
  "message": "Email marked as read"
}
```

#### Mark Email as Replied
```http
PUT /api/email/emails/{email_id}/mark-replied
```

Mark a specific email as replied to.

**Response:**
```json
{
  "success": true,
  "message": "Email marked as replied"
}
```

### Notifications

#### Send Notification
```http
POST /api/notifications/send
```

Send notification through specified channels.

**Request Body:**
```json
{
  "message": "You have 5 new emails requiring attention",
  "channels": ["slack", "telegram"]
}
```

**Response:**
```json
{
  "slack": true,
  "telegram": true,
  "whatsapp": false
}
```

#### Send Daily Summary Notification
```http
POST /api/notifications/daily-summary
```

Send formatted daily summary notification.

**Request Body:**
```json
{
  "date": "2024-01-15",
  "total_emails": 25,
  "categories": {
    "work": 15,
    "personal": 5,
    "promotions": 3,
    "social": 2
  },
  "urgent_emails": [],
  "unread_emails": [],
  "response_reminders": [],
  "priority_breakdown": {
    "low": 8,
    "medium": 12,
    "high": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Daily summary notification sent"
}
```

#### Send Urgent Email Notification
```http
POST /api/notifications/urgent-email
```

Send immediate notification for urgent emails.

**Request Body:**
```json
{
  "subject": "URGENT: System Down",
  "sender": "Admin",
  "sender_email": "admin@company.com",
  "received_at": "2024-01-15T10:00:00",
  "summary": "System is down and needs immediate attention"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Urgent email notification sent"
}
```

### Voice

#### Generate Voice Summary
```http
POST /api/voice/generate-voice-summary
```

Convert text to speech and return audio file.

**Request Body:**
```json
{
  "text": "You have 5 new emails today. 3 are work-related and 2 are personal.",
  "voice": "en-US-Standard-A"
}
```

**Response:**
- Content-Type: `audio/mpeg`
- Body: Binary audio data

#### Get Available Voices
```http
GET /api/voice/available-voices
```

Retrieve list of available TTS voices.

**Response:**
```json
[
  {
    "name": "en-US-Standard-A",
    "language": "en-US",
    "gender": "female"
  },
  {
    "name": "en-US-Standard-B",
    "language": "en-US",
    "gender": "male"
  }
]
```

### Configuration

#### Get Configuration
```http
GET /api/config/configuration/{config_key}
```

Retrieve configuration for a specific key.

**Parameters:**
- `config_key` (path): Configuration key (e.g., "email_config")

**Response:**
```json
{
  "email_address": "user@example.com",
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "use_ssl": true
}
```

#### Save Configuration
```http
POST /api/config/configuration/{config_key}
```

Save configuration for a specific key.

**Request Body:**
```json
{
  "email_address": "user@example.com",
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "use_ssl": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration saved successfully"
}
```

#### Get VIP Contacts
```http
GET /api/config/vip-contacts
```

Retrieve all VIP contacts.

**Response:**
```json
[
  {
    "email": "ceo@company.com",
    "name": "CEO",
    "priority_level": "high"
  },
  {
    "email": "manager@company.com",
    "name": "Manager",
    "priority_level": "medium"
  }
]
```

#### Add VIP Contact
```http
POST /api/config/vip-contacts
```

Add a new VIP contact.

**Request Body:**
```json
{
  "email": "newvip@company.com",
  "name": "New VIP",
  "priority_level": "high"
}
```

**Response:**
```json
{
  "success": true,
  "message": "VIP contact added successfully"
}
```

#### Delete VIP Contact
```http
DELETE /api/config/vip-contacts/{email}
```

Remove a VIP contact.

**Parameters:**
- `email` (path): Email address of VIP contact

**Response:**
```json
{
  "success": true,
  "message": "VIP contact deleted successfully"
}
```

## Data Models

### EmailSummary
```json
{
  "id": "string",
  "subject": "string",
  "sender": "string",
  "sender_email": "string",
  "received_at": "2024-01-15T10:30:00",
  "category": "work|personal|promotions|social|urgent|meetings|deadlines|other",
  "priority": "low|medium|high",
  "summary": "string",
  "is_read": false,
  "is_replied": false,
  "urgency_score": 0.6,
  "action_required": true,
  "follow_up_suggestions": ["string"]
}
```

### DailySummary
```json
{
  "date": "2024-01-15",
  "total_emails": 25,
  "categories": {
    "work": 15,
    "personal": 5
  },
  "urgent_emails": [EmailSummary],
  "unread_emails": [EmailSummary],
  "response_reminders": [EmailSummary],
  "priority_breakdown": {
    "low": 8,
    "medium": 12,
    "high": 5
  }
}
```

### VIPContact
```json
{
  "email": "string",
  "name": "string",
  "priority_level": "low|medium|high"
}
```

## Error Handling

### Error Response Format
```json
{
  "error": "Error message",
  "details": "Additional error details",
  "timestamp": "2024-01-15T10:30:00"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request - Invalid parameters |
| 404  | Not Found - Resource not found |
| 422  | Validation Error - Invalid request format |
| 500  | Internal Server Error |

## Getting Started

### 1. Configure Email Settings
```bash
curl -X POST "http://localhost:8000/api/config/configuration/email_config" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "your@email.com",
    "password": "your-app-password",
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "use_ssl": true
  }'
```

### 2. Add VIP Contacts
```bash
curl -X POST "http://localhost:8000/api/config/vip-contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "boss@company.com",
    "name": "Boss",
    "priority_level": "high"
  }'
```

### 3. Process Emails
```bash
curl -X POST "http://localhost:8000/api/email/process-emails" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "your@email.com",
    "password": "your-app-password",
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "use_ssl": true,
    "limit": 50
  }'
```

### 4. Get Daily Summary
```bash
curl "http://localhost:8000/api/email/daily-summary/2024-01-15"
```

## SDKs and Libraries

### Python
```python
import requests

# Process emails
response = requests.post(
    "http://localhost:8000/api/email/process-emails",
    json={
        "email_address": "your@email.com",
        "password": "your-app-password",
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "use_ssl": True,
        "limit": 50
    }
)

# Get daily summary
summary = requests.get(
    "http://localhost:8000/api/email/daily-summary/2024-01-15"
).json()
```

### JavaScript
```javascript
// Process emails
const response = await fetch('http://localhost:8000/api/email/process-emails', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email_address: 'your@email.com',
    password: 'your-app-password',
    imap_server: 'imap.gmail.com',
    imap_port: 993,
    use_ssl: true,
    limit: 50
  })
});

// Get daily summary
const summary = await fetch(
  'http://localhost:8000/api/email/daily-summary/2024-01-15'
).then(res => res.json());
```

## Support

For API support and questions:
- **Email**: support@emailagent.com
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/emailagent/issues)

## Changelog

### v1.0.0 (2024-01-15)
- Initial API release
- Email processing and analysis
- Multi-channel notifications
- Voice summary generation
- VIP contact management
- Configuration endpoints 