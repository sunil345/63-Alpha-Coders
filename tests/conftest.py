import pytest
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from main import app
from app.core.database import Database
from app.models import EmailSummary, EmailCategory, PriorityLevel

@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def temp_db():
    """Temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Create test database
    db = Database(db_path)
    db.init_database()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)

@pytest.fixture
def sample_email_data():
    """Sample email data for testing"""
    return {
        'id': 'test-email-1',
        'subject': 'Test Email Subject',
        'sender': 'John Doe',
        'sender_email': 'john@example.com',
        'received_at': datetime.now().isoformat(),
        'body': 'This is a test email body with some content.',
        'raw_message': Mock()
    }

@pytest.fixture
def sample_email_summary():
    """Sample email summary for testing"""
    return EmailSummary(
        id='test-email-1',
        subject='Test Email Subject',
        sender='John Doe',
        sender_email='john@example.com',
        received_at=datetime.now(),
        category=EmailCategory.WORK,
        priority=PriorityLevel.MEDIUM,
        summary='Test email summary',
        urgency_score=0.5,
        action_required=False,
        follow_up_suggestions=['Reply to the email']
    )

@pytest.fixture
def sample_daily_summary():
    """Sample daily summary for testing"""
    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_emails': 5,
        'categories': {
            'work': 3,
            'personal': 1,
            'promotions': 1
        },
        'urgent_emails': [],
        'unread_emails': [],
        'response_reminders': [],
        'priority_breakdown': {
            'low': 2,
            'medium': 2,
            'high': 1
        }
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "0.7"
    return mock_response

@pytest.fixture
def mock_imap_connection():
    """Mock IMAP connection"""
    mock_imap = Mock()
    mock_imap.search.return_value = (None, [b'1 2 3'])
    mock_imap.fetch.return_value = (None, [(b'1', b'email_data')])
    mock_imap.logout.return_value = None
    return mock_imap

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'email_address': 'test@example.com',
        'password': 'test-password',
        'imap_server': 'imap.gmail.com',
        'imap_port': 993,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_ssl': True,
        'vip_contacts': ['vip@example.com'],
        'auto_categorize': True,
        'daily_summary_time': '09:00',
        'response_reminder_hours': 24,
        'follow_up_reminder_days': 3
    } 