# Quick Start Guide - Intelligent Email Agent API

## 🚀 Running the Server Locally

### Prerequisites
- Python 3.9 or higher
- pip3 (Python package manager)

### Step 1: Install Dependencies
```bash
python3 -m pip install -r requirements.txt
```

### Step 2: Set Up Environment (Optional)
```bash
# Copy the sample environment file
cp sample.env .env

# Edit .env with your actual credentials
# - Add your OpenAI API key
# - Configure your email settings
# - Set up notification tokens
```

### Step 3: Start the Server
```bash
# Option 1: Using the simple runner script
python3 run_server.py

# Option 2: Using uvicorn directly
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Access the API
Once the server starts, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Dashboard**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Interactive Documentation
The server automatically opens the Swagger UI documentation in your browser. You can:
- Browse all available endpoints
- Test API calls directly in the browser
- View request/response schemas
- See example payloads

### Available Endpoints

#### Email Analysis
- `POST /api/email/process-emails` - Process emails from IMAP
- `GET /api/email/daily-summary/{date}` - Get daily summary
- `GET /api/email/emails/{date}` - Get emails by date
- `PUT /api/email/emails/{id}/mark-read` - Mark as read
- `PUT /api/email/emails/{id}/mark-replied` - Mark as replied

#### Notifications
- `POST /api/notifications/send` - Send notification
- `POST /api/notifications/daily-summary` - Send daily summary
- `POST /api/notifications/urgent-email` - Send urgent alert

#### Voice
- `POST /api/voice/generate-voice-summary` - Generate TTS
- `GET /api/voice/available-voices` - List voices

#### Configuration
- `GET/POST /api/config/configuration/{key}` - Manage config
- `GET/POST/DELETE /api/config/vip-contacts` - Manage VIP contacts

## 🔧 Configuration

### Environment Variables
Copy `sample.env` to `.env` and configure:

```env
# Email Settings
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# AI Settings
OPENAI_API_KEY=sk-your-openai-key

# Notifications (optional)
SLACK_BOT_TOKEN=xoxb-your-slack-token
TELEGRAM_BOT_TOKEN=your-telegram-token
```

### Email Setup
1. Enable IMAP in your email provider
2. Generate an app-specific password
3. Update the EMAIL_* variables in .env

### OpenAI Setup
1. Get API key from https://platform.openai.com/
2. Set OPENAI_API_KEY in .env

## 🧪 Testing the API

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Get daily summary
curl http://localhost:8000/api/email/daily-summary/2024-01-15

# Send notification
curl -X POST http://localhost:8000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Test notification", "channels": ["slack"]}'
```

### Using Postman
1. Import `docs/Intelligent_Email_Agent_API.postman_collection.json`
2. Set base_url variable to `http://localhost:8000`
3. Run requests from the collection

## 🛠️ Troubleshooting

### Common Issues

**Server won't start:**
- Check if port 8000 is available
- Ensure all dependencies are installed
- Check Python version (3.9+ required)

**Import errors:**
- Run `python3 -m pip install -r requirements.txt`
- Check if you're using the right Python version

**Email processing fails:**
- Verify email credentials in .env
- Check IMAP settings for your provider
- Ensure app passwords are enabled

**AI features not working:**
- Set valid OPENAI_API_KEY in .env
- Check your OpenAI account has credits

### Getting Help
- Check the logs in the terminal
- Visit http://localhost:8000/docs for API documentation
- Review the full documentation in `docs/API_Documentation.md`

## 🎯 Next Steps

1. **Configure your email**: Update .env with real credentials
2. **Test email processing**: Use the `/api/email/process-emails` endpoint
3. **Set up notifications**: Configure Slack/Telegram tokens
4. **Add VIP contacts**: Use the configuration endpoints
5. **Schedule automation**: Set up daily summaries and alerts

Happy coding! 🚀 