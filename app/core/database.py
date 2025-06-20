import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class Database:
    def __init__(self, db_path: str = "email_agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Email summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_summaries (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                received_at TIMESTAMP NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                summary TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                is_replied BOOLEAN DEFAULT FALSE,
                urgency_score REAL DEFAULT 0.0,
                action_required BOOLEAN DEFAULT FALSE,
                follow_up_suggestions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_emails INTEGER NOT NULL,
                categories TEXT NOT NULL,
                urgent_emails TEXT,
                unread_emails TEXT,
                response_reminders TEXT,
                priority_breakdown TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_type TEXT NOT NULL,
                config_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # VIP contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                priority_level TEXT DEFAULT 'high',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_email_summary(self, email_summary: Dict[str, Any]):
        """Save email summary to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO email_summaries 
            (id, subject, sender, sender_email, received_at, category, priority, 
             summary, is_read, is_replied, urgency_score, action_required, follow_up_suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_summary['id'],
            email_summary['subject'],
            email_summary['sender'],
            email_summary['sender_email'],
            email_summary['received_at'],
            email_summary['category'],
            email_summary['priority'],
            email_summary['summary'],
            email_summary['is_read'],
            email_summary['is_replied'],
            email_summary['urgency_score'],
            email_summary['action_required'],
            json.dumps(email_summary.get('follow_up_suggestions', []))
        ))
        
        conn.commit()
        conn.close()

    def save_daily_summary(self, daily_summary: Dict[str, Any]):
        """Save daily summary to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO daily_summaries 
            (date, total_emails, categories, urgent_emails, unread_emails, 
             response_reminders, priority_breakdown)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            daily_summary['date'],
            daily_summary['total_emails'],
            json.dumps(daily_summary['categories']),
            json.dumps(daily_summary.get('urgent_emails', [])),
            json.dumps(daily_summary.get('unread_emails', [])),
            json.dumps(daily_summary.get('response_reminders', [])),
            json.dumps(daily_summary['priority_breakdown'])
        ))
        
        conn.commit()
        conn.close()

    def get_emails_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get emails for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM email_summaries 
            WHERE DATE(received_at) = ?
            ORDER BY received_at DESC
        ''', (date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        emails = []
        for row in rows:
            emails.append({
                'id': row[0],
                'subject': row[1],
                'sender': row[2],
                'sender_email': row[3],
                'received_at': row[4],
                'category': row[5],
                'priority': row[6],
                'summary': row[7],
                'is_read': bool(row[8]),
                'is_replied': bool(row[9]),
                'urgency_score': row[10],
                'action_required': bool(row[11]),
                'follow_up_suggestions': json.loads(row[12]) if row[12] else []
            })
        
        return emails

    def get_daily_summary(self, date: str) -> Optional[Dict[str, Any]]:
        """Get daily summary for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM daily_summaries 
            WHERE date = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'date': row[1],
                'total_emails': row[2],
                'categories': json.loads(row[3]),
                'urgent_emails': json.loads(row[4]) if row[4] else [],
                'unread_emails': json.loads(row[5]) if row[5] else [],
                'response_reminders': json.loads(row[6]) if row[6] else [],
                'priority_breakdown': json.loads(row[7])
            }
        return None

    def save_configuration(self, config_type: str, config_data: Dict[str, Any]):
        """Save configuration to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO configurations (config_type, config_data, updated_at)
            VALUES (?, ?, ?)
        ''', (config_type, json.dumps(config_data), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

    def get_configuration(self, config_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT config_data FROM configurations 
            WHERE config_type = ?
            ORDER BY updated_at DESC
            LIMIT 1
        ''', (config_type,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None

    def add_vip_contact(self, email: str, name: str = None, priority_level: str = "high"):
        """Add VIP contact"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO vip_contacts (email, name, priority_level)
            VALUES (?, ?, ?)
        ''', (email, name, priority_level))
        
        conn.commit()
        conn.close()

    def get_vip_contacts(self) -> List[Dict[str, Any]]:
        """Get all VIP contacts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT email, name, priority_level FROM vip_contacts')
        rows = cursor.fetchall()
        conn.close()
        
        return [{'email': row[0], 'name': row[1], 'priority_level': row[2]} for row in rows]

# Global database instance
db = Database()

async def init_db():
    """Initialize database on startup"""
    db.init_database() 