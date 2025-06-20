import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.notification_manager import NotificationManager

class TestNotificationManager:
    """Test cases for NotificationManager class"""
    
    def test_init_notification_manager(self):
        """Test NotificationManager initialization"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat_id',
            'whatsapp_api_key': 'test_api_key',
            'whatsapp_phone_number': '+1234567890'
        }
        
        manager = NotificationManager(config)
        
        assert manager.slack_webhook_url == 'https://hooks.slack.com/test'
        assert manager.telegram_bot_token == 'test_token'
        assert manager.telegram_chat_id == 'test_chat_id'
        assert manager.whatsapp_api_key == 'test_api_key'
        assert manager.whatsapp_phone_number == '+1234567890'
    
    @patch('app.core.notification_manager.requests.post')
    def test_send_slack_notification_success(self, mock_post):
        """Test successful Slack notification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response
        
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        success = manager.send_slack_notification("Test message")
        
        assert success is True
        mock_post.assert_called_once()
        
        # Check the call arguments
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://hooks.slack.com/test'
        assert 'text' in call_args[1]['json']
        assert call_args[1]['json']['text'] == "Test message"
    
    @patch('app.core.notification_manager.requests.post')
    def test_send_slack_notification_failure(self, mock_post):
        """Test Slack notification failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        success = manager.send_slack_notification("Test message")
        
        assert success is False
    
    @patch('app.core.notification_manager.requests.post')
    def test_send_slack_notification_exception(self, mock_post):
        """Test Slack notification with exception"""
        mock_post.side_effect = Exception("Network error")
        
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        success = manager.send_slack_notification("Test message")
        
        assert success is False
    
    @patch('app.core.notification_manager.requests.post')
    def test_send_telegram_notification_success(self, mock_post):
        """Test successful Telegram notification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response
        
        config = {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat_id'
        }
        
        manager = NotificationManager(config)
        
        success = manager.send_telegram_notification("Test message")
        
        assert success is True
        mock_post.assert_called_once()
        
        # Check the call arguments
        call_args = mock_post.call_args
        expected_url = f"https://api.telegram.org/bot{config['telegram_bot_token']}/sendMessage"
        assert call_args[0][0] == expected_url
        assert call_args[1]['json']['chat_id'] == 'test_chat_id'
        assert call_args[1]['json']['text'] == "Test message"
    
    @patch('app.core.notification_manager.requests.post')
    def test_send_telegram_notification_failure(self, mock_post):
        """Test Telegram notification failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'ok': False, 'description': 'Bad Request'}
        mock_post.return_value = mock_response
        
        config = {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat_id'
        }
        
        manager = NotificationManager(config)
        
        success = manager.send_telegram_notification("Test message")
        
        assert success is False
    
    @patch('app.core.notification_manager.requests.post')
    def test_send_whatsapp_notification_success(self, mock_post):
        """Test successful WhatsApp notification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        config = {
            'whatsapp_api_key': 'test_api_key',
            'whatsapp_phone_number': '+1234567890'
        }
        
        manager = NotificationManager(config)
        
        success = manager.send_whatsapp_notification("Test message")
        
        assert success is True
        mock_post.assert_called_once()
        
        # Check the call arguments
        call_args = mock_post.call_args
        assert 'api_key' in call_args[1]['json']
        assert call_args[1]['json']['api_key'] == 'test_api_key'
        assert call_args[1]['json']['phone_number'] == '+1234567890'
        assert call_args[1]['json']['message'] == "Test message"
    
    @patch('app.core.notification_manager.requests.post')
    def test_send_whatsapp_notification_failure(self, mock_post):
        """Test WhatsApp notification failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'success': False, 'error': 'Invalid API key'}
        mock_post.return_value = mock_response
        
        config = {
            'whatsapp_api_key': 'test_api_key',
            'whatsapp_phone_number': '+1234567890'
        }
        
        manager = NotificationManager(config)
        
        success = manager.send_whatsapp_notification("Test message")
        
        assert success is False
    
    def test_send_notification_all_channels(self):
        """Test sending notification to all channels"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat_id',
            'whatsapp_api_key': 'test_api_key',
            'whatsapp_phone_number': '+1234567890'
        }
        
        manager = NotificationManager(config)
        
        # Mock all notification methods
        with patch.object(manager, 'send_slack_notification', return_value=True) as mock_slack, \
             patch.object(manager, 'send_telegram_notification', return_value=True) as mock_telegram, \
             patch.object(manager, 'send_whatsapp_notification', return_value=True) as mock_whatsapp:
            
            result = manager.send_notification("Test message", channels=['slack', 'telegram', 'whatsapp'])
            
            assert result['slack'] is True
            assert result['telegram'] is True
            assert result['whatsapp'] is True
            
            mock_slack.assert_called_once_with("Test message")
            mock_telegram.assert_called_once_with("Test message")
            mock_whatsapp.assert_called_once_with("Test message")
    
    def test_send_notification_specific_channels(self):
        """Test sending notification to specific channels"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat_id'
        }
        
        manager = NotificationManager(config)
        
        # Mock notification methods
        with patch.object(manager, 'send_slack_notification', return_value=True) as mock_slack, \
             patch.object(manager, 'send_telegram_notification', return_value=True) as mock_telegram:
            
            result = manager.send_notification("Test message", channels=['slack'])
            
            assert result['slack'] is True
            assert 'telegram' not in result
            
            mock_slack.assert_called_once_with("Test message")
            mock_telegram.assert_not_called()
    
    def test_send_notification_no_channels(self):
        """Test sending notification with no channels specified"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        # Mock notification method
        with patch.object(manager, 'send_slack_notification', return_value=True) as mock_slack:
            
            result = manager.send_notification("Test message")
            
            assert result['slack'] is True
            mock_slack.assert_called_once_with("Test message")
    
    def test_send_notification_invalid_channel(self):
        """Test sending notification to invalid channel"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        # Mock notification method
        with patch.object(manager, 'send_slack_notification', return_value=True) as mock_slack:
            
            result = manager.send_notification("Test message", channels=['invalid_channel'])
            
            assert result == {}
            mock_slack.assert_not_called()
    
    def test_send_daily_summary_notification(self):
        """Test sending daily summary notification"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        daily_summary = {
            'date': '2024-01-01',
            'total_emails': 5,
            'categories': {'work': 3, 'personal': 2},
            'urgent_emails': [],
            'unread_emails': [],
            'response_reminders': [],
            'priority_breakdown': {'low': 2, 'medium': 3}
        }
        
        # Mock notification method
        with patch.object(manager, 'send_slack_notification', return_value=True) as mock_slack:
            
            success = manager.send_daily_summary_notification(daily_summary)
            
            assert success is True
            mock_slack.assert_called_once()
            
            # Check that the message contains summary information
            call_args = mock_slack.call_args
            message = call_args[1]['json']['text']
            assert '2024-01-01' in message
            assert '5' in message  # total emails
            assert 'work' in message.lower()
    
    def test_send_urgent_email_notification(self):
        """Test sending urgent email notification"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        urgent_email = {
            'subject': 'URGENT: System Down',
            'sender': 'Admin',
            'sender_email': 'admin@company.com',
            'received_at': '2024-01-01 10:00:00',
            'summary': 'System is down and needs immediate attention'
        }
        
        # Mock notification method
        with patch.object(manager, 'send_slack_notification', return_value=True) as mock_slack:
            
            success = manager.send_urgent_email_notification(urgent_email)
            
            assert success is True
            mock_slack.assert_called_once()
            
            # Check that the message contains urgent email information
            call_args = mock_slack.call_args
            message = call_args[1]['json']['text']
            assert 'URGENT' in message
            assert 'System Down' in message
            assert 'admin@company.com' in message
    
    def test_send_response_reminder_notification(self):
        """Test sending response reminder notification"""
        config = {
            'slack_webhook_url': 'https://hooks.slack.com/test'
        }
        
        manager = NotificationManager(config)
        
        reminder_email = {
            'subject': 'Project Update',
            'sender': 'Colleague',
            'sender_email': 'colleague@company.com',
            'received_at': '2024-01-01 10:00:00',
            'hours_since_received': 25
        }
        
        # Mock notification method
        with patch.object(manager, 'send_slack_notification', return_value=True) as mock_slack:
            
            success = manager.send_response_reminder_notification(reminder_email)
            
            assert success is True
            mock_slack.assert_called_once()
            
            # Check that the message contains reminder information
            call_args = mock_slack.call_args
            message = call_args[1]['json']['text']
            assert 'reminder' in message.lower()
            assert 'Project Update' in message
            assert '25' in message  # hours since received
    
    def test_format_daily_summary_message(self):
        """Test daily summary message formatting"""
        config = {}
        manager = NotificationManager(config)
        
        daily_summary = {
            'date': '2024-01-01',
            'total_emails': 5,
            'categories': {'work': 3, 'personal': 2},
            'urgent_emails': [],
            'unread_emails': [],
            'response_reminders': [],
            'priority_breakdown': {'low': 2, 'medium': 3}
        }
        
        message = manager._format_daily_summary_message(daily_summary)
        
        assert '2024-01-01' in message
        assert '5' in message  # total emails
        assert 'work' in message.lower()
        assert 'personal' in message.lower()
        assert '3' in message  # work emails
        assert '2' in message  # personal emails
    
    def test_format_urgent_email_message(self):
        """Test urgent email message formatting"""
        config = {}
        manager = NotificationManager(config)
        
        urgent_email = {
            'subject': 'URGENT: System Down',
            'sender': 'Admin',
            'sender_email': 'admin@company.com',
            'received_at': '2024-01-01 10:00:00',
            'summary': 'System is down and needs immediate attention'
        }
        
        message = manager._format_urgent_email_message(urgent_email)
        
        assert 'URGENT' in message
        assert 'System Down' in message
        assert 'admin@company.com' in message
        assert 'System is down' in message
    
    def test_format_response_reminder_message(self):
        """Test response reminder message formatting"""
        config = {}
        manager = NotificationManager(config)
        
        reminder_email = {
            'subject': 'Project Update',
            'sender': 'Colleague',
            'sender_email': 'colleague@company.com',
            'received_at': '2024-01-01 10:00:00',
            'hours_since_received': 25
        }
        
        message = manager._format_response_reminder_message(reminder_email)
        
        assert 'reminder' in message.lower()
        assert 'Project Update' in message
        assert 'colleague@company.com' in message
        assert '25' in message  # hours since received 