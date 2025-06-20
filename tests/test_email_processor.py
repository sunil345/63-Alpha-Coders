import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.core.email_processor import EmailProcessor
from app.models import EmailCategory, PriorityLevel

class TestEmailProcessor:
    """Test cases for EmailProcessor class"""
    
    def test_init_email_processor(self):
        """Test EmailProcessor initialization"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        
        assert processor.email_address == 'test@example.com'
        assert processor.password == 'test-password'
        assert processor.imap_server == 'imap.gmail.com'
        assert processor.imap_port == 993
        assert processor.use_ssl is True
    
    @patch('app.core.email_processor.imaplib.IMAP4_SSL')
    def test_connect_to_imap_success(self, mock_imap_ssl):
        """Test successful IMAP connection"""
        mock_imap = Mock()
        mock_imap.login.return_value = ('OK', [b'Logged in'])
        mock_imap_ssl.return_value = mock_imap
        
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        connection = processor.connect_to_imap()
        
        assert connection is not None
        mock_imap.login.assert_called_once_with('test@example.com', 'test-password')
    
    @patch('app.core.email_processor.imaplib.IMAP4')
    def test_connect_to_imap_no_ssl(self, mock_imap):
        """Test IMAP connection without SSL"""
        mock_connection = Mock()
        mock_connection.login.return_value = ('OK', [b'Logged in'])
        mock_imap.return_value = mock_connection
        
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 143,
            'use_ssl': False
        }
        
        processor = EmailProcessor(config)
        connection = processor.connect_to_imap()
        
        assert connection is not None
        mock_connection.login.assert_called_once_with('test@example.com', 'test-password')
    
    @patch('app.core.email_processor.imaplib.IMAP4_SSL')
    def test_connect_to_imap_failure(self, mock_imap_ssl):
        """Test IMAP connection failure"""
        mock_imap = Mock()
        mock_imap.login.side_effect = Exception("Authentication failed")
        mock_imap_ssl.return_value = mock_imap
        
        config = {
            'email_address': 'test@example.com',
            'password': 'wrong-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        
        with pytest.raises(Exception):
            processor.connect_to_imap()
    
    def test_parse_email_message(self):
        """Test email message parsing"""
        processor = EmailProcessor({})
        
        # Create a mock email message
        mock_message = Mock()
        mock_message.get.return_value = 'test@example.com'
        mock_message.get_all.return_value = ['John Doe <john@example.com>']
        mock_message.get_payload.return_value = [Mock()]
        
        # Mock the email body
        mock_part = Mock()
        mock_part.get_content_type.return_value = 'text/plain'
        mock_part.get_payload.return_value = 'Test email body'
        mock_message.get_payload.return_value = [mock_part]
        
        parsed_email = processor.parse_email_message(mock_message, 'test-email-1')
        
        assert parsed_email['id'] == 'test-email-1'
        assert parsed_email['sender_email'] == 'test@example.com'
        assert parsed_email['body'] == 'Test email body'
    
    def test_analyze_priority_vip_contact(self):
        """Test priority analysis for VIP contacts"""
        processor = EmailProcessor({})
        processor.vip_contacts = ['vip@example.com']
        
        email_data = {
            'sender_email': 'vip@example.com',
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        priority = processor.analyze_priority(email_data)
        
        assert priority == PriorityLevel.HIGH
    
    def test_analyze_priority_urgent_keywords(self):
        """Test priority analysis for urgent keywords"""
        processor = EmailProcessor({})
        
        email_data = {
            'sender_email': 'test@example.com',
            'subject': 'URGENT: Action Required',
            'body': 'This needs immediate attention ASAP.'
        }
        
        priority = processor.analyze_priority(email_data)
        
        assert priority == PriorityLevel.HIGH
    
    def test_analyze_priority_normal_email(self):
        """Test priority analysis for normal email"""
        processor = EmailProcessor({})
        
        email_data = {
            'sender_email': 'test@example.com',
            'subject': 'Weekly Newsletter',
            'body': 'Here is your weekly newsletter.'
        }
        
        priority = processor.analyze_priority(email_data)
        
        assert priority == PriorityLevel.LOW
    
    def test_process_emails_empty(self, temp_db):
        """Test processing empty email list"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        processor.db = temp_db
        
        result = processor.process_emails([])
        
        assert result['total_processed'] == 0
        assert result['total_saved'] == 0
        assert result['errors'] == []
    
    def test_process_emails_with_data(self, temp_db, sample_email_data):
        """Test processing emails with data"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        processor.db = temp_db
        
        emails = [sample_email_data]
        
        result = processor.process_emails(emails)
        
        assert result['total_processed'] == 1
        assert result['total_saved'] == 1
        assert len(result['errors']) == 0
    
    def test_fetch_emails_mock(self, mock_imap_connection):
        """Test fetching emails with mock connection"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        
        # Mock the parse_email_message method
        with patch.object(processor, 'parse_email_message') as mock_parse:
            mock_parse.return_value = {
                'id': 'test-email-1',
                'subject': 'Test Subject',
                'sender': 'Test Sender',
                'sender_email': 'test@example.com',
                'received_at': '2024-01-01 10:00:00',
                'body': 'Test body'
            }
            
            emails = processor.fetch_emails(mock_imap_connection, limit=5)
            
            assert len(emails) > 0
            assert emails[0]['id'] == 'test-email-1'
    
    def test_generate_daily_summary(self, temp_db):
        """Test daily summary generation"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        processor.db = temp_db
        
        # Add some test emails to the database
        test_emails = [
            {
                'id': 'email-1',
                'subject': 'Work Email',
                'sender': 'Colleague',
                'sender_email': 'colleague@company.com',
                'received_at': '2024-01-01 10:00:00',
                'category': EmailCategory.WORK.value,
                'priority': PriorityLevel.MEDIUM.value,
                'summary': 'Work related email',
                'is_read': False,
                'is_replied': False,
                'urgency_score': 0.5,
                'action_required': False,
                'follow_up_suggestions': []
            },
            {
                'id': 'email-2',
                'subject': 'Personal Email',
                'sender': 'Friend',
                'sender_email': 'friend@example.com',
                'received_at': '2024-01-01 11:00:00',
                'category': EmailCategory.PERSONAL.value,
                'priority': PriorityLevel.LOW.value,
                'summary': 'Personal email',
                'is_read': False,
                'is_replied': False,
                'urgency_score': 0.2,
                'action_required': False,
                'follow_up_suggestions': []
            }
        ]
        
        for email in test_emails:
            processor.db.save_email_summary(email)
        
        summary = processor.generate_daily_summary('2024-01-01')
        
        assert summary['date'] == '2024-01-01'
        assert summary['total_emails'] == 2
        assert summary['categories']['work'] == 1
        assert summary['categories']['personal'] == 1
    
    def test_mark_email_as_read(self, temp_db):
        """Test marking email as read"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        processor.db = temp_db
        
        # Save a test email
        email_data = {
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
        
        processor.db.save_email_summary(email_data)
        
        # Mark as read
        success = processor.mark_email_as_read('test-email-1')
        
        assert success is True
        
        # Verify in database
        conn = processor.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT is_read FROM email_summaries WHERE id = ?", ('test-email-1',))
        result = cursor.fetchone()
        
        assert result[0] is True
        conn.close()
    
    def test_mark_email_as_replied(self, temp_db):
        """Test marking email as replied"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        processor.db = temp_db
        
        # Save a test email
        email_data = {
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
        
        processor.db.save_email_summary(email_data)
        
        # Mark as replied
        success = processor.mark_email_as_replied('test-email-1')
        
        assert success is True
        
        # Verify in database
        conn = processor.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT is_replied FROM email_summaries WHERE id = ?", ('test-email-1',))
        result = cursor.fetchone()
        
        assert result[0] is True
        conn.close()
    
    def test_get_unread_emails(self, temp_db):
        """Test getting unread emails"""
        config = {
            'email_address': 'test@example.com',
            'password': 'test-password',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        }
        
        processor = EmailProcessor(config)
        processor.db = temp_db
        
        # Save test emails (one read, one unread)
        emails = [
            {
                'id': 'email-1',
                'subject': 'Unread Email',
                'sender': 'Sender 1',
                'sender_email': 'sender1@example.com',
                'received_at': '2024-01-01 10:00:00',
                'category': EmailCategory.WORK.value,
                'priority': PriorityLevel.MEDIUM.value,
                'summary': 'Unread email',
                'is_read': False,
                'is_replied': False,
                'urgency_score': 0.5,
                'action_required': False,
                'follow_up_suggestions': []
            },
            {
                'id': 'email-2',
                'subject': 'Read Email',
                'sender': 'Sender 2',
                'sender_email': 'sender2@example.com',
                'received_at': '2024-01-01 11:00:00',
                'category': EmailCategory.WORK.value,
                'priority': PriorityLevel.MEDIUM.value,
                'summary': 'Read email',
                'is_read': True,
                'is_replied': False,
                'urgency_score': 0.5,
                'action_required': False,
                'follow_up_suggestions': []
            }
        ]
        
        for email in emails:
            processor.db.save_email_summary(email)
        
        unread_emails = processor.get_unread_emails()
        
        assert len(unread_emails) == 1
        assert unread_emails[0]['subject'] == 'Unread Email' 