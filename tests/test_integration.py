import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import tempfile
import os

class TestIntegration:
    """Integration tests for the complete email agent system"""
    
    def test_full_email_processing_workflow(self, client, temp_db):
        """Test complete email processing workflow"""
        # Mock all external dependencies
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class, \
             patch('app.routers.email_analysis.Database') as mock_db_class, \
             patch('app.routers.notifications.NotificationManager') as mock_notification_class:
            
            # Setup mocks
            mock_processor = Mock()
            mock_processor.process_emails.return_value = {
                'total_processed': 3,
                'total_saved': 3,
                'errors': []
            }
            mock_processor_class.return_value = mock_processor
            
            mock_db = Mock()
            mock_db.get_daily_summary.return_value = {
                'date': '2024-01-01',
                'total_emails': 3,
                'categories': {'work': 2, 'personal': 1},
                'urgent_emails': [],
                'unread_emails': [],
                'response_reminders': [],
                'priority_breakdown': {'low': 1, 'medium': 2}
            }
            mock_db.get_emails_by_date.return_value = [
                {
                    'id': 'email-1',
                    'subject': 'Work Email',
                    'sender': 'Colleague',
                    'sender_email': 'colleague@company.com',
                    'received_at': '2024-01-01 10:00:00',
                    'category': 'work',
                    'priority': 'medium',
                    'summary': 'Work related email',
                    'is_read': False,
                    'is_replied': False,
                    'urgency_score': 0.5,
                    'action_required': False,
                    'follow_up_suggestions': []
                }
            ]
            mock_db_class.return_value = mock_db
            
            mock_notification = Mock()
            mock_notification.send_daily_summary_notification.return_value = True
            mock_notification_class.return_value = mock_notification
            
            # Step 1: Process emails
            response = client.post("/api/email/process-emails", json={
                'email_address': 'test@example.com',
                'password': 'test-password',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'use_ssl': True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['total_processed'] == 3
            assert data['total_saved'] == 3
            
            # Step 2: Get daily summary
            response = client.get("/api/email/daily-summary/2024-01-01")
            
            assert response.status_code == 200
            data = response.json()
            assert data['total_emails'] == 3
            assert data['categories']['work'] == 2
            
            # Step 3: Get emails by date
            response = client.get("/api/email/emails/2024-01-01")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['subject'] == 'Work Email'
            
            # Step 4: Send daily summary notification
            response = client.post("/api/notifications/daily-summary", json={
                'date': '2024-01-01',
                'total_emails': 3,
                'categories': {'work': 2, 'personal': 1},
                'urgent_emails': [],
                'unread_emails': [],
                'response_reminders': [],
                'priority_breakdown': {'low': 1, 'medium': 2}
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_urgent_email_notification_workflow(self, client):
        """Test urgent email notification workflow"""
        with patch('app.routers.notifications.NotificationManager') as mock_notification_class:
            mock_notification = Mock()
            mock_notification.send_urgent_email_notification.return_value = True
            mock_notification_class.return_value = mock_notification
            
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
    
    def test_voice_summary_generation_workflow(self, client):
        """Test voice summary generation workflow"""
        with patch('app.routers.voice.text_to_speech') as mock_tts, \
             patch('app.routers.voice.get_available_voices') as mock_get_voices:
            
            mock_tts.return_value = b'audio_data'
            mock_get_voices.return_value = [
                {'name': 'en-US-Standard-A', 'language': 'en-US'},
                {'name': 'en-US-Standard-B', 'language': 'en-US'}
            ]
            
            # Get available voices
            response = client.get("/api/voice/available-voices")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            
            # Generate voice summary
            response = client.post("/api/voice/generate-voice-summary", json={
                'text': 'You have 3 emails today. 2 work emails and 1 personal email.',
                'voice': 'en-US-Standard-A'
            })
            
            assert response.status_code == 200
            assert response.headers['content-type'] == 'audio/mpeg'
    
    def test_configuration_management_workflow(self, client):
        """Test configuration management workflow"""
        with patch('app.routers.config.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.get_configuration.return_value = {
                'email_address': 'test@example.com',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993
            }
            mock_db.save_configuration.return_value = True
            mock_db.get_vip_contacts.return_value = [
                {
                    'email': 'vip@example.com',
                    'name': 'VIP User',
                    'priority_level': 'high'
                }
            ]
            mock_db.add_vip_contact.return_value = True
            mock_db.delete_vip_contact.return_value = True
            mock_db_class.return_value = mock_db
            
            # Get configuration
            response = client.get("/api/config/configuration/email_config")
            
            assert response.status_code == 200
            data = response.json()
            assert data['email_address'] == 'test@example.com'
            
            # Save configuration
            config_data = {
                'email_address': 'new@example.com',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993
            }
            
            response = client.post("/api/config/configuration/email_config", json=config_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            
            # Get VIP contacts
            response = client.get("/api/config/vip-contacts")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['email'] == 'vip@example.com'
            
            # Add VIP contact
            new_vip = {
                'email': 'newvip@example.com',
                'name': 'New VIP User',
                'priority_level': 'medium'
            }
            
            response = client.post("/api/config/vip-contacts", json=new_vip)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            
            # Delete VIP contact
            response = client.delete("/api/config/vip-contacts/vip@example.com")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_error_handling_integration(self, client):
        """Test error handling across the system"""
        # Test email processing with connection error
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_emails.side_effect = Exception("IMAP connection failed")
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
        
        # Test notification with service error
        with patch('app.routers.notifications.NotificationManager') as mock_notification_class:
            mock_notification = Mock()
            mock_notification.send_notification.side_effect = Exception("Slack API error")
            mock_notification_class.return_value = mock_notification
            
            response = client.post("/api/notifications/send", json={
                'message': 'Test notification',
                'channels': ['slack']
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'error' in data
        
        # Test voice generation with TTS error
        with patch('app.routers.voice.text_to_speech') as mock_tts:
            mock_tts.side_effect = Exception("TTS service unavailable")
            
            response = client.post("/api/voice/generate-voice-summary", json={
                'text': 'Test text',
                'voice': 'en-US-Standard-A'
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'error' in data
    
    def test_data_consistency_integration(self, client, temp_db):
        """Test data consistency across the system"""
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class, \
             patch('app.routers.email_analysis.Database') as mock_db_class:
            
            # Setup consistent test data
            test_emails = [
                {
                    'id': 'email-1',
                    'subject': 'Work Email 1',
                    'sender': 'Colleague 1',
                    'sender_email': 'colleague1@company.com',
                    'received_at': '2024-01-01 10:00:00',
                    'category': 'work',
                    'priority': 'medium',
                    'summary': 'Work related email 1',
                    'is_read': False,
                    'is_replied': False,
                    'urgency_score': 0.5,
                    'action_required': False,
                    'follow_up_suggestions': []
                },
                {
                    'id': 'email-2',
                    'subject': 'Work Email 2',
                    'sender': 'Colleague 2',
                    'sender_email': 'colleague2@company.com',
                    'received_at': '2024-01-01 11:00:00',
                    'category': 'work',
                    'priority': 'high',
                    'summary': 'Work related email 2',
                    'is_read': False,
                    'is_replied': False,
                    'urgency_score': 0.8,
                    'action_required': True,
                    'follow_up_suggestions': ['Reply urgently']
                }
            ]
            
            mock_processor = Mock()
            mock_processor.process_emails.return_value = {
                'total_processed': 2,
                'total_saved': 2,
                'errors': []
            }
            mock_processor_class.return_value = mock_processor
            
            mock_db = Mock()
            mock_db.get_daily_summary.return_value = {
                'date': '2024-01-01',
                'total_emails': 2,
                'categories': {'work': 2},
                'urgent_emails': [test_emails[1]],  # Second email is urgent
                'unread_emails': test_emails,
                'response_reminders': [test_emails[1]],  # Second email needs response
                'priority_breakdown': {'medium': 1, 'high': 1}
            }
            mock_db.get_emails_by_date.return_value = test_emails
            mock_db_class.return_value = mock_db
            
            # Process emails
            response = client.post("/api/email/process-emails", json={
                'email_address': 'test@example.com',
                'password': 'test-password',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'use_ssl': True
            })
            
            assert response.status_code == 200
            assert response.json()['total_processed'] == 2
            
            # Get daily summary and verify consistency
            response = client.get("/api/email/daily-summary/2024-01-01")
            
            assert response.status_code == 200
            data = response.json()
            assert data['total_emails'] == 2
            assert data['categories']['work'] == 2
            assert len(data['urgent_emails']) == 1
            assert len(data['unread_emails']) == 2
            assert len(data['response_reminders']) == 1
            
            # Get emails by date and verify consistency
            response = client.get("/api/email/emails/2024-01-01")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]['subject'] == 'Work Email 1'
            assert data[1]['subject'] == 'Work Email 2'
            assert data[1]['urgency_score'] == 0.8
            assert data[1]['action_required'] is True
    
    def test_performance_integration(self, client):
        """Test system performance with multiple requests"""
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class, \
             patch('app.routers.email_analysis.Database') as mock_db_class:
            
            mock_processor = Mock()
            mock_processor.process_emails.return_value = {
                'total_processed': 100,
                'total_saved': 100,
                'errors': []
            }
            mock_processor_class.return_value = mock_processor
            
            mock_db = Mock()
            mock_db.get_daily_summary.return_value = {
                'date': '2024-01-01',
                'total_emails': 100,
                'categories': {'work': 50, 'personal': 30, 'promotions': 20},
                'urgent_emails': [],
                'unread_emails': [],
                'response_reminders': [],
                'priority_breakdown': {'low': 30, 'medium': 50, 'high': 20}
            }
            mock_db_class.return_value = mock_db
            
            # Test multiple concurrent requests
            import time
            start_time = time.time()
            
            # Make multiple requests
            for i in range(10):
                response = client.get("/api/email/daily-summary/2024-01-01")
                assert response.status_code == 200
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verify performance (should complete within reasonable time)
            assert execution_time < 5.0  # Should complete within 5 seconds
    
    def test_security_integration(self, client):
        """Test security aspects of the system"""
        # Test with invalid credentials
        with patch('app.routers.email_analysis.EmailProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_emails.side_effect = Exception("Invalid credentials")
            mock_processor_class.return_value = mock_processor
            
            response = client.post("/api/email/process-emails", json={
                'email_address': 'test@example.com',
                'password': 'wrong-password',
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'use_ssl': True
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'error' in data
        
        # Test with missing required fields
        response = client.post("/api/email/process-emails", json={
            'email_address': 'test@example.com'
            # Missing password and other required fields
        })
        
        assert response.status_code == 422  # Validation error
        
        # Test with invalid date format
        response = client.get("/api/email/daily-summary/invalid-date")
        
        assert response.status_code == 422  # Validation error 