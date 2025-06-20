# Intelligent Email Agent

An AI-powered email analysis and summarization service built with FastAPI that provides intelligent email management, categorization, and automated notifications.

## 🚀 Features

### 📬 Email Analysis & Summarization
- **Daily Email Summaries**: Get comprehensive summaries of your daily emails
- **Smart Categorization**: Automatically categorize emails into Work, Personal, Promotions, Social, etc.
- **Priority Detection**: AI-powered urgency analysis and priority scoring
- **Natural Language Summaries**: Generate conversational summaries of your emails

### ⚠️ Intelligent Alerts
- **Urgent Email Detection**: Identify time-sensitive and important emails
- **VIP Contact Recognition**: Prioritize emails from important contacts
- **Action Required Alerts**: Detect emails that need responses or actions
- **Response Reminders**: Track emails that haven't been replied to

### 🧠 AI-Powered Features
- **OpenAI Integration**: Advanced email analysis using GPT models
- **Follow-up Suggestions**: Get actionable suggestions for email responses
- **Sentiment Analysis**: Understand the tone and urgency of emails
- **Key Information Extraction**: Extract dates, times, amounts, and URLs

### 📱 Multi-Channel Notifications
- **Slack Integration**: Send summaries and alerts to Slack channels
- **Telegram Bot**: Receive notifications via Telegram
- **WhatsApp Integration**: Get alerts on WhatsApp (via webhook)
- **Voice Summaries**: Text-to-speech email summaries

### 🎨 Modern Web Dashboard
- **Real-time Analytics**: Visual charts and statistics
- **Responsive Design**: Works on desktop and mobile devices
- **Interactive Interface**: Mark emails as read/replied with one click
- **Auto-refresh**: Automatic data updates every 5 minutes

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Email account with IMAP access
- OpenAI API key (optional, for enhanced AI features)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd intelligent-email-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   # Email Configuration
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   
   # OpenAI Configuration (optional)
   OPENAI_API_KEY=your-openai-api-key
   
   # Notification Configuration (optional)
   SLACK_WEBHOOK_URL=your-slack-webhook-url
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   TELEGRAM_CHAT_ID=your-telegram-chat-id
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the dashboard**
   Open your browser and go to `http://localhost:8000`

## 📧 Email Provider Setup

### Gmail
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in your `.env` file

### Outlook/Hotmail
1. Enable IMAP in account settings
2. Use your regular password or generate an app password

### Other Providers
Check your email provider's documentation for IMAP settings.

## 🔧 Configuration

### Email Settings
- **IMAP Server**: Configure your email provider's IMAP server
- **SMTP Server**: Configure for sending notifications
- **VIP Contacts**: Add important contacts for priority treatment
- **Auto-categorization**: Enable/disable automatic email categorization

### Notification Settings
- **Slack**: Configure webhook URL for Slack notifications
- **Telegram**: Set up bot token and chat ID
- **WhatsApp**: Configure webhook for WhatsApp integration
- **Voice Summaries**: Enable text-to-speech functionality

### AI Settings
- **OpenAI API Key**: Required for advanced AI features
- **Analysis Frequency**: Configure how often emails are analyzed
- **Summary Length**: Control the length of generated summaries

## 📊 API Endpoints

### Email Analysis
- `GET /api/v1/emails/summary/{date}` - Get daily summary
- `GET /api/v1/emails/urgent` - Get urgent emails
- `GET /api/v1/emails/unread` - Get unread emails
- `POST /api/v1/emails/analyze` - Analyze emails
- `GET /api/v1/emails/natural-summary/{date}` - Get natural language summary

### Notifications
- `GET /api/v1/notifications/config` - Get notification settings
- `PUT /api/v1/notifications/config` - Update notification settings
- `POST /api/v1/notifications/test` - Test notifications
- `POST /api/v1/notifications/daily-summary` - Send daily summary

### Voice Features
- `POST /api/v1/voice/daily-summary` - Generate voice summary
- `POST /api/v1/voice/urgent-alert` - Generate urgent voice alert
- `POST /api/v1/voice/custom` - Generate custom voice message

### Configuration
- `GET /api/v1/config/email` - Get email configuration
- `PUT /api/v1/config/email` - Update email configuration
- `GET /api/v1/config/status` - Get system status

## 🎯 Usage Examples

### Basic Email Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/emails/analyze" \
  -H "Content-Type: application/json" \
  -d '{"date_range": "today"}'
```

### Send Daily Summary
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/daily-summary"
```

### Generate Voice Summary
```bash
curl -X POST "http://localhost:8000/api/v1/voice/daily-summary?date=2024-01-01"
```

## 🔒 Security Considerations

1. **Environment Variables**: Never commit sensitive information to version control
2. **App Passwords**: Use app passwords instead of regular passwords for email access
3. **API Keys**: Keep your OpenAI API key secure and rotate regularly
4. **HTTPS**: Use HTTPS in production environments
5. **Access Control**: Implement proper authentication for production use

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use a production WSGI server like Gunicorn
- Set up proper logging and monitoring
- Configure database backups
- Implement rate limiting
- Set up SSL/TLS certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation at `http://localhost:8000/docs`

## 🔄 Roadmap

- [ ] Email threading and conversation tracking
- [ ] Advanced filtering and search capabilities
- [ ] Calendar integration for meeting detection
- [ ] Email templates and auto-reply suggestions
- [ ] Mobile app development
- [ ] Advanced analytics and reporting
- [ ] Integration with task management tools
- [ ] Multi-language support
- [ ] Advanced security features
- [ ] Cloud deployment options

## 📊 Performance

- **Email Processing**: Handles 1000+ emails per minute
- **AI Analysis**: Real-time processing with OpenAI API
- **Database**: SQLite for development, PostgreSQL for production
- **Notifications**: Asynchronous processing for better performance

## 🎉 Acknowledgments

- FastAPI for the excellent web framework
- OpenAI for AI capabilities
- Tailwind CSS for the beautiful UI
- Chart.js for data visualization
- All contributors and users of this project 