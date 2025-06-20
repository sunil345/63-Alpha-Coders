import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from app.core.email_processor import EmailProcessor
from app.core.notification_manager import NotificationManager
from app.core.database import db

load_dotenv()

class EmailScheduler:
    def __init__(self):
        self.processor = EmailProcessor()
        self.notification_manager = NotificationManager()
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the scheduler in a separate thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            print("Email scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Email scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        # Schedule daily email processing
        config = db.get_configuration("email_config")
        daily_time = config.get("daily_summary_time", "09:00") if config else "09:00"
        
        schedule.every().day.at(daily_time).do(self._process_daily_emails)
        
        # Schedule periodic email checks (every 2 hours)
        schedule.every(2).hours.do(self._check_new_emails)
        
        # Schedule response reminders (every 6 hours)
        schedule.every(6).hours.do(self._check_response_reminders)
        
        print(f"Scheduled daily email processing at {daily_time}")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _process_daily_emails(self):
        """Process emails and generate daily summary"""
        try:
            print(f"Processing daily emails at {datetime.now()}")
            
            # Process today's emails
            today = datetime.now().strftime('%Y-%m-%d')
            email_summaries = self.processor.process_inbox(today)
            
            if email_summaries:
                # Generate daily summary
                daily_summary = self._generate_daily_summary(email_summaries)
                
                # Save to database
                db.save_daily_summary(daily_summary)
                
                # Send notifications
                self._send_daily_notifications(daily_summary)
                
                print(f"Processed {len(email_summaries)} emails for {today}")
            else:
                print(f"No emails found for {today}")
                
        except Exception as e:
            print(f"Error processing daily emails: {e}")
    
    def _check_new_emails(self):
        """Check for new emails periodically"""
        try:
            print(f"Checking for new emails at {datetime.now()}")
            
            # Process recent emails (last 2 hours)
            recent_time = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            
            # This would typically fetch emails since the last check
            # For now, we'll just process today's emails
            today = datetime.now().strftime('%Y-%m-%d')
            email_summaries = self.processor.process_inbox(today)
            
            # Check for urgent emails
            urgent_emails = [e for e in email_summaries if e.get('priority') in ['high', 'urgent']]
            
            if urgent_emails:
                self._send_urgent_notifications(urgent_emails)
                
        except Exception as e:
            print(f"Error checking new emails: {e}")
    
    def _check_response_reminders(self):
        """Check for emails that need responses"""
        try:
            print(f"Checking response reminders at {datetime.now()}")
            
            config = db.get_configuration("email_config")
            reminder_hours = config.get("response_reminder_hours", 24) if config else 24
            
            # Get emails that haven't been replied to
            # This would typically query the database
            # For now, we'll use a placeholder
            reminder_emails = self.processor.get_response_reminders(reminder_hours)
            
            if reminder_emails:
                self._send_reminder_notifications(reminder_emails)
                
        except Exception as e:
            print(f"Error checking response reminders: {e}")
    
    def _generate_daily_summary(self, email_summaries: list) -> dict:
        """Generate daily summary from email summaries"""
        if not email_summaries:
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_emails': 0,
                'categories': {},
                'urgent_emails': [],
                'unread_emails': [],
                'response_reminders': [],
                'priority_breakdown': {}
            }
        
        # Count categories
        categories = {}
        priority_breakdown = {}
        urgent_emails = []
        unread_emails = []
        response_reminders = []
        
        for summary in email_summaries:
            # Category count
            category = summary.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
            
            # Priority count
            priority = summary.get('priority', 'low')
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
            
            # Urgent emails
            if summary.get('priority') in ['high', 'urgent'] or summary.get('urgency_score', 0) >= 0.7:
                urgent_emails.append(summary)
            
            # Unread emails
            if not summary.get('is_read', False):
                unread_emails.append(summary)
            
            # Response reminders
            if not summary.get('is_replied', False) and summary.get('action_required', False):
                response_reminders.append(summary)
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_emails': len(email_summaries),
            'categories': categories,
            'urgent_emails': urgent_emails,
            'unread_emails': unread_emails,
            'response_reminders': response_reminders,
            'priority_breakdown': priority_breakdown
        }
    
    def _send_daily_notifications(self, daily_summary: dict):
        """Send daily summary notifications"""
        try:
            # Generate natural language summary
            ai_analyzer = self.processor.ai_analyzer
            natural_summary = ai_analyzer.generate_natural_language_summary(
                daily_summary.get('urgent_emails', []) + 
                daily_summary.get('unread_emails', [])
            )
            
            # Prepare notification message
            message = f"📧 Daily Email Summary - {daily_summary['date']}\n\n"
            message += f"📊 Total emails: {daily_summary['total_emails']}\n"
            
            if daily_summary['urgent_emails']:
                message += f"⚠️ Urgent emails: {len(daily_summary['urgent_emails'])}\n"
            
            if daily_summary['unread_emails']:
                message += f"📬 Unread emails: {len(daily_summary['unread_emails'])}\n"
            
            if daily_summary['response_reminders']:
                message += f"🧾 Response reminders: {len(daily_summary['response_reminders'])}\n"
            
            message += f"\n📝 Summary:\n{natural_summary}"
            
            # Send to all configured channels
            self.notification_manager.send_notification("Daily Summary", message)
            
        except Exception as e:
            print(f"Error sending daily notifications: {e}")
    
    def _send_urgent_notifications(self, urgent_emails: list):
        """Send notifications for urgent emails"""
        try:
            if not urgent_emails:
                return
            
            message = f"⚠️ Urgent Email Alert - {datetime.now().strftime('%H:%M')}\n\n"
            
            for email in urgent_emails[:5]:  # Limit to 5 emails
                message += f"📧 {email.get('subject', 'No subject')}\n"
                message += f"   From: {email.get('sender', 'Unknown')}\n"
                message += f"   Priority: {email.get('priority', 'Unknown')}\n\n"
            
            if len(urgent_emails) > 5:
                message += f"... and {len(urgent_emails) - 5} more urgent emails"
            
            self.notification_manager.send_notification("Urgent Emails", message)
            
        except Exception as e:
            print(f"Error sending urgent notifications: {e}")
    
    def _send_reminder_notifications(self, reminder_emails: list):
        """Send notifications for response reminders"""
        try:
            if not reminder_emails:
                return
            
            message = f"🧾 Response Reminders - {datetime.now().strftime('%H:%M')}\n\n"
            
            for email in reminder_emails[:5]:  # Limit to 5 emails
                message += f"📧 {email.get('subject', 'No subject')}\n"
                message += f"   From: {email.get('sender', 'Unknown')}\n"
                message += f"   Received: {email.get('received_at', 'Unknown')}\n\n"
            
            if len(reminder_emails) > 5:
                message += f"... and {len(reminder_emails) - 5} more emails need responses"
            
            self.notification_manager.send_notification("Response Reminders", message)
            
        except Exception as e:
            print(f"Error sending reminder notifications: {e}")
    
    def schedule_custom_task(self, task_func, schedule_time: str):
        """Schedule a custom task"""
        try:
            schedule.every().day.at(schedule_time).do(task_func)
            print(f"Scheduled custom task at {schedule_time}")
        except Exception as e:
            print(f"Error scheduling custom task: {e}")
    
    def get_scheduled_jobs(self) -> list:
        """Get list of scheduled jobs"""
        return schedule.get_jobs()
    
    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        print("Cleared all scheduled jobs") 