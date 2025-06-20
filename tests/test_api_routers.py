import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
from app.models import EmailCategory, PriorityLevel

class TestEmailAnalysisRouter:
    """Test cases for email analysis router"""
    
    def test_process_emails_endpoint(self, client, temp_db):
        """Test /process-emails endpoint"""
        # Mock the email processor
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_emails.return_value = {
                'total_processed': 5,
                'total_saved': 5,
                'errors': []
            }
            mock_processor_class.return_value = mock_processor
            
            response = client.post("/api/email/process-emails", json={
                'email_address': 'test@example.com',
                'password': 'test-password',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'use_ssl': True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['total_processed'] == 5
            assert data['total_saved'] == 5
            assert len(data['errors']) == 0
    
    def test_process_emails_endpoint_error(self, client):
        """Test /process-emails endpoint with error"""
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_emails.side_effect = Exception("Connection failed")
            mock_processor_class.return_value = mock_processor
            
            response = client.post("/api/email/process-emails", json={
                'email_address': 'test@example.com',
                'password': 'test-password',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'use_ssl': True
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'error' in data
    
    def test_get_daily_summary_endpoint(self, client, temp_db):
        """Test /daily-summary/{date} endpoint"""
        # Mock the database
        with patch('app.routers.email_analysis.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.get_daily_summary.return_value = {
                'date': '2024-01-01',
                'total_emails': 5,
                'categories': {'work': 3, 'personal': 2},
                'urgent_emails': [],
                'unread_emails': [],
                'response_reminders': [],
                'priority_breakdown': {'low': 2, 'medium': 3}
            }
            mock_db_class.return_value = mock_db
            
            response = client.get("/api/email/daily-summary/2024-01-01")
            
            assert response.status_code == 200
            data = response.json()
            assert data['date'] == '2024-01-01'
            assert data['total_emails'] == 5
    
    def test_get_daily_summary_endpoint_not_found(self, client):
        """Test /daily-summary/{date} endpoint with no data"""
        with patch('app.routers.email_analysis.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.get_daily_summary.return_value = None
            mock_db_class.return_value = mock_db
            
            response = client.get("/api/email/daily-summary/2024-01-01")
            
            assert response.status_code == 404
            data = response.json()
            assert 'error' in data
    
    def test_get_emails_by_date_endpoint(self, client, temp_db):
        """Test /emails/{date} endpoint"""
        with patch('app.routers.email_analysis.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.get_emails_by_date.return_value = [
                {
                    'id': 'email-1',
                    'subject': 'Test Email',
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
            ]
            mock_db_class.return_value = mock_db
            
            response = client.get("/api/email/emails/2024-01-01")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['subject'] == 'Test Email'
    
    def test_mark_email_as_read_endpoint(self, client, temp_db):
        """Test /emails/{email_id}/mark-read endpoint"""
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.mark_email_as_read.return_value = True
            mock_processor_class.return_value = mock_processor
            
            response = client.put("/api/email/emails/test-email-1/mark-read")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_mark_email_as_replied_endpoint(self, client, temp_db):
        """Test /emails/{email_id}/mark-replied endpoint"""
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.mark_email_as_replied.return_value = True
            mock_processor_class.return_value = mock_processor
            
            response = client.put("/api/email/emails/test-email-1/mark-replied")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True

class TestNotificationsRouter:
    """Test cases for notifications router"""
    
    def test_send_notification_endpoint(self, client):
        """Test /send endpoint"""
        with patch('app.routers.notifications.NotificationManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.send_notification.return_value = {
                'slack': True,
                'telegram': True
            }
            mock_manager_class.return_value = mock_manager
            
            response = client.post("/api/notifications/send", json={
                'message': 'Test notification',
                'channels': ['slack', 'telegram']
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['slack'] is True
            assert data['telegram'] is True
    
    def test_send_notification_endpoint_error(self, client):
        """Test /send endpoint with error"""
        with patch('app.routers.notifications.NotificationManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.send_notification.side_effect = Exception("Notification failed")
            mock_manager_class.return_value = mock_manager
            
            response = client.post("/api/notifications/send", json={
                'message': 'Test notification',
                'channels': ['slack']
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'error' in data
    
    def test_send_daily_summary_notification_endpoint(self, client):
        """Test /daily-summary endpoint"""
        with patch('app.routers.notifications.NotificationManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.send_daily_summary_notification.return_value = True
            mock_manager_class.return_value = mock_manager
            
            daily_summary = {
                'date': '2024-01-01',
                'total_emails': 5,
                'categories': {'work': 3, 'personal': 2},
                'urgent_emails': [],
                'unread_emails': [],
                'response_reminders': [],
                'priority_breakdown': {'low': 2, 'medium': 3}
            }
            
            response = client.post("/api/notifications/daily-summary", json=daily_summary)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_send_urgent_email_notification_endpoint(self, client):
        """Test /urgent-email endpoint"""
        with patch('app.routers.notifications.NotificationManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.send_urgent_email_notification.return_value = True
            mock_manager_class.return_value = mock_manager
            
            urgent_email = {
                'subject': 'URGENT: System Down',
                'sender': 'Admin',
                'sender_email': 'admin@company.com',
                'received_at': '2024-01-01 10:00:00',
                'summary': 'System is down and needs immediate attention'
            }
            
            response = client.post("/api/notifications/urgent-email", json=urgent_email)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True

class TestVoiceRouter:
    """Test cases for voice router"""
    
    def test_generate_voice_summary_endpoint(self, client):
        """Test /generate-voice-summary endpoint"""
        with patch('app.routers.voice.text_to_speech') as mock_tts:
            mock_tts.return_value = b'audio_data'
            
            response = client.post("/api/voice/generate-voice-summary", json={
                'text': 'This is a test summary for voice generation.',
                'voice': 'en-US-Standard-A'
            })
            
            assert response.status_code == 200
            assert response.headers['content-type'] == 'audio/mpeg'
    
    def test_generate_voice_summary_endpoint_error(self, client):
        """Test /generate-voice-summary endpoint with error"""
        with patch('app.routers.voice.text_to_speech') as mock_tts:
            mock_tts.side_effect = Exception("TTS service error")
            
            response = client.post("/api/voice/generate-voice-summary", json={
                'text': 'Test text',
                'voice': 'en-US-Standard-A'
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'error' in data
    
    def test_get_available_voices_endpoint(self, client):
        """Test /available-voices endpoint"""
        with patch('app.routers.voice.get_available_voices') as mock_get_voices:
            mock_get_voices.return_value = [
                {'name': 'en-US-Standard-A', 'language': 'en-US'},
                {'name': 'en-US-Standard-B', 'language': 'en-US'}
            ]
            
            response = client.get("/api/voice/available-voices")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]['name'] == 'en-US-Standard-A'

class TestConfigRouter:
    """Test cases for config router"""
    
    def test_get_configuration_endpoint(self, client, temp_db):
        """Test /configuration/{config_key} endpoint"""
        with patch('app.routers.config.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.get_configuration.return_value = {
                'email_address': 'test@example.com',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993
            }
            mock_db_class.return_value = mock_db
            
            response = client.get("/api/config/configuration/email_config")
            
            assert response.status_code == 200
            data = response.json()
            assert data['email_address'] == 'test@example.com'
            assert data['imap_server'] == 'imap.gmail.com'
    
    def test_get_configuration_endpoint_not_found(self, client):
        """Test /configuration/{config_key} endpoint with no data"""
        with patch('app.routers.config.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.get_configuration.return_value = None
            mock_db_class.return_value = mock_db
            
            response = client.get("/api/config/configuration/nonexistent_config")
            
            assert response.status_code == 404
            data = response.json()
            assert 'error' in data
    
    def test_save_configuration_endpoint(self, client, temp_db):
        """Test /configuration/{config_key} endpoint (POST)"""
        with patch('app.routers.config.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.save_configuration.return_value = True
            mock_db_class.return_value = mock_db
            
            config_data = {
                'email_address': 'test@example.com',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993
            }
            
            response = client.post("/api/config/configuration/email_config", json=config_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_get_vip_contacts_endpoint(self, client, temp_db):
        """Test /vip-contacts endpoint (GET)"""
        with patch('app.routers.config.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.get_vip_contacts.return_value = [
                {
                    'email': 'vip@example.com',
                    'name': 'VIP User',
                    'priority_level': 'high'
                }
            ]
            mock_db_class.return_value = mock_db
            
            response = client.get("/api/config/vip-contacts")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['email'] == 'vip@example.com'
    
    def test_add_vip_contact_endpoint(self, client, temp_db):
        """Test /vip-contacts endpoint (POST)"""
        with patch('app.routers.config.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.add_vip_contact.return_value = True
            mock_db_class.return_value = mock_db
            
            vip_contact = {
                'email': 'newvip@example.com',
                'name': 'New VIP User',
                'priority_level': 'medium'
            }
            
            response = client.post("/api/config/vip-contacts", json=vip_contact)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_delete_vip_contact_endpoint(self, client, temp_db):
        """Test /vip-contacts/{email} endpoint (DELETE)"""
        with patch('app.routers.config.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.delete_vip_contact.return_value = True
            mock_db_class.return_value = mock_db
            
            response = client.delete("/api/config/vip-contacts/vip@example.com")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True 