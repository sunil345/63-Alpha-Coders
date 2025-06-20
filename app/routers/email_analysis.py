from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import os

from app.models import (
    EmailSummary, DailySummary, AnalysisRequest, 
    EmailCategory, PriorityLevel
)
from app.core.email_processor import EmailProcessor
from app.core.database import db
from app.core.ai_analyzer import AIAnalyzer

router = APIRouter(
    prefix="/api/email",
    tags=["Email Analysis"],
    responses={404: {"description": "Not found"}},
)

@router.get("/summary/{date}", response_model=DailySummary)
async def get_daily_summary(date_str: str):
    """Get daily email summary for a specific date"""
    try:
        # Validate date format
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get summary from database
        summary = db.get_daily_summary(date_str)
        
        if not summary:
            raise HTTPException(status_code=404, detail="No summary found for this date")
        
        return DailySummary(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/{date}", response_model=List[EmailSummary])
async def get_emails_by_date(
    date_str: str,
    category: Optional[EmailCategory] = Query(None, description="Filter by category"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority"),
    limit: int = Query(50, description="Maximum number of emails to return")
):
    """Get emails for a specific date with optional filtering"""
    try:
        # Validate date format
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get emails from database
        emails = db.get_emails_by_date(date_str)
        
        # Apply filters
        if category:
            emails = [e for e in emails if e['category'] == category]
        
        if priority:
            emails = [e for e in emails if e['priority'] == priority]
        
        # Apply limit
        emails = emails[:limit]
        
        return [EmailSummary(**email) for email in emails]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_emails(request: AnalysisRequest):
    """Analyze emails based on request parameters"""
    try:
        processor = EmailProcessor()
        
        # Determine date range
        if request.date_range == "today":
            target_date = datetime.now().strftime('%Y-%m-%d')
        elif request.date_range == "yesterday":
            target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            target_date = request.date_range
        
        # Process emails
        email_summaries = processor.process_inbox(target_date)
        
        # Apply filters
        if request.categories_filter:
            email_summaries = [
                e for e in email_summaries 
                if e['category'] in request.categories_filter
            ]
        
        if request.priority_filter:
            email_summaries = [
                e for e in email_summaries 
                if e['priority'] in request.priority_filter
            ]
        
        # Generate analysis results
        analysis_results = {
            "date": target_date,
            "total_emails": len(email_summaries),
            "categories": {},
            "priorities": {},
            "urgent_emails": [],
            "unread_emails": [],
            "response_reminders": []
        }
        
        # Count categories and priorities
        for email in email_summaries:
            category = email['category']
            priority = email['priority']
            
            analysis_results['categories'][category] = analysis_results['categories'].get(category, 0) + 1
            analysis_results['priorities'][priority] = analysis_results['priorities'].get(priority, 0) + 1
            
            # Check for urgent emails
            if email['priority'] in ['high', 'urgent'] or email['urgency_score'] >= 0.7:
                analysis_results['urgent_emails'].append(email)
            
            # Check for unread emails
            if not email['is_read']:
                analysis_results['unread_emails'].append(email)
            
            # Check for response reminders
            if not email['is_replied'] and email['action_required']:
                analysis_results['response_reminders'].append(email)
        
        return analysis_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/urgent", response_model=List[EmailSummary])
async def get_urgent_emails(limit: int = Query(10, description="Maximum number of urgent emails to return")):
    """Get urgent emails that need immediate attention"""
    try:
        # Get today's emails
        today = datetime.now().strftime('%Y-%m-%d')
        emails = db.get_emails_by_date(today)
        
        # Filter for urgent emails
        urgent_emails = [
            e for e in emails 
            if e['priority'] in ['high', 'urgent'] or e['urgency_score'] >= 0.7
        ]
        
        # Sort by urgency score (highest first)
        urgent_emails.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        # Apply limit
        urgent_emails = urgent_emails[:limit]
        
        return [EmailSummary(**email) for email in urgent_emails]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unread", response_model=List[EmailSummary])
async def get_unread_emails(limit: int = Query(20, description="Maximum number of unread emails to return")):
    """Get unread emails"""
    try:
        # Get today's emails
        today = datetime.now().strftime('%Y-%m-%d')
        emails = db.get_emails_by_date(today)
        
        # Filter for unread emails
        unread_emails = [e for e in emails if not e['is_read']]
        
        # Sort by received date (newest first)
        unread_emails.sort(key=lambda x: x['received_at'], reverse=True)
        
        # Apply limit
        unread_emails = unread_emails[:limit]
        
        return [EmailSummary(**email) for email in unread_emails]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reminders", response_model=List[EmailSummary])
async def get_response_reminders(limit: int = Query(10, description="Maximum number of reminders to return")):
    """Get emails that need responses"""
    try:
        # Get today's emails
        today = datetime.now().strftime('%Y-%m-%d')
        emails = db.get_emails_by_date(today)
        
        # Filter for emails that need responses
        reminder_emails = [
            e for e in emails 
            if not e['is_replied'] and e['action_required']
        ]
        
        # Sort by received date (oldest first, as they need attention)
        reminder_emails.sort(key=lambda x: x['received_at'])
        
        # Apply limit
        reminder_emails = reminder_emails[:limit]
        
        return [EmailSummary(**email) for email in reminder_emails]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", response_model=Dict[str, int])
async def get_category_stats(date_str: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")):
    """Get email category statistics"""
    try:
        if date_str:
            # Validate date format
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            
            emails = db.get_emails_by_date(date_str)
        else:
            # Get today's emails
            today = datetime.now().strftime('%Y-%m-%d')
            emails = db.get_emails_by_date(today)
        
        # Count categories
        categories = {}
        for email in emails:
            category = email['category']
            categories[category] = categories.get(category, 0) + 1
        
        return categories
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/priorities", response_model=Dict[str, int])
async def get_priority_stats(date_str: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")):
    """Get email priority statistics"""
    try:
        if date_str:
            # Validate date format
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            
            emails = db.get_emails_by_date(date_str)
        else:
            # Get today's emails
            today = datetime.now().strftime('%Y-%m-%d')
            emails = db.get_emails_by_date(today)
        
        # Count priorities
        priorities = {}
        for email in emails:
            priority = email['priority']
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return priorities
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-read/{email_id}")
async def mark_email_as_read(email_id: str):
    """Mark an email as read"""
    try:
        # This would typically update the database
        # For now, we'll return a success message
        return {"message": f"Email {email_id} marked as read", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-replied/{email_id}")
async def mark_email_as_replied(email_id: str):
    """Mark an email as replied"""
    try:
        # This would typically update the database
        # For now, we'll return a success message
        return {"message": f"Email {email_id} marked as replied", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/natural-summary/{date}")
async def get_natural_language_summary(date_str: str):
    """Get natural language summary of emails for a specific date"""
    try:
        # Validate date format
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get emails for the date
        emails = db.get_emails_by_date(date_str)
        
        if not emails:
            return {"summary": f"No emails found for {date_str}"}
        
        # Generate natural language summary
        ai_analyzer = AIAnalyzer()
        summary = ai_analyzer.generate_natural_language_summary(emails)
        
        return {
            "date": date_str,
            "total_emails": len(emails),
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 