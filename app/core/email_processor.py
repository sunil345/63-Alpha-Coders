import imaplib
import email
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv

from app.models import EmailCategory, PriorityLevel, EmailSummary
from app.core.database import db
from app.core.ai_analyzer import AIAnalyzer
from app.core.email_categorizer import EmailCategorizer

load_dotenv()

class EmailProcessor:
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.categorizer = EmailCategorizer()
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load email configuration from database"""
        config = db.get_configuration("email_config")
        if not config:
            # Default configuration
            config = {
                "email_address": os.getenv("EMAIL_ADDRESS", ""),
                "password": os.getenv("EMAIL_PASSWORD", ""),
                "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
                "imap_port": int(os.getenv("IMAP_PORT", "993")),
                "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "use_ssl": True,
                "vip_contacts": [],
                "auto_categorize": True,
                "daily_summary_time": "09:00",
                "response_reminder_hours": 24,
                "follow_up_reminder_days": 3
            }
        return config

    def connect_imap(self):
        """Connect to IMAP server"""
        try:
            if self.config["use_ssl"]:
                imap = imaplib.IMAP4_SSL(self.config["imap_server"], self.config["imap_port"])
            else:
                imap = imaplib.IMAP4(self.config["imap_server"], self.config["imap_port"])
            
            imap.login(self.config["email_address"], self.config["password"])
            return imap
        except Exception as e:
            raise Exception(f"Failed to connect to IMAP server: {str(e)}")

    def fetch_emails(self, date: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch emails from inbox"""
        imap = self.connect_imap()
        emails = []
        
        try:
            imap.select('INBOX')
            
            # Search criteria
            if date:
                search_criteria = f'(SINCE "{date}")'
            else:
                search_criteria = 'ALL'
            
            _, message_numbers = imap.search(None, search_criteria)
            
            # Get the latest emails
            email_list = message_numbers[0].split()[-limit:] if limit else message_numbers[0].split()
            
            for num in email_list:
                try:
                    _, msg_data = imap.fetch(num, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    email_data = self._parse_email(email_message)
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    print(f"Error parsing email {num}: {str(e)}")
                    continue
                    
        finally:
            imap.logout()
            
        return emails

    def _parse_email(self, email_message) -> Optional[Dict[str, Any]]:
        """Parse email message and extract relevant information"""
        try:
            # Extract basic information
            subject = email_message.get('Subject', '')
            sender = email_message.get('From', '')
            date_str = email_message.get('Date', '')
            message_id = email_message.get('Message-ID', str(uuid.uuid4()))
            
            # Parse sender email
            sender_email = self._extract_email(sender)
            sender_name = self._extract_name(sender)
            
            # Parse date
            try:
                received_date = email.utils.parsedate_to_datetime(date_str)
            except:
                received_date = datetime.now()
            
            # Extract email body
            body = self._extract_body(email_message)
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender_name,
                'sender_email': sender_email,
                'received_at': received_date,
                'body': body,
                'raw_message': email_message
            }
            
        except Exception as e:
            print(f"Error parsing email: {str(e)}")
            return None

    def _extract_email(self, sender: str) -> str:
        """Extract email address from sender string"""
        email_pattern = r'<(.+?)>'
        match = re.search(email_pattern, sender)
        if match:
            return match.group(1)
        return sender

    def _extract_name(self, sender: str) -> str:
        """Extract name from sender string"""
        name_pattern = r'^([^<]+)'
        match = re.search(name_pattern, sender)
        if match:
            return match.group(1).strip()
        return "Unknown"

    def _extract_body(self, email_message) -> str:
        """Extract email body content"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
            
        return body

    def analyze_email(self, email_data: Dict[str, Any]) -> EmailSummary:
        """Analyze email and create summary"""
        # Categorize email
        category = self.categorizer.categorize_email(
            email_data['subject'], 
            email_data['body'], 
            email_data['sender_email']
        )
        
        # Analyze urgency and priority
        urgency_score = self.ai_analyzer.analyze_urgency(
            email_data['subject'], 
            email_data['body']
        )
        
        priority = self._determine_priority(urgency_score, email_data['sender_email'])
        
        # Generate summary
        summary = self.ai_analyzer.generate_summary(
            email_data['subject'], 
            email_data['body']
        )
        
        # Check if action is required
        action_required = self.ai_analyzer.check_action_required(
            email_data['subject'], 
            email_data['body']
        )
        
        # Generate follow-up suggestions
        follow_up_suggestions = self.ai_analyzer.generate_follow_up_suggestions(
            email_data['subject'], 
            email_data['body'],
            category
        )
        
        return EmailSummary(
            id=email_data['id'],
            subject=email_data['subject'],
            sender=email_data['sender'],
            sender_email=email_data['sender_email'],
            received_at=email_data['received_at'],
            category=category,
            priority=priority,
            summary=summary,
            urgency_score=urgency_score,
            action_required=action_required,
            follow_up_suggestions=follow_up_suggestions
        )

    def _determine_priority(self, urgency_score: float, sender_email: str) -> PriorityLevel:
        """Determine email priority based on urgency score and sender"""
        # Check if sender is VIP
        vip_contacts = db.get_vip_contacts()
        is_vip = any(contact['email'] == sender_email for contact in vip_contacts)
        
        if is_vip:
            return PriorityLevel.HIGH
        
        if urgency_score >= 0.8:
            return PriorityLevel.URGENT
        elif urgency_score >= 0.6:
            return PriorityLevel.HIGH
        elif urgency_score >= 0.4:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW

    def process_inbox(self, date: str = None):
        """Process inbox and analyze emails"""
        try:
            # Fetch emails
            emails = self.fetch_emails(date)
            
            # Analyze each email
            email_summaries = []
            for email_data in emails:
                try:
                    summary = self.analyze_email(email_data)
                    email_summaries.append(summary.dict())
                    
                    # Save to database
                    db.save_email_summary(summary.dict())
                    
                except Exception as e:
                    print(f"Error analyzing email {email_data.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Generate daily summary
            if email_summaries:
                daily_summary = self._generate_daily_summary(email_summaries, date)
                db.save_daily_summary(daily_summary)
            
            return email_summaries
            
        except Exception as e:
            raise Exception(f"Error processing inbox: {str(e)}")

    def _generate_daily_summary(self, email_summaries: List[Dict[str, Any]], date: str = None) -> Dict[str, Any]:
        """Generate daily summary from email summaries"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Count categories
        categories = {}
        priority_breakdown = {}
        urgent_emails = []
        unread_emails = []
        response_reminders = []
        
        for summary in email_summaries:
            # Category count
            category = summary['category']
            categories[category] = categories.get(category, 0) + 1
            
            # Priority count
            priority = summary['priority']
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
            
            # Urgent emails
            if summary['priority'] in ['high', 'urgent'] or summary['urgency_score'] >= 0.7:
                urgent_emails.append(summary)
            
            # Unread emails
            if not summary['is_read']:
                unread_emails.append(summary)
            
            # Response reminders (emails that need replies)
            if not summary['is_replied'] and summary['action_required']:
                response_reminders.append(summary)
        
        return {
            'date': date,
            'total_emails': len(email_summaries),
            'categories': categories,
            'urgent_emails': urgent_emails,
            'unread_emails': unread_emails,
            'response_reminders': response_reminders,
            'priority_breakdown': priority_breakdown
        }

    def get_response_reminders(self, hours_threshold: int = 24) -> List[Dict[str, Any]]:
        """Get emails that need responses"""
        # This would typically query the database for emails that haven't been replied to
        # For now, we'll return a placeholder
        return []

    def mark_as_read(self, email_id: str):
        """Mark email as read"""
        # Update database
        pass

    def mark_as_replied(self, email_id: str):
        """Mark email as replied"""
        # Update database
        pass 