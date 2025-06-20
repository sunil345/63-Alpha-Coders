import pytest
from app.core.email_categorizer import EmailCategorizer
from app.models import EmailCategory

class TestEmailCategorizer:
    """Test cases for EmailCategorizer class"""
    
    def test_categorize_work_email(self):
        """Test categorization of work emails"""
        categorizer = EmailCategorizer()
        
        subject = "Project Update Meeting"
        body = "Please review the project timeline and prepare for the meeting."
        sender_email = "colleague@company.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.WORK
    
    def test_categorize_personal_email(self):
        """Test categorization of personal emails"""
        categorizer = EmailCategorizer()
        
        subject = "Family Dinner"
        body = "Let's have dinner this weekend with the family."
        sender_email = "family@example.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.PERSONAL
    
    def test_categorize_promotional_email(self):
        """Test categorization of promotional emails"""
        categorizer = EmailCategorizer()
        
        subject = "Special Offer - 50% Off"
        body = "Don't miss our special sale with 50% off all items."
        sender_email = "store@amazon.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.PROMOTIONS
    
    def test_categorize_social_email(self):
        """Test categorization of social emails"""
        categorizer = EmailCategorizer()
        
        subject = "Facebook Friend Request"
        body = "You have a new friend request on Facebook."
        sender_email = "noreply@facebook.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.SOCIAL
    
    def test_categorize_urgent_email(self):
        """Test categorization of urgent emails"""
        categorizer = EmailCategorizer()
        
        subject = "URGENT: System Down"
        body = "The system is down and needs immediate attention ASAP."
        sender_email = "admin@company.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.URGENT
    
    def test_categorize_meeting_email(self):
        """Test categorization of meeting emails"""
        categorizer = EmailCategorizer()
        
        subject = "Team Meeting Tomorrow"
        body = "We have a team meeting scheduled for tomorrow at 2 PM."
        sender_email = "manager@company.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.MEETINGS
    
    def test_categorize_deadline_email(self):
        """Test categorization of deadline emails"""
        categorizer = EmailCategorizer()
        
        subject = "Project Deadline"
        body = "The project deadline is approaching. Please submit your work by Friday."
        sender_email = "project@company.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.DEADLINES
    
    def test_categorize_by_sender_domain(self):
        """Test categorization by sender domain"""
        categorizer = EmailCategorizer()
        
        # Test work domain
        subject = "Test Email"
        body = "Test content"
        sender_email = "test@gmail.com"
        
        category = categorizer._categorize_by_sender(sender_email)
        assert category == EmailCategory.WORK
        
        # Test social domain
        sender_email = "test@facebook.com"
        category = categorizer._categorize_by_sender(sender_email)
        assert category == EmailCategory.SOCIAL
        
        # Test promotional domain
        sender_email = "test@amazon.com"
        category = categorizer._categorize_by_sender(sender_email)
        assert category == EmailCategory.PROMOTIONS
    
    def test_has_keywords(self):
        """Test keyword detection"""
        categorizer = EmailCategorizer()
        
        text = "This email contains project and meeting keywords"
        keywords = ['project', 'meeting', 'deadline']
        
        has_keywords = categorizer._has_keywords(text, keywords)
        assert has_keywords is True
        
        text = "This email has no relevant keywords"
        has_keywords = categorizer._has_keywords(text, keywords)
        assert has_keywords is False
    
    def test_get_category_confidence(self):
        """Test category confidence calculation"""
        categorizer = EmailCategorizer()
        
        subject = "Project Meeting"
        body = "Let's discuss the project timeline and next steps."
        sender_email = "colleague@company.com"
        
        confidence_scores = categorizer.get_category_confidence(subject, body, sender_email)
        
        assert isinstance(confidence_scores, dict)
        assert EmailCategory.WORK in confidence_scores
        assert confidence_scores[EmailCategory.WORK] > 0
    
    def test_extract_category_features(self):
        """Test category feature extraction"""
        categorizer = EmailCategorizer()
        
        subject = "Meeting on 2024-01-15?"
        body = "Can you attend the meeting at 2:00 PM? Visit https://example.com for details."
        
        features = categorizer.extract_category_features(subject, body)
        
        assert isinstance(features, dict)
        assert features['has_question_marks'] is True
        assert features['has_numbers'] is True
        assert features['has_dates'] is True
        assert features['has_times'] is True
        assert features['has_urls'] is True
        assert features['word_count'] > 0
        assert features['sentence_count'] > 0
    
    def test_get_category_stats(self):
        """Test category statistics calculation"""
        categorizer = EmailCategorizer()
        
        emails = [
            {'category': EmailCategory.WORK},
            {'category': EmailCategory.WORK},
            {'category': EmailCategory.PERSONAL},
            {'category': EmailCategory.PROMOTIONS}
        ]
        
        stats = categorizer.get_category_stats(emails)
        
        assert stats[EmailCategory.WORK] == 2
        assert stats[EmailCategory.PERSONAL] == 1
        assert stats[EmailCategory.PROMOTIONS] == 1
        assert stats[EmailCategory.SOCIAL] == 0
    
    def test_update_keywords(self):
        """Test keyword update functionality"""
        categorizer = EmailCategorizer()
        
        original_keywords = categorizer.category_keywords[EmailCategory.WORK].copy()
        new_keywords = ['new_keyword1', 'new_keyword2']
        
        categorizer.update_keywords(EmailCategory.WORK, new_keywords)
        
        # Check if new keywords were added
        for keyword in new_keywords:
            assert keyword in categorizer.category_keywords[EmailCategory.WORK]
        
        # Check if original keywords are still there
        for keyword in original_keywords:
            assert keyword in categorizer.category_keywords[EmailCategory.WORK]
    
    def test_categorize_unknown_email(self):
        """Test categorization of unknown email type"""
        categorizer = EmailCategorizer()
        
        subject = "Random Subject"
        body = "Random content without specific keywords."
        sender_email = "unknown@random.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.OTHER
    
    def test_categorize_email_with_mixed_keywords(self):
        """Test categorization when multiple category keywords are present"""
        categorizer = EmailCategorizer()
        
        # Email with both work and urgent keywords (urgent should take precedence)
        subject = "URGENT: Project Update"
        body = "The project needs immediate attention. Please review the timeline."
        sender_email = "manager@company.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.URGENT
    
    def test_categorize_email_with_special_characters(self):
        """Test categorization with special characters in text"""
        categorizer = EmailCategorizer()
        
        subject = "Project Update - Q1 2024"
        body = "Here's the project update for Q1 2024. Please review & provide feedback!"
        sender_email = "team@company.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.WORK
    
    def test_categorize_email_case_insensitive(self):
        """Test that categorization is case insensitive"""
        categorizer = EmailCategorizer()
        
        subject = "PROJECT MEETING"
        body = "We have a PROJECT meeting scheduled for tomorrow."
        sender_email = "colleague@company.com"
        
        category = categorizer.categorize_email(subject, body, sender_email)
        
        assert category == EmailCategory.WORK 