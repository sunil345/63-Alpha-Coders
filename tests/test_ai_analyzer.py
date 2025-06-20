import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.ai_analyzer import AIAnalyzer

class TestAIAnalyzer:
    """Test cases for AIAnalyzer class"""
    
    def test_analyze_urgency_with_keywords(self):
        """Test urgency analysis with urgency keywords"""
        analyzer = AIAnalyzer()
        
        subject = "URGENT: Action Required"
        body = "This is an urgent matter that needs immediate attention ASAP."
        
        urgency_score = analyzer.analyze_urgency(subject, body)
        
        assert urgency_score > 0.5
        assert urgency_score <= 1.0
    
    def test_analyze_urgency_without_keywords(self):
        """Test urgency analysis without urgency keywords"""
        analyzer = AIAnalyzer()
        
        subject = "Weekly Newsletter"
        body = "Here's your weekly newsletter with updates and news."
        
        urgency_score = analyzer.analyze_urgency(subject, body)
        
        assert urgency_score < 0.5
    
    @patch('app.core.ai_analyzer.openai')
    def test_analyze_urgency_with_openai(self, mock_openai):
        """Test urgency analysis with OpenAI integration"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "0.8"
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response
        
        analyzer = AIAnalyzer()
        
        subject = "Important Meeting"
        body = "Please attend the important meeting tomorrow."
        
        urgency_score = analyzer.analyze_urgency(subject, body)
        
        assert urgency_score > 0.0
        assert urgency_score <= 1.0
    
    def test_generate_summary_fallback(self):
        """Test summary generation fallback"""
        analyzer = AIAnalyzer()
        
        subject = "Project Update"
        body = "Here is the latest update on our project. We have made significant progress."
        
        summary = analyzer.generate_summary(subject, body)
        
        assert summary is not None
        assert len(summary) > 0
        assert "Project Update" in summary or "project" in summary.lower()
    
    @patch('app.core.ai_analyzer.openai')
    def test_generate_summary_with_openai(self, mock_openai):
        """Test summary generation with OpenAI"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Project update with significant progress made."
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response
        
        analyzer = AIAnalyzer()
        
        subject = "Project Update"
        body = "Here is the latest update on our project. We have made significant progress."
        
        summary = analyzer.generate_summary(subject, body)
        
        assert summary is not None
        assert len(summary) > 0
    
    def test_check_action_required_with_keywords(self):
        """Test action required detection with action keywords"""
        analyzer = AIAnalyzer()
        
        subject = "Please Review Document"
        body = "Please review the attached document and provide your feedback."
        
        action_required = analyzer.check_action_required(subject, body)
        
        assert action_required is True
    
    def test_check_action_required_with_questions(self):
        """Test action required detection with questions"""
        analyzer = AIAnalyzer()
        
        subject = "Meeting Schedule"
        body = "Can you attend the meeting tomorrow? What time works best for you?"
        
        action_required = analyzer.check_action_required(subject, body)
        
        assert action_required is True
    
    def test_check_action_required_without_action(self):
        """Test action required detection without action keywords"""
        analyzer = AIAnalyzer()
        
        subject = "Newsletter"
        body = "Here's our monthly newsletter with company updates."
        
        action_required = analyzer.check_action_required(subject, body)
        
        assert action_required is False
    
    def test_generate_follow_up_suggestions_work(self):
        """Test follow-up suggestions for work category"""
        analyzer = AIAnalyzer()
        
        subject = "Project Meeting"
        body = "Let's discuss the project timeline and next steps."
        category = "work"
        
        suggestions = analyzer.generate_follow_up_suggestions(subject, body, category)
        
        assert len(suggestions) > 0
        assert any("meeting" in suggestion.lower() for suggestion in suggestions)
    
    def test_generate_follow_up_suggestions_meetings(self):
        """Test follow-up suggestions for meetings category"""
        analyzer = AIAnalyzer()
        
        subject = "Team Meeting"
        body = "Weekly team meeting scheduled for Friday."
        category = "meetings"
        
        suggestions = analyzer.generate_follow_up_suggestions(subject, body, category)
        
        assert len(suggestions) > 0
        assert any("meeting" in suggestion.lower() for suggestion in suggestions)
    
    @patch('app.core.ai_analyzer.openai')
    def test_generate_follow_up_suggestions_with_openai(self, mock_openai):
        """Test follow-up suggestions with OpenAI"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Schedule follow-up meeting\nSend detailed response"
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response
        
        analyzer = AIAnalyzer()
        
        subject = "Project Update"
        body = "Here's the latest project update."
        category = "work"
        
        suggestions = analyzer.generate_follow_up_suggestions(subject, body, category)
        
        assert len(suggestions) > 0
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral content"""
        analyzer = AIAnalyzer()
        
        subject = "Weekly Report"
        body = "Here's the weekly report with standard updates."
        
        sentiment = analyzer.analyze_sentiment(subject, body)
        
        assert sentiment in ['positive', 'negative', 'neutral', 'urgent']
    
    def test_extract_key_information(self):
        """Test key information extraction"""
        analyzer = AIAnalyzer()
        
        subject = "Meeting on 2024-01-15"
        body = "Please join us at 2:00 PM for the meeting. Visit https://example.com for details. Budget is $5000."
        
        info = analyzer.extract_key_information(subject, body)
        
        assert 'dates' in info
        assert 'times' in info
        assert 'urls' in info
        assert 'amounts' in info
        
        # Check for extracted dates
        assert len(info['dates']) > 0
        assert '2024-01-15' in info['dates']
        
        # Check for extracted times
        assert len(info['times']) > 0
        assert '2:00' in info['times'][0]
        
        # Check for extracted URLs
        assert len(info['urls']) > 0
        assert 'https://example.com' in info['urls']
        
        # Check for extracted amounts
        assert len(info['amounts']) > 0
        assert '$5000' in info['amounts']
    
    def test_generate_natural_language_summary_empty(self):
        """Test natural language summary with empty data"""
        analyzer = AIAnalyzer()
        
        email_summaries = []
        
        summary = analyzer.generate_natural_language_summary(email_summaries)
        
        assert summary == "No emails to summarize."
    
    def test_generate_natural_language_summary_with_data(self):
        """Test natural language summary with data"""
        analyzer = AIAnalyzer()
        
        email_summaries = [
            {
                'subject': 'Test Email 1',
                'sender': 'John Doe',
                'category': 'work',
                'priority': 'high',
                'summary': 'Important work email'
            },
            {
                'subject': 'Test Email 2',
                'sender': 'Jane Smith',
                'category': 'personal',
                'priority': 'low',
                'summary': 'Personal email'
            }
        ]
        
        summary = analyzer.generate_natural_language_summary(email_summaries)
        
        assert summary is not None
        assert len(summary) > 0
        assert "2" in summary  # Should mention number of emails
    
    @patch('app.core.ai_analyzer.openai')
    def test_generate_natural_language_summary_with_openai(self, mock_openai):
        """Test natural language summary with OpenAI"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "You received 2 emails today. One urgent work email and one personal email."
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response
        
        analyzer = AIAnalyzer()
        
        email_summaries = [
            {
                'subject': 'Test Email 1',
                'sender': 'John Doe',
                'category': 'work',
                'priority': 'high',
                'summary': 'Important work email'
            }
        ]
        
        summary = analyzer.generate_natural_language_summary(email_summaries)
        
        assert summary is not None
        assert len(summary) > 0
    
    def test_fallback_summary(self):
        """Test fallback summary generation"""
        analyzer = AIAnalyzer()
        
        subject = "Test Subject"
        body = "This is a test email body with some content that should be summarized."
        
        summary = analyzer._fallback_summary(subject, body)
        
        assert summary is not None
        assert len(summary) > 0
        assert "Test Subject" in summary
    
    def test_fallback_natural_summary(self):
        """Test fallback natural language summary"""
        analyzer = AIAnalyzer()
        
        email_summaries = [
            {
                'subject': 'Test Email',
                'sender': 'Test Sender',
                'category': 'work',
                'priority': 'high',
                'is_read': False
            }
        ]
        
        summary = analyzer._fallback_natural_summary(email_summaries)
        
        assert summary is not None
        assert len(summary) > 0
        assert "1" in summary  # Should mention number of emails 