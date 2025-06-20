import re
from typing import List, Dict, Any
from app.models import EmailCategory

class EmailCategorizer:
    def __init__(self):
        self.category_keywords = self._initialize_keywords()
        
    def _initialize_keywords(self) -> Dict[EmailCategory, List[str]]:
        """Initialize keywords for each category"""
        return {
            EmailCategory.WORK: [
                'project', 'task', 'deadline', 'meeting', 'report', 'presentation',
                'client', 'customer', 'team', 'collaboration', 'workflow', 'process',
                'development', 'code', 'bug', 'feature', 'release', 'deployment',
                'review', 'approval', 'signature', 'contract', 'proposal', 'quote',
                'invoice', 'payment', 'budget', 'expense', 'reimbursement'
            ],
            EmailCategory.PERSONAL: [
                'family', 'friend', 'personal', 'home', 'house', 'family',
                'birthday', 'anniversary', 'celebration', 'party', 'dinner',
                'weekend', 'vacation', 'travel', 'trip', 'holiday', 'personal',
                'health', 'medical', 'doctor', 'appointment', 'insurance'
            ],
            EmailCategory.PROMOTIONS: [
                'sale', 'discount', 'offer', 'deal', 'promotion', 'coupon',
                'limited time', 'special offer', 'exclusive', 'membership',
                'subscription', 'newsletter', 'marketing', 'advertisement',
                'sponsored', 'promotional', 'commercial', 'retail', 'store',
                'shop', 'buy', 'purchase', 'order', 'shipping', 'delivery'
            ],
            EmailCategory.SOCIAL: [
                'social', 'network', 'facebook', 'twitter', 'instagram', 'linkedin',
                'invitation', 'connect', 'friend request', 'follow', 'like',
                'share', 'post', 'update', 'status', 'profile', 'social media',
                'community', 'group', 'forum', 'discussion', 'chat'
            ],
            EmailCategory.URGENT: [
                'urgent', 'asap', 'immediate', 'emergency', 'critical', 'important',
                'action required', 'response needed', 'deadline', 'due date',
                'overdue', 'late', 'missed', 'failed', 'error', 'issue',
                'problem', 'trouble', 'help', 'support', 'assistance'
            ],
            EmailCategory.MEETINGS: [
                'meeting', 'appointment', 'call', 'conference', 'webinar',
                'schedule', 'calendar', 'agenda', 'minutes', 'attend',
                'participate', 'join', 'dial', 'zoom', 'teams', 'skype',
                'video call', 'phone call', 'conference call', 'standup',
                'daily', 'weekly', 'monthly', 'quarterly', 'annual'
            ],
            EmailCategory.DEADLINES: [
                'deadline', 'due date', 'due', 'submit', 'deliver', 'complete',
                'finish', 'end date', 'cutoff', 'expiration', 'expires',
                'last day', 'final', 'closing', 'deadline', 'timeline',
                'schedule', 'milestone', 'deliverable', 'target date'
            ]
        }
        
    def categorize_email(self, subject: str, body: str, sender_email: str) -> EmailCategory:
        """Categorize email based on subject, body, and sender"""
        try:
            # Combine subject and body for analysis
            text = f"{subject} {body}".lower()
            
            # Check for urgent keywords first
            if self._has_keywords(text, self.category_keywords[EmailCategory.URGENT]):
                return EmailCategory.URGENT
            
            # Check for meeting-related keywords
            if self._has_keywords(text, self.category_keywords[EmailCategory.MEETINGS]):
                return EmailCategory.MEETINGS
            
            # Check for deadline-related keywords
            if self._has_keywords(text, self.category_keywords[EmailCategory.DEADLINES]):
                return EmailCategory.DEADLINES
            
            # Check for work-related keywords
            if self._has_keywords(text, self.category_keywords[EmailCategory.WORK]):
                return EmailCategory.WORK
            
            # Check for personal keywords
            if self._has_keywords(text, self.category_keywords[EmailCategory.PERSONAL]):
                return EmailCategory.PERSONAL
            
            # Check for promotional keywords
            if self._has_keywords(text, self.category_keywords[EmailCategory.PROMOTIONS]):
                return EmailCategory.PROMOTIONS
            
            # Check for social keywords
            if self._has_keywords(text, self.category_keywords[EmailCategory.SOCIAL]):
                return EmailCategory.SOCIAL
            
            # Check sender domain for additional clues
            sender_category = self._categorize_by_sender(sender_email)
            if sender_category != EmailCategory.OTHER:
                return sender_category
            
            # Default to other if no clear category
            return EmailCategory.OTHER
            
        except Exception as e:
            print(f"Error categorizing email: {e}")
            return EmailCategory.OTHER
    
    def _has_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the given keywords"""
        for keyword in keywords:
            if keyword in text:
                return True
        return False
    
    def _categorize_by_sender(self, sender_email: str) -> EmailCategory:
        """Categorize email based on sender domain"""
        try:
            domain = sender_email.split('@')[-1].lower()
            
            # Work domains
            work_domains = [
                'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com',
                'company.com', 'corp.com', 'business.com', 'enterprise.com'
            ]
            
            # Social media domains
            social_domains = [
                'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
                'snapchat.com', 'tiktok.com', 'pinterest.com'
            ]
            
            # Promotional domains
            promo_domains = [
                'amazon.com', 'ebay.com', 'etsy.com', 'shopify.com',
                'mailchimp.com', 'constantcontact.com', 'sendgrid.com',
                'salesforce.com', 'hubspot.com', 'marketing.com'
            ]
            
            if domain in work_domains:
                return EmailCategory.WORK
            elif domain in social_domains:
                return EmailCategory.SOCIAL
            elif domain in promo_domains:
                return EmailCategory.PROMOTIONS
            
            return EmailCategory.OTHER
            
        except Exception as e:
            print(f"Error categorizing by sender: {e}")
            return EmailCategory.OTHER
    
    def get_category_confidence(self, subject: str, body: str, sender_email: str) -> Dict[EmailCategory, float]:
        """Get confidence scores for each category"""
        try:
            text = f"{subject} {body}".lower()
            confidence_scores = {}
            
            for category, keywords in self.category_keywords.items():
                score = 0.0
                for keyword in keywords:
                    if keyword in text:
                        score += 0.1  # Each keyword match adds 10% confidence
                
                # Normalize score
                confidence_scores[category] = min(score, 1.0)
            
            # Add sender-based confidence
            sender_category = self._categorize_by_sender(sender_email)
            if sender_category in confidence_scores:
                confidence_scores[sender_category] += 0.3  # Sender adds 30% confidence
            
            return confidence_scores
            
        except Exception as e:
            print(f"Error calculating category confidence: {e}")
            return {EmailCategory.OTHER: 1.0}
    
    def extract_category_features(self, subject: str, body: str) -> Dict[str, Any]:
        """Extract features that help with categorization"""
        try:
            text = f"{subject} {body}".lower()
            features = {
                'has_question_marks': '?' in text,
                'has_exclamation_marks': '!' in text,
                'has_numbers': bool(re.search(r'\d', text)),
                'has_dates': bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)),
                'has_times': bool(re.search(r'\d{1,2}:\d{2}', text)),
                'has_urls': bool(re.search(r'http[s]?://', text)),
                'has_emails': bool(re.search(r'\S+@\S+', text)),
                'word_count': len(text.split()),
                'sentence_count': len(text.split('.')),
                'has_attachments': 'attachment' in text or 'attached' in text,
                'has_signature': 'best regards' in text or 'sincerely' in text or 'thanks' in text
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting category features: {e}")
            return {}
    
    def update_keywords(self, category: EmailCategory, keywords: List[str]):
        """Update keywords for a category"""
        if category in self.category_keywords:
            self.category_keywords[category].extend(keywords)
    
    def get_category_stats(self, emails: List[Dict[str, Any]]) -> Dict[EmailCategory, int]:
        """Get statistics for email categories"""
        stats = {}
        for category in EmailCategory:
            stats[category] = 0
        
        for email in emails:
            category = email.get('category', EmailCategory.OTHER)
            if category in stats:
                stats[category] += 1
        
        return stats 