"""
Dashboard Service - Business Logic for Dashboard
==============================================
Handles all dashboard data aggregation and business logic.

Author: MindMate Team
Version: 2.0.0
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, select
import redis
import logging

from app.models.patient import Patient, ExerciseProgress, ExerciseSession, UserStreak, JournalEntry, MoodAssessment
from app.models.appointment import Appointment
from app.schemas.dashboard import (
    DashboardOverview,
    UserStats,
    ProgressData,
    AppointmentData,
    ActivityData,
    WellnessData,
    QuickAction,
    Notification,
    ActivityType,
    NotificationType
)

logger = logging.getLogger(__name__)

# Redis connection (configure as needed) - make it optional
_redis_client = None
_redis_available = False

def get_redis_client():
    """Get Redis client, initializing if needed. Returns None if Redis is unavailable."""
    global _redis_client, _redis_available
    
    if _redis_client is not None:
        return _redis_client if _redis_available else None
    
    try:
        _redis_client = redis.Redis(
            host='localhost', 
            port=6379, 
            db=0, 
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        # Test connection
        _redis_client.ping()
        _redis_available = True
        logger.info("Redis connection established")
        return _redis_client
    except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
        logger.warning(f"Redis not available, continuing without cache: {str(e)}")
        _redis_available = False
        return None


class DashboardService:
    """Service class for dashboard data operations"""
    
    @staticmethod
    async def get_dashboard_overview(db: Session, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data in a single optimized call
        """
        try:
            redis_client = get_redis_client()
            
            # Check cache first (if Redis is available)
            if redis_client:
                try:
                    cache_key = f"dashboard_overview:{patient_id}"
                    cached_data = redis_client.get(cache_key)
                    
                    if cached_data:
                        logger.info(f"Returning cached dashboard data for user {patient_id}")
                        return json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"Redis cache read failed, continuing without cache: {str(e)}")
            
            # Fetch all data in parallel
            tasks = [
                DashboardService.get_user_stats(db, patient_id),
                DashboardService.get_progress_data(db, patient_id),
                DashboardService.get_appointments_data(db, patient_id),
                DashboardService.get_activity_data(db, patient_id, 10),
                DashboardService.get_wellness_data(db, patient_id),
                DashboardService.get_quick_actions(db, patient_id),
                DashboardService.get_notifications(db, patient_id, False)
            ]
            
            results = await asyncio.gather(*tasks)
            
            dashboard_data = {
                "user_stats": results[0],
                "progress_data": results[1],
                "appointments": results[2],
                "recent_activity": results[3],
                "wellness_metrics": results[4],
                "quick_actions": results[5],
                "notifications": results[6],
                "last_updated": datetime.now().isoformat(),
                "cache_expires": (datetime.now() + timedelta(minutes=5)).isoformat()
            }
            
            # Cache the result for 5 minutes (if Redis is available)
            if redis_client:
                try:
                    cache_key = f"dashboard_overview:{patient_id}"
                    redis_client.setex(
                        cache_key, 
                        300,  # 5 minutes
                        json.dumps(dashboard_data, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Redis cache write failed: {str(e)}")
            
            logger.info(f"Dashboard data fetched for user {patient_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error fetching dashboard overview for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_user_stats(db: Session, patient_id: str) -> Dict[str, Any]:
        """Get user statistics and achievements"""
        try:
            # Get user
            user = db.query(Patient).filter(Patient.id == patient_id).first()
            if not user:
                raise ValueError(f"User {patient_id} not found")
            
            # Calculate statistics
            total_sessions = db.query(ExerciseSession).filter(
                ExerciseSession.patient_id == patient_id
            ).count()
            
            current_streak_record = db.query(UserStreak).filter(
                UserStreak.patient_id == patient_id
            ).first()
            
            current_streak_value = current_streak_record.current_streak if current_streak_record else 0
            longest_streak_value = current_streak_record.longest_streak if current_streak_record else 0
            
            total_exercises = db.query(ExerciseProgress).filter(
                ExerciseProgress.patient_id == patient_id
            ).count()
            
            # Calculate wellness score from recent mood entries
            # Use explicit select to avoid loading non-existent columns like mood_score
            mood_query = select(
                MoodAssessment.overall_mood_score
            ).filter(
                MoodAssessment.patient_id == patient_id
            ).order_by(desc(MoodAssessment.assessment_date)).limit(1)
            
            mood_result = db.execute(mood_query).first()
            recent_mood_score = mood_result[0] if mood_result and mood_result[0] is not None else None
            wellness_score = (float(recent_mood_score) * 10) if recent_mood_score else 50.0
            
            # Get last activity
            last_activity = db.query(ExerciseSession).filter(
                ExerciseSession.patient_id == patient_id
            ).order_by(desc(ExerciseSession.created_at)).first()
            
            return {
                "total_sessions": total_sessions,
                "current_streak": current_streak_value,
                "longest_streak": longest_streak_value,
                "total_exercises": total_exercises,
                "achievements_unlocked": 0,  # TODO: Implement achievements
                "total_goals": 0,  # TODO: Implement goals
                "completed_goals": 0,  # TODO: Implement goals
                "wellness_score": wellness_score,
                "last_active": last_activity.created_at.isoformat() if last_activity else None
            }
            
        except Exception as e:
            logger.error(f"Error fetching user stats for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_progress_data(db: Session, patient_id: str) -> Dict[str, Any]:
        """Get progress tracking data"""
        try:
            # Get current streak record
            current_streak_record = db.query(UserStreak).filter(
                UserStreak.patient_id == patient_id
            ).first()
            
            current_streak_value = current_streak_record.current_streak if current_streak_record else 0
            longest_streak_value = current_streak_record.longest_streak if current_streak_record else 0
            
            # Get total sessions
            total_sessions = db.query(ExerciseSession).filter(
                ExerciseSession.patient_id == patient_id
            ).count()
            
            # Get sessions this week
            week_start = datetime.now() - timedelta(days=7)
            sessions_this_week = db.query(ExerciseSession).filter(
                and_(
                    ExerciseSession.patient_id == patient_id,
                    ExerciseSession.created_at >= week_start
                )
            ).count()
            
            # Get sessions this month
            month_start = datetime.now() - timedelta(days=30)
            sessions_this_month = db.query(ExerciseSession).filter(
                and_(
                    ExerciseSession.patient_id == patient_id,
                    ExerciseSession.created_at >= month_start
                )
            ).count()
            
            # Calculate completion rate (simplified)
            completion_rate = min(100.0, (sessions_this_week / 7) * 100) if sessions_this_week > 0 else 0.0
            
            return {
                "current_streak": current_streak_value,
                "longest_streak": longest_streak_value,
                "total_sessions": total_sessions,
                "sessions_this_week": sessions_this_week,
                "sessions_this_month": sessions_this_month,
                "completion_rate": completion_rate,
                "goals_progress": [],  # TODO: Implement goals
                "recent_achievements": [],  # TODO: Implement achievements
                "next_milestone": None  # TODO: Implement milestones
            }
            
        except Exception as e:
            logger.error(f"Error fetching progress data for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_appointments_data(db: Session, patient_id: str) -> List[Dict[str, Any]]:
        """Get appointments data for dashboard"""
        try:
            # Use joinedload to avoid lazy loading issues
            from sqlalchemy.orm import joinedload
            
            appointments = db.query(Appointment).options(
                joinedload(Appointment.specialist)
            ).filter(
                Appointment.patient_id == patient_id
            ).order_by(Appointment.scheduled_start).limit(5).all()
            
            appointment_data = []
            for apt in appointments:
                specialist_name = "Unknown"
                specialist_specialty = "Unknown"
                
                if apt.specialist:
                    specialist_name = getattr(apt.specialist, 'name', None) or getattr(apt.specialist, 'first_name', '') + ' ' + getattr(apt.specialist, 'last_name', '')
                    specialist_specialty = getattr(apt.specialist, 'specialty', None) or "Unknown"
                
                # Calculate duration or use default
                duration_minutes = 60
                if apt.scheduled_start and apt.scheduled_end:
                    duration = apt.scheduled_end - apt.scheduled_start
                    duration_minutes = int(duration.total_seconds() / 60)
                
                appointment_data.append({
                    "id": str(apt.id),
                    "specialist_name": specialist_name.strip() or "Unknown",
                    "specialist_specialty": specialist_specialty or "Unknown",
                    "appointment_date": apt.scheduled_start.isoformat() if apt.scheduled_start else datetime.now().isoformat(),
                    "duration_minutes": duration_minutes,
                    "status": apt.status.value if hasattr(apt.status, 'value') else str(apt.status) if apt.status else "scheduled",
                    "location": getattr(apt, 'location', '') or "",
                    "notes": apt.notes or "",
                    "is_virtual": apt.appointment_type.value == 'virtual' if hasattr(apt.appointment_type, 'value') else str(apt.appointment_type) == 'virtual' if apt.appointment_type else False
                })
            
            return appointment_data
            
        except Exception as e:
            logger.error(f"Error fetching appointments data for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_activity_data(db: Session, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity data"""
        try:
            activities = []
            
            # Get recent exercise sessions
            exercise_sessions = db.query(ExerciseSession).filter(
                ExerciseSession.patient_id == patient_id
            ).order_by(desc(ExerciseSession.created_at)).limit(limit // 2).all()
            
            for session in exercise_sessions:
                activities.append({
                    "id": str(session.id),
                    "type": ActivityType.EXERCISE,
                    "title": "Exercise Session",
                    "description": f"Completed {session.exercise_type or 'exercise'}",
                    "timestamp": session.created_at.isoformat(),
                    "metadata": {"session_id": str(session.id)},
                    "icon": "activity"
                })
            
            # Get recent journal entries
            journal_entries = db.query(JournalEntry).filter(
                JournalEntry.patient_id == patient_id
            ).order_by(desc(JournalEntry.created_at)).limit(limit // 2).all()
            
            for entry in journal_entries:
                entry_timestamp = getattr(entry, "created_at", None) or getattr(entry, "entry_date", None)
                entry_content = (entry.content or "").strip()
                description = entry_content[:120] + ("..." if len(entry_content) > 120 else "")
                if not description:
                    description = "New journal entry"
                
                activities.append({
                    "id": str(entry.id),
                    "type": ActivityType.JOURNAL,
                    "title": "Journal Entry",
                    "description": description,
                    "timestamp": entry_timestamp.isoformat() if entry_timestamp else datetime.now().isoformat(),
                    "metadata": {"entry_id": str(entry.id)},
                    "icon": "book-open"
                })
            
            # Sort by timestamp and limit
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching activity data for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_wellness_data(db: Session, patient_id: str) -> Dict[str, Any]:
        """Get wellness metrics and mood data"""
        try:
            # Get recent mood entries - explicitly select only columns that exist in database
            # This avoids loading mood_score column that doesn't exist in the database
            # Explicitly select only columns that exist in the database
            mood_query = select(
                MoodAssessment.assessment_date,
                MoodAssessment.overall_mood_score,
                MoodAssessment.stress_level,
                MoodAssessment.energy_level,
                MoodAssessment.completed
            ).filter(
                MoodAssessment.patient_id == patient_id
            ).order_by(desc(MoodAssessment.assessment_date)).limit(7)
            
            result = db.execute(mood_query).all()
            
            # Convert results to list of dictionaries
            recent_moods = [
                {
                    'assessment_date': row.assessment_date,
                    'overall_mood_score': row.overall_mood_score,
                    'stress_level': row.stress_level,
                    'energy_level': row.energy_level,
                    'completed': row.completed
                }
                for row in result
            ]
            
            current_mood = float(recent_moods[0]['overall_mood_score']) if recent_moods and recent_moods[0]['overall_mood_score'] else 5.0
            last_mood_entry = recent_moods[0]['assessment_date'] if recent_moods else None
            
            # Calculate mood trend
            mood_trend = []
            for mood in recent_moods:
                if mood['overall_mood_score'] is not None:
                    mood_trend.append({
                        "date": mood['assessment_date'].isoformat(),
                        "score": float(mood['overall_mood_score'])
                    })
            
            # Calculate wellness score (mood_score is 0-10, convert to percentage)
            wellness_score = (current_mood / 10) * 100 if current_mood else 50.0
            
            # Get stress and energy from most recent mood assessment
            recent_stress = float(recent_moods[0]['stress_level']) if recent_moods and recent_moods[0]['stress_level'] is not None else 5.0
            recent_energy = float(recent_moods[0]['energy_level']) if recent_moods and recent_moods[0]['energy_level'] is not None else 5.0
            
            return {
                "current_mood": current_mood,
                "mood_trend": mood_trend,
                "wellness_score": wellness_score,
                "stress_level": recent_stress,
                "energy_level": recent_energy,
                "sleep_quality": None,  # TODO: Implement sleep tracking
                "exercise_frequency": 3,  # TODO: Calculate from actual data
                "social_connections": 7,  # TODO: Implement social tracking
                "last_mood_entry": last_mood_entry.isoformat() if last_mood_entry else None
            }
            
        except Exception as e:
            logger.error(f"Error fetching wellness data for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_quick_actions(db: Session, patient_id: str) -> List[Dict[str, Any]]:
        """Get available quick actions"""
        try:
            actions = [
                {
                    "id": "start_exercise",
                    "title": "Start Exercise",
                    "description": "Begin a new exercise session",
                    "icon": "activity",
                    "route": "/dashboard/exercises/start",
                    "color": "blue",
                    "is_available": True,
                    "metadata": {
                        "action_type": "modal",
                        "modal_type": "exercise",
                        "api_endpoint": "/api/exercises",
                        "api_method": "GET",
                        "requires_exercise_selection": True,
                        "start_session_endpoint": "/api/progress-tracker/sessions/start",
                        "start_session_method": "POST"
                    }
                },
                {
                    "id": "journal_entry",
                    "title": "Journal Entry",
                    "description": "Write in your journal",
                    "icon": "book-open",
                    "route": "/dashboard/journal/new",
                    "color": "green",
                    "is_available": True,
                    "metadata": {
                        "action_type": "modal",
                        "modal_type": "journal",
                        "api_endpoint": "/api/journal/entries",
                        "api_method": "POST",
                        "requires_form": True,
                        "form_fields": ["content", "mood", "tags"]
                    }
                },
                {
                    "id": "mood_check",
                    "title": "Mood Check",
                    "description": "Log your current mood",
                    "icon": "heart",
                    "route": "/dashboard/progress-tracker/mood",
                    "color": "purple",
                    "is_available": True,
                    "metadata": {
                        "action_type": "modal",
                        "modal_type": "mood",
                        "api_endpoint": "/api/progress-tracker/mood/session/start",
                        "api_method": "POST",
                        "requires_confirmation": False,
                        "opens_modal": True
                    }
                }
            ]
            
            return actions
            
        except Exception as e:
            logger.error(f"Error fetching quick actions for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_notifications(db: Session, patient_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get user notifications"""
        try:
            # TODO: Implement proper notification system
            # For now, return mock notifications
            notifications = [
                {
                    "id": "notif_1",
                    "type": NotificationType.APPOINTMENT,
                    "title": "Appointment Reminder",
                    "message": "You have an appointment tomorrow at 2:00 PM",
                    "is_read": False,
                    "created_at": datetime.now().isoformat(),
                    "action_url": "/appointments",
                    "priority": 3,
                    "metadata": {}
                },
                {
                    "id": "notif_2",
                    "type": NotificationType.ACHIEVEMENT,
                    "title": "Achievement Unlocked!",
                    "message": "You've completed 7 days in a row!",
                    "is_read": False,
                    "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "action_url": "/progress-tracker",
                    "priority": 2,
                    "metadata": {}
                }
            ]
            
            if unread_only:
                notifications = [n for n in notifications if not n["is_read"]]
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error fetching notifications for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_dashboard_updates(db: Session, patient_id: str, last_updated: Optional[datetime] = None) -> Dict[str, Any]:
        """Get incremental updates since last_updated timestamp"""
        try:
            # TODO: Implement real-time updates
            return {
                "updates": [],
                "last_updated": datetime.now().isoformat(),
                "has_updates": False
            }
            
        except Exception as e:
            logger.error(f"Error fetching dashboard updates for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def update_widget_preferences(db: Session, patient_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user's widget preferences"""
        try:
            # TODO: Implement widget preferences storage
            return {"success": True, "preferences": preferences}
            
        except Exception as e:
            logger.error(f"Error updating widget preferences for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_widget_preferences(db: Session, patient_id: str) -> Dict[str, Any]:
        """Get user's widget preferences"""
        try:
            # TODO: Implement widget preferences retrieval
            return {
                "widgets": [],
                "layout": {},
                "theme": "light",
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching widget preferences for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def export_dashboard_pdf(db: Session, patient_id: str) -> str:
        """Export dashboard data as PDF"""
        try:
            # TODO: Implement PDF export
            return f"/exports/dashboard_{patient_id}.pdf"
            
        except Exception as e:
            logger.error(f"Error exporting dashboard PDF for user {patient_id}: {str(e)}")
            raise
    
    @staticmethod
    async def export_dashboard_excel(db: Session, patient_id: str) -> str:
        """Export dashboard data as Excel"""
        try:
            # TODO: Implement Excel export
            return f"/exports/dashboard_{patient_id}.xlsx"
            
        except Exception as e:
            logger.error(f"Error exporting dashboard Excel for user {patient_id}: {str(e)}")
            raise
