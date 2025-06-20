import requests
import json
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from app.core.database import db

load_dotenv()

class NotificationManager:
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load notification configuration from database"""
        config = db.get_configuration("notification_config")
        if not config:
            # Default configuration
            config = {
                "slack_webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
                "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
                "whatsapp_webhook_url": os.getenv("WHATSAPP_WEBHOOK_URL", ""),
                "enable_voice_summary": False,
                "notification_channels": []
            }
        return config
    
    def send_notification(self, title: str, message: str, priority: str = "normal") -> Dict[str, bool]:
        """Send notification to all configured channels"""
        results = {}
        
        try:
            # Send to Slack
            if self.config.get("slack_webhook_url"):
                results["slack"] = self._send_slack_notification(title, message, priority)
            
            # Send to Telegram
            if self.config.get("telegram_bot_token") and self.config.get("telegram_chat_id"):
                results["telegram"] = self._send_telegram_notification(title, message, priority)
            
            # Send to WhatsApp
            if self.config.get("whatsapp_webhook_url"):
                results["whatsapp"] = self._send_whatsapp_notification(title, message, priority)
            
            return results
            
        except Exception as e:
            print(f"Error sending notifications: {e}")
            return {"error": str(e)}
    
    def _send_slack_notification(self, title: str, message: str, priority: str = "normal") -> bool:
        """Send notification to Slack"""
        try:
            webhook_url = self.config.get("slack_webhook_url")
            if not webhook_url:
                return False
            
            # Determine color based on priority
            color_map = {
                "urgent": "#ff0000",  # Red
                "high": "#ff9900",    # Orange
                "normal": "#36a64f",  # Green
                "low": "#cccccc"      # Gray
            }
            color = color_map.get(priority, color_map["normal"])
            
            # Prepare Slack message
            slack_message = {
                "attachments": [
                    {
                        "color": color,
                        "title": title,
                        "text": message,
                        "footer": "Intelligent Email Agent",
                        "ts": int(time.time())
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                webhook_url,
                json=slack_message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Slack notification sent successfully: {title}")
                return True
            else:
                print(f"Failed to send Slack notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False
    
    def _send_telegram_notification(self, title: str, message: str, priority: str = "normal") -> bool:
        """Send notification to Telegram"""
        try:
            bot_token = self.config.get("telegram_bot_token")
            chat_id = self.config.get("telegram_chat_id")
            
            if not bot_token or not chat_id:
                return False
            
            # Prepare message with emoji based on priority
            emoji_map = {
                "urgent": "🚨",
                "high": "⚠️",
                "normal": "📧",
                "low": "📬"
            }
            emoji = emoji_map.get(priority, emoji_map["normal"])
            
            telegram_message = f"{emoji} *{title}*\n\n{message}"
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": telegram_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"Telegram notification sent successfully: {title}")
                return True
            else:
                print(f"Failed to send Telegram notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")
            return False
    
    def _send_whatsapp_notification(self, title: str, message: str, priority: str = "normal") -> bool:
        """Send notification to WhatsApp"""
        try:
            webhook_url = self.config.get("whatsapp_webhook_url")
            if not webhook_url:
                return False
            
            # Prepare WhatsApp message
            whatsapp_message = {
                "title": title,
                "message": message,
                "priority": priority,
                "timestamp": int(time.time())
            }
            
            # Send to WhatsApp webhook
            response = requests.post(
                webhook_url,
                json=whatsapp_message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"WhatsApp notification sent successfully: {title}")
                return True
            else:
                print(f"Failed to send WhatsApp notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending WhatsApp notification: {e}")
            return False
    
    def send_daily_summary(self, daily_summary: Dict[str, Any]) -> Dict[str, bool]:
        """Send daily email summary notification"""
        try:
            title = f"📧 Daily Email Summary - {daily_summary.get('date', 'Today')}"
            
            message = f"📊 *Total emails:* {daily_summary.get('total_emails', 0)}\n"
            
            # Add category breakdown
            categories = daily_summary.get('categories', {})
            if categories:
                message += "\n📂 *Categories:*\n"
                for category, count in categories.items():
                    message += f"   • {category}: {count}\n"
            
            # Add urgent emails
            urgent_emails = daily_summary.get('urgent_emails', [])
            if urgent_emails:
                message += f"\n⚠️ *Urgent emails:* {len(urgent_emails)}\n"
                for email in urgent_emails[:3]:  # Show top 3
                    message += f"   • {email.get('subject', 'No subject')} - {email.get('sender', 'Unknown')}\n"
            
            # Add unread emails
            unread_emails = daily_summary.get('unread_emails', [])
            if unread_emails:
                message += f"\n📬 *Unread emails:* {len(unread_emails)}\n"
            
            # Add response reminders
            response_reminders = daily_summary.get('response_reminders', [])
            if response_reminders:
                message += f"\n🧾 *Response reminders:* {len(response_reminders)}\n"
            
            return self.send_notification(title, message, "normal")
            
        except Exception as e:
            print(f"Error sending daily summary: {e}")
            return {"error": str(e)}
    
    def send_urgent_alert(self, urgent_emails: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Send urgent email alert"""
        try:
            title = "🚨 Urgent Email Alert"
            
            message = f"⚠️ You have {len(urgent_emails)} urgent emails:\n\n"
            
            for email in urgent_emails[:5]:  # Limit to 5
                message += f"📧 *{email.get('subject', 'No subject')}*\n"
                message += f"   From: {email.get('sender', 'Unknown')}\n"
                message += f"   Priority: {email.get('priority', 'Unknown')}\n"
                message += f"   Summary: {email.get('summary', 'No summary')}\n\n"
            
            if len(urgent_emails) > 5:
                message += f"... and {len(urgent_emails) - 5} more urgent emails"
            
            return self.send_notification(title, message, "urgent")
            
        except Exception as e:
            print(f"Error sending urgent alert: {e}")
            return {"error": str(e)}
    
    def send_response_reminder(self, reminder_emails: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Send response reminder notification"""
        try:
            title = "🧾 Response Reminders"
            
            message = f"📧 You have {len(reminder_emails)} emails that need responses:\n\n"
            
            for email in reminder_emails[:5]:  # Limit to 5
                message += f"📧 *{email.get('subject', 'No subject')}*\n"
                message += f"   From: {email.get('sender', 'Unknown')}\n"
                message += f"   Received: {email.get('received_at', 'Unknown')}\n"
                message += f"   Action: {email.get('action_required', 'Response needed')}\n\n"
            
            if len(reminder_emails) > 5:
                message += f"... and {len(reminder_emails) - 5} more emails need responses"
            
            return self.send_notification(title, message, "high")
            
        except Exception as e:
            print(f"Error sending response reminder: {e}")
            return {"error": str(e)}
    
    def test_notifications(self) -> Dict[str, bool]:
        """Test all configured notification channels"""
        test_message = "🧪 This is a test notification from your Intelligent Email Agent. If you receive this, your notifications are working correctly!"
        
        return self.send_notification("Test Notification", test_message, "normal")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update notification configuration"""
        try:
            self.config.update(new_config)
            db.save_configuration("notification_config", self.config)
            print("Notification configuration updated")
        except Exception as e:
            print(f"Error updating notification config: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current notification configuration"""
        return self.config.copy()

import time  # Add this import at the top 