import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app.core.scheduler import EmailScheduler

class TestEmailScheduler:
    """Test cases for EmailScheduler class"""
    
    def test_init_scheduler(self):
        """Test EmailScheduler initialization"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        assert scheduler.daily_summary_time == '09:00'
        assert scheduler.response_reminder_hours == 24
        assert scheduler.follow_up_reminder_days == 3
        assert scheduler.check_interval_minutes == 30
        assert scheduler.is_running is False
    
    def test_start_scheduler(self):
        """Test starting the scheduler"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Mock the threading
        with patch('app.core.scheduler.threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            scheduler.start()
            
            assert scheduler.is_running is True
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    def test_stop_scheduler(self):
        """Test stopping the scheduler"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        scheduler.is_running = True
        
        scheduler.stop()
        
        assert scheduler.is_running is False
    
    def test_schedule_daily_summary(self):
        """Test scheduling daily summary"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Mock the email processor and notification manager
        mock_processor = Mock()
        mock_notification_manager = Mock()
        
        scheduler.email_processor = mock_processor
        scheduler.notification_manager = mock_notification_manager
        
        # Mock the daily summary generation
        mock_processor.generate_daily_summary.return_value = {
            'date': '2024-01-01',
            'total_emails': 5,
            'categories': {'work': 3, 'personal': 2},
            'urgent_emails': [],
            'unread_emails': [],
            'response_reminders': [],
            'priority_breakdown': {'low': 2, 'medium': 3}
        }
        
        mock_notification_manager.send_daily_summary_notification.return_value = True
        
        # Test scheduling
        scheduler.schedule_daily_summary()
        
        # Verify that the daily summary was generated and notification sent
        mock_processor.generate_daily_summary.assert_called_once()
        mock_notification_manager.send_daily_summary_notification.assert_called_once()
    
    def test_check_urgent_emails(self):
        """Test checking for urgent emails"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Mock the email processor and notification manager
        mock_processor = Mock()
        mock_notification_manager = Mock()
        
        scheduler.email_processor = mock_processor
        scheduler.notification_manager = mock_notification_manager
        
        # Mock urgent emails
        urgent_emails = [
            {
                'id': 'urgent-1',
                'subject': 'URGENT: System Down',
                'sender': 'Admin',
                'sender_email': 'admin@company.com',
                'received_at': '2024-01-01 10:00:00',
                'summary': 'System is down and needs immediate attention'
            }
        ]
        
        mock_processor.get_urgent_emails.return_value = urgent_emails
        mock_notification_manager.send_urgent_email_notification.return_value = True
        
        # Test checking urgent emails
        scheduler.check_urgent_emails()
        
        # Verify that urgent emails were checked and notifications sent
        mock_processor.get_urgent_emails.assert_called_once()
        mock_notification_manager.send_urgent_email_notification.assert_called_once_with(urgent_emails[0])
    
    def test_check_response_reminders(self):
        """Test checking for response reminders"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Mock the email processor and notification manager
        mock_processor = Mock()
        mock_notification_manager = Mock()
        
        scheduler.email_processor = mock_processor
        scheduler.notification_manager = mock_notification_manager
        
        # Mock emails needing response reminders
        reminder_emails = [
            {
                'id': 'reminder-1',
                'subject': 'Project Update',
                'sender': 'Colleague',
                'sender_email': 'colleague@company.com',
                'received_at': '2024-01-01 10:00:00',
                'hours_since_received': 25
            }
        ]
        
        mock_processor.get_response_reminders.return_value = reminder_emails
        mock_notification_manager.send_response_reminder_notification.return_value = True
        
        # Test checking response reminders
        scheduler.check_response_reminders()
        
        # Verify that response reminders were checked and notifications sent
        mock_processor.get_response_reminders.assert_called_once_with(24)  # response_reminder_hours
        mock_notification_manager.send_response_reminder_notification.assert_called_once_with(reminder_emails[0])
    
    def test_check_follow_up_reminders(self):
        """Test checking for follow-up reminders"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Mock the email processor and notification manager
        mock_processor = Mock()
        mock_notification_manager = Mock()
        
        scheduler.email_processor = mock_processor
        scheduler.notification_manager = mock_notification_manager
        
        # Mock emails needing follow-up reminders
        follow_up_emails = [
            {
                'id': 'followup-1',
                'subject': 'Meeting Follow-up',
                'sender': 'Manager',
                'sender_email': 'manager@company.com',
                'received_at': '2024-01-01 10:00:00',
                'days_since_received': 4
            }
        ]
        
        mock_processor.get_follow_up_reminders.return_value = follow_up_emails
        mock_notification_manager.send_follow_up_reminder_notification.return_value = True
        
        # Test checking follow-up reminders
        scheduler.check_follow_up_reminders()
        
        # Verify that follow-up reminders were checked and notifications sent
        mock_processor.get_follow_up_reminders.assert_called_once_with(3)  # follow_up_reminder_days
        mock_notification_manager.send_follow_up_reminder_notification.assert_called_once_with(follow_up_emails[0])
    
    def test_run_scheduler_loop(self):
        """Test the main scheduler loop"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        scheduler.is_running = True
        
        # Mock all the check methods
        with patch.object(scheduler, 'check_urgent_emails') as mock_urgent, \
             patch.object(scheduler, 'check_response_reminders') as mock_response, \
             patch.object(scheduler, 'check_follow_up_reminders') as mock_followup, \
             patch.object(scheduler, 'schedule_daily_summary') as mock_daily, \
             patch('app.core.scheduler.time.sleep') as mock_sleep:
            
            # Mock sleep to raise an exception after first iteration to stop the loop
            mock_sleep.side_effect = KeyboardInterrupt()
            
            # Run the scheduler loop
            scheduler._run_scheduler_loop()
            
            # Verify that all check methods were called
            mock_urgent.assert_called_once()
            mock_response.assert_called_once()
            mock_followup.assert_called_once()
            mock_daily.assert_called_once()
            mock_sleep.assert_called_once_with(30 * 60)  # check_interval_minutes * 60 seconds
    
    def test_is_daily_summary_time(self):
        """Test checking if it's time for daily summary"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Test with current time at 09:00
        with patch('app.core.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 9, 0, 0)
            mock_datetime.strptime = datetime.strptime
            
            is_time = scheduler._is_daily_summary_time()
            assert is_time is True
        
        # Test with current time at 10:00
        with patch('app.core.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0)
            mock_datetime.strptime = datetime.strptime
            
            is_time = scheduler._is_daily_summary_time()
            assert is_time is False
    
    def test_get_next_daily_summary_time(self):
        """Test getting next daily summary time"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Test with current time before 09:00
        with patch('app.core.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 8, 0, 0)
            mock_datetime.strptime = datetime.strptime
            
            next_time = scheduler._get_next_daily_summary_time()
            expected_time = datetime(2024, 1, 1, 9, 0, 0)
            assert next_time == expected_time
        
        # Test with current time after 09:00
        with patch('app.core.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0)
            mock_datetime.strptime = datetime.strptime
            
            next_time = scheduler._get_next_daily_summary_time()
            expected_time = datetime(2024, 1, 2, 9, 0, 0)  # Next day at 09:00
            assert next_time == expected_time
    
    def test_scheduler_with_no_emails(self):
        """Test scheduler behavior when no emails are found"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Mock the email processor and notification manager
        mock_processor = Mock()
        mock_notification_manager = Mock()
        
        scheduler.email_processor = mock_processor
        scheduler.notification_manager = mock_notification_manager
        
        # Mock empty results
        mock_processor.get_urgent_emails.return_value = []
        mock_processor.get_response_reminders.return_value = []
        mock_processor.get_follow_up_reminders.return_value = []
        
        # Test checking with no emails
        scheduler.check_urgent_emails()
        scheduler.check_response_reminders()
        scheduler.check_follow_up_reminders()
        
        # Verify that methods were called but no notifications sent
        mock_processor.get_urgent_emails.assert_called_once()
        mock_processor.get_response_reminders.assert_called_once()
        mock_processor.get_follow_up_reminders.assert_called_once()
        
        # No notifications should be sent
        mock_notification_manager.send_urgent_email_notification.assert_not_called()
        mock_notification_manager.send_response_reminder_notification.assert_not_called()
        mock_notification_manager.send_follow_up_reminder_notification.assert_not_called()
    
    def test_scheduler_error_handling(self):
        """Test scheduler error handling"""
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        scheduler = EmailScheduler(config)
        
        # Mock the email processor to raise an exception
        mock_processor = Mock()
        mock_processor.get_urgent_emails.side_effect = Exception("Database error")
        
        scheduler.email_processor = mock_processor
        
        # Test that the scheduler handles errors gracefully
        try:
            scheduler.check_urgent_emails()
        except Exception:
            pytest.fail("Scheduler should handle exceptions gracefully")
    
    def test_scheduler_configuration_validation(self):
        """Test scheduler configuration validation"""
        # Test with invalid time format
        config = {
            'daily_summary_time': 'invalid_time',
            'response_reminder_hours': 24,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        with pytest.raises(ValueError):
            EmailScheduler(config)
        
        # Test with negative values
        config = {
            'daily_summary_time': '09:00',
            'response_reminder_hours': -1,
            'follow_up_reminder_days': 3,
            'check_interval_minutes': 30
        }
        
        with pytest.raises(ValueError):
            EmailScheduler(config) 