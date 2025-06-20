import openai
import re
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class AIAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def analyze_urgency(self, subject: str, body: str) -> float:
        """Analyze email urgency and return a score between 0 and 1"""
        try:
            # Simple rule-based urgency detection as fallback
            urgency_keywords = [
                'urgent', 'asap', 'immediate', 'emergency', 'critical', 'deadline',
                'action required', 'response needed', 'important', 'priority'
            ]
            
            text = f"{subject} {body}".lower()
            urgency_count = sum(1 for keyword in urgency_keywords if keyword in text)
            
            # Base urgency score
            base_score = min(urgency_count * 0.2, 0.8)
            
            # Try AI analysis if available
            if os.getenv("OPENAI_API_KEY"):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an email urgency analyzer. Rate the urgency of emails from 0 to 1, where 0 is not urgent and 1 is extremely urgent."
                            },
                            {
                                "role": "user",
                                "content": f"Subject: {subject}\n\nBody: {body[:500]}...\n\nRate the urgency from 0 to 1:"
                            }
                        ],
                        max_tokens=10,
                        temperature=0.1
                    )
                    
                    ai_score = float(response.choices[0].message.content.strip())
                    # Combine rule-based and AI scores
                    return min((base_score + ai_score) / 2, 1.0)
                    
                except Exception as e:
                    print(f"AI urgency analysis failed: {e}")
                    return base_score
            
            return base_score
            
        except Exception as e:
            print(f"Error analyzing urgency: {e}")
            return 0.5

    def generate_summary(self, subject: str, body: str) -> str:
        """Generate a concise summary of the email"""
        try:
            if os.getenv("OPENAI_API_KEY"):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an email summarizer. Create concise, informative summaries of emails in 1-2 sentences."
                            },
                            {
                                "role": "user",
                                "content": f"Subject: {subject}\n\nBody: {body[:1000]}...\n\nSummarize this email:"
                            }
                        ],
                        max_tokens=100,
                        temperature=0.3
                    )
                    
                    return response.choices[0].message.content.strip()
                    
                except Exception as e:
                    print(f"AI summary generation failed: {e}")
                    return self._fallback_summary(subject, body)
            
            return self._fallback_summary(subject, body)
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Email about: {subject}"

    def _fallback_summary(self, subject: str, body: str) -> str:
        """Fallback summary when AI is not available"""
        # Extract first sentence or key phrases
        if len(body) > 100:
            # Take first meaningful sentence
            sentences = body.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 10:
                    return f"{subject}: {sentence.strip()[:100]}..."
        
        return f"Email about: {subject}"

    def check_action_required(self, subject: str, body: str) -> bool:
        """Check if the email requires action"""
        try:
            action_keywords = [
                'action required', 'please respond', 'reply needed', 'urgent',
                'deadline', 'meeting', 'call', 'schedule', 'confirm', 'approve',
                'review', 'sign', 'complete', 'submit', 'send', 'provide'
            ]
            
            text = f"{subject} {body}".lower()
            
            # Check for action keywords
            has_action_keywords = any(keyword in text for keyword in action_keywords)
            
            # Check for question marks
            has_questions = '?' in text
            
            # Check for time-sensitive words
            time_sensitive = any(word in text for word in ['today', 'tomorrow', 'asap', 'urgent', 'deadline'])
            
            return has_action_keywords or has_questions or time_sensitive
            
        except Exception as e:
            print(f"Error checking action required: {e}")
            return False

    def generate_follow_up_suggestions(self, subject: str, body: str, category: str) -> List[str]:
        """Generate follow-up suggestions for the email"""
        try:
            suggestions = []
            
            # Basic suggestions based on category
            if category == "work":
                suggestions.extend([
                    "Schedule a follow-up meeting",
                    "Send a detailed response with next steps",
                    "Add to task list for tracking"
                ])
            elif category == "meetings":
                suggestions.extend([
                    "Confirm meeting details",
                    "Prepare agenda items",
                    "Set calendar reminder"
                ])
            elif category == "deadlines":
                suggestions.extend([
                    "Set deadline reminder",
                    "Break down tasks",
                    "Update project timeline"
                ])
            
            # AI-generated suggestions if available
            if os.getenv("OPENAI_API_KEY"):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an email assistant. Generate 2-3 specific, actionable follow-up suggestions for emails. Keep them concise and practical."
                            },
                            {
                                "role": "user",
                                "content": f"Subject: {subject}\n\nBody: {body[:500]}...\n\nCategory: {category}\n\nGenerate follow-up suggestions:"
                            }
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    
                    ai_suggestions = response.choices[0].message.content.strip().split('\n')
                    ai_suggestions = [s.strip() for s in ai_suggestions if s.strip()]
                    suggestions.extend(ai_suggestions[:2])  # Add top 2 AI suggestions
                    
                except Exception as e:
                    print(f"AI follow-up suggestions failed: {e}")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            print(f"Error generating follow-up suggestions: {e}")
            return ["Review and respond as needed"]

    def analyze_sentiment(self, subject: str, body: str) -> str:
        """Analyze email sentiment"""
        try:
            if os.getenv("OPENAI_API_KEY"):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Analyze the sentiment of this email. Respond with only: positive, negative, neutral, or urgent."
                            },
                            {
                                "role": "user",
                                "content": f"Subject: {subject}\n\nBody: {body[:500]}..."
                            }
                        ],
                        max_tokens=10,
                        temperature=0.1
                    )
                    
                    return response.choices[0].message.content.strip().lower()
                    
                except Exception as e:
                    print(f"AI sentiment analysis failed: {e}")
                    return "neutral"
            
            return "neutral"
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return "neutral"

    def extract_key_information(self, subject: str, body: str) -> Dict[str, Any]:
        """Extract key information from email"""
        try:
            info = {
                'dates': [],
                'times': [],
                'people': [],
                'locations': [],
                'amounts': [],
                'urls': []
            }
            
            text = f"{subject} {body}"
            
            # Extract dates
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
            info['dates'] = re.findall(date_pattern, text)
            
            # Extract times
            time_pattern = r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b'
            info['times'] = re.findall(time_pattern, text)
            
            # Extract URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            info['urls'] = re.findall(url_pattern, text)
            
            # Extract amounts (basic)
            amount_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
            info['amounts'] = re.findall(amount_pattern, text)
            
            return info
            
        except Exception as e:
            print(f"Error extracting key information: {e}")
            return {}

    def generate_natural_language_summary(self, email_summaries: List[Dict[str, Any]]) -> str:
        """Generate natural language summary of multiple emails"""
        try:
            if not email_summaries:
                return "No emails to summarize."
            
            if os.getenv("OPENAI_API_KEY"):
                try:
                    # Prepare email data for AI
                    email_data = []
                    for summary in email_summaries[:10]:  # Limit to 10 emails
                        email_data.append({
                            'subject': summary['subject'],
                            'sender': summary['sender'],
                            'category': summary['category'],
                            'priority': summary['priority'],
                            'summary': summary['summary']
                        })
                    
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an email assistant creating a natural language daily summary. Write a conversational summary that highlights important emails, urgent items, and key themes from the day's emails."
                            },
                            {
                                "role": "user",
                                "content": f"Create a natural language summary of these emails:\n\n{email_data}"
                            }
                        ],
                        max_tokens=300,
                        temperature=0.7
                    )
                    
                    return response.choices[0].message.content.strip()
                    
                except Exception as e:
                    print(f"AI natural language summary failed: {e}")
                    return self._fallback_natural_summary(email_summaries)
            
            return self._fallback_natural_summary(email_summaries)
            
        except Exception as e:
            print(f"Error generating natural language summary: {e}")
            return "Unable to generate summary."

    def _fallback_natural_summary(self, email_summaries: List[Dict[str, Any]]) -> str:
        """Fallback natural language summary"""
        if not email_summaries:
            return "No emails to summarize."
        
        total_emails = len(email_summaries)
        urgent_count = len([e for e in email_summaries if e['priority'] in ['high', 'urgent']])
        unread_count = len([e for e in email_summaries if not e['is_read']])
        
        summary = f"You received {total_emails} emails today. "
        
        if urgent_count > 0:
            summary += f"There are {urgent_count} urgent emails that need your attention. "
        
        if unread_count > 0:
            summary += f"You have {unread_count} unread emails. "
        
        # Group by category
        categories = {}
        for email in email_summaries:
            cat = email['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            summary += "Emails are categorized as: "
            category_list = [f"{count} {cat}" for cat, count in categories.items()]
            summary += ", ".join(category_list) + "."
        
        return summary 