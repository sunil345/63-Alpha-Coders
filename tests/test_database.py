import pytest
import json
from datetime import datetime
from app.core.database import Database
from app.models import EmailCategory, PriorityLevel

class TestDatabase:
    """Test cases for Database class"""
    
    def test_init_database(self, temp_db):
        """Test database initialization"""
        db = Database(temp_db)
        
        # Check if tables are created
        conn = db.connect()
        cursor = conn.cursor()
        
        # Check email_summaries table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='email_summaries'")
        assert cursor.fetchone() is not None
        
        # Check daily_summaries table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_summaries'")
        assert cursor.fetchone() is not None
        
        # Check configurations table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='configurations'")
        assert cursor.fetchone() is not None
        
        # Check vip_contacts table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vip_contacts'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_save_email_summary(self, temp_db):
        """Test saving email summary"""
        db = Database(temp_db)
        
        email_summary = {
            'id': 'test-email-1',
            'subject': 'Test Subject',
            'sender': 'Test Sender',
            'sender_email': 'test@example.com',
            'received_at': datetime.now().isoformat(),
            'category': EmailCategory.WORK.value,
            'priority': PriorityLevel.MEDIUM.value,
            'summary': 'Test summary',
            'is_read': False,
            'is_replied': False,
            'urgency_score': 0.5,
            'action_required': False,
            'follow_up_suggestions': ['Reply to email']
        }
        
        db.save_email_summary(email_summary)
        
        # Verify email was saved
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM email_summaries WHERE id = ?", ('test-email-1',))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[1] == 'Test Subject'
        assert result[2] == 'Test Sender'
        assert result[3] == 'test@example.com'
        
        conn.close()
    
    def test_save_daily_summary(self, temp_db):
        """Test saving daily summary"""
        db = Database(temp_db)
        
        daily_summary = {
            'date': '2024-01-01',
            'total_emails': 10,
            'categories': {'work': 5, 'personal': 3, 'promotions': 2},
            'urgent_emails': [],
            'unread_emails': [],
            'response_reminders': [],
            'priority_breakdown': {'low': 3, 'medium': 5, 'high': 2}
        }
        
        db.save_daily_summary(daily_summary)
        
        # Verify daily summary was saved
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_summaries WHERE date = ?", ('2024-01-01',))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[2] == 10  # total_emails
        
        # Check categories JSON
        categories = json.loads(result[3])
        assert categories['work'] == 5
        assert categories['personal'] == 3
        
        conn.close()
    
    def test_get_emails_by_date(self, temp_db):
        """Test getting emails by date"""
        db = Database(temp_db)
        
        # Save test email
        email_summary = {
            'id': 'test-email-1',
            'subject': 'Test Subject',
            'sender': 'Test Sender',
            'sender_email': 'test@example.com',
            'received_at': '2024-01-01 10:00:00',
            'category': EmailCategory.WORK.value,
            'priority': PriorityLevel.MEDIUM.value,
            'summary': 'Test summary',
            'is_read': False,
            'is_replied': False,
            'urgency_score': 0.5,
            'action_required': False,
            'follow_up_suggestions': []
        }
        db.save_email_summary(email_summary)
        
        # Get emails for the date
        emails = db.get_emails_by_date('2024-01-01')
        
        assert len(emails) == 1
        assert emails[0]['id'] == 'test-email-1'
        assert emails[0]['subject'] == 'Test Subject'
    
    def test_get_daily_summary(self, temp_db):
        """Test getting daily summary"""
        db = Database(temp_db)
        
        # Save test daily summary
        daily_summary = {
            'date': '2024-01-01',
            'total_emails': 5,
            'categories': {'work': 3, 'personal': 2},
            'urgent_emails': [],
            'unread_emails': [],
            'response_reminders': [],
            'priority_breakdown': {'low': 2, 'medium': 3}
        }
        db.save_daily_summary(daily_summary)
        
        # Get daily summary
        result = db.get_daily_summary('2024-01-01')
        
        assert result is not None
        assert result['date'] == '2024-01-01'
        assert result['total_emails'] == 5
        assert result['categories']['work'] == 3
    
    def test_save_and_get_configuration(self, temp_db):
        """Test saving and getting configuration"""
        db = Database(temp_db)
        
        config_data = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com'
        }
        
        db.save_configuration('email_config', config_data)
        
        # Get configuration
        result = db.get_configuration('email_config')
        
        assert result is not None
        assert result['email_address'] == 'test@example.com'
        assert result['password'] == 'test-password'
        assert result['imap_server'] == 'imap.gmail.com'
    
    def test_add_and_get_vip_contacts(self, temp_db):
        """Test adding and getting VIP contacts"""
        db = Database(temp_db)
        
        # Add VIP contact
        db.add_vip_contact('vip@example.com', 'VIP User', 'high')
        
        # Get VIP contacts
        contacts = db.get_vip_contacts()
        
        assert len(contacts) == 1
        assert contacts[0]['email'] == 'vip@example.com'
        assert contacts[0]['name'] == 'VIP User'
        assert contacts[0]['priority_level'] == 'high'
    
    def test_get_nonexistent_daily_summary(self, temp_db):
        """Test getting non-existent daily summary"""
        db = Database(temp_db)
        
        result = db.get_daily_summary('2024-01-01')
        assert result is None
    
    def test_get_emails_empty_date(self, temp_db):
        """Test getting emails for empty date"""
        db = Database(temp_db)
        
        emails = db.get_emails_by_date('2024-01-01')
        assert len(emails) == 0
    
    def test_get_nonexistent_configuration(self, temp_db):
        """Test getting non-existent configuration"""
        db = Database(temp_db)
        
        result = db.get_configuration('nonexistent_config')
        assert result is None 