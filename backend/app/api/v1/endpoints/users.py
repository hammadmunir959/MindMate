"""
User Profile Management Router
==============================
Handles user profile operations for both patients and specialists.
Provides endpoints for profile management, updates, and retrieval.

Endpoints:
- GET /patient/profile: Get patient profile information
- PUT /patient/profile: Update patient profile
- GET /specialist/profile: Get specialist profile information
- PUT /specialist/profile: Update specialist profile

Author: Mental Health Platform Team
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.db.session import get_db
from app.services.patient_profiles import create_patient_private_profile_response
from app.api.v1.endpoints.auth import get_current_user_from_token
from app.models.specialist import EmailVerificationStatusEnum, ApprovalStatusEnum

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# PATIENT PROFILE ENDPOINTS
# ============================================================================

@router.get("/patient/profile")
async def get_patient_profile(
    current_user_data: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive patient profile information for the current user.
    Returns detailed patient profile including personal information, medical history,
    mood tracking, exercise progress, goals, journal entries, and appointments.
    """
    try:
        from app.models import (
            Patient, MoodAssessment, ExerciseProgress, ExerciseSession, 
            UserGoal, UserStreak, JournalEntry, Appointment,
            MandatoryQuestionnaireSubmission
        )
        from app.models.appointment import AppointmentStatusEnum
        from sqlalchemy import func, desc
        from datetime import datetime, timedelta, date
        
        user = current_user_data["user"]
        user_type = current_user_data["user_type"]

        if user_type != "patient":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Patient profile only accessible to patients."
            )

        logger.info(f"Getting comprehensive patient profile for {user.email}")
        
        # Get patient basic info
        patient = db.query(Patient).filter(
            Patient.id == user.id,
            Patient.is_deleted == False
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get questionnaire data
        questionnaire = db.query(MandatoryQuestionnaireSubmission).filter(
            MandatoryQuestionnaireSubmission.patient_id == user.id
        ).first()
        
        # Get mood tracking statistics
        mood_stats = db.query(
            func.count(MoodAssessment.id).label('total_assessments'),
            func.avg(MoodAssessment.overall_mood_score).label('avg_mood'),
            func.max(MoodAssessment.assessment_date).label('last_assessment')
        ).filter(
            MoodAssessment.patient_id == user.id
        ).first()
        
        # Get recent mood assessments (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_moods = db.query(MoodAssessment).filter(
            MoodAssessment.patient_id == user.id,
            MoodAssessment.assessment_date >= thirty_days_ago
        ).order_by(desc(MoodAssessment.assessment_date)).limit(10).all()
        
        # Get exercise progress statistics
        exercise_stats = db.query(
            func.count(ExerciseProgress.id).label('total_exercises'),
            func.sum(ExerciseProgress.completion_count).label('total_completions'),
            func.sum(ExerciseProgress.total_time_seconds).label('total_time')
        ).filter(
            ExerciseProgress.patient_id == user.id
        ).first()
        
        # Get recent exercise sessions
        recent_sessions = db.query(ExerciseSession).filter(
            ExerciseSession.patient_id == user.id,
            ExerciseSession.session_completed == True
        ).order_by(desc(ExerciseSession.start_time)).limit(5).all()
        
        # Get user streak
        streak = db.query(UserStreak).filter(
            UserStreak.patient_id == user.id
        ).first()
        
        # Get active goals
        from app.models.progress import GoalStatus
        active_goals = db.query(UserGoal).filter(
            UserGoal.patient_id == user.id,
            UserGoal.status == GoalStatus.ACTIVE
        ).all()
        
        # Get journal statistics
        journal_stats = db.query(
            func.count(JournalEntry.id).label('total_entries'),
            func.max(JournalEntry.entry_date).label('last_entry')
        ).filter(
            JournalEntry.patient_id == user.id,
            JournalEntry.is_archived == False
        ).first()
        
        # Get appointments
        upcoming_appointments = db.query(Appointment).filter(
            Appointment.patient_id == user.id,
            Appointment.scheduled_start > datetime.utcnow(),
            Appointment.status.in_([AppointmentStatusEnum.SCHEDULED, AppointmentStatusEnum.CONFIRMED])
        ).order_by(Appointment.scheduled_start).limit(5).all()
        
        past_appointments_count = db.query(func.count(Appointment.id)).filter(
            Appointment.patient_id == user.id,
            Appointment.status == AppointmentStatusEnum.COMPLETED
        ).scalar()
        
        # Build comprehensive response
        return {
            # Personal Information
            "personal_info": {
                "id": str(patient.id),
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "full_name": patient.full_name,
                "email": patient.email,
                "phone": patient.phone,
                "age": patient.age,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "gender": patient.gender.value if patient.gender else None,
                "primary_language": patient.primary_language.value if patient.primary_language else None,
            },
            
            # Location Information
            "location": {
                "city": patient.city,
                "district": patient.district,
                "province": patient.province,
                "postal_code": patient.postal_code,
                "country": patient.country,
                "full_address": patient.full_address
            },
            
            # Medical History (from questionnaire)
            "medical_history": {
                "chief_complaint": questionnaire.chief_complaint if questionnaire else None,
                "past_psychiatric_diagnosis": questionnaire.past_psychiatric_diagnosis if questionnaire else None,
                "past_psychiatric_treatment": questionnaire.past_psychiatric_treatment if questionnaire else None,
                "current_medications": questionnaire.current_medications if questionnaire else None,
                "medication_allergies": questionnaire.medication_allergies if questionnaire else None,
                "chronic_illnesses": questionnaire.chronic_illnesses if questionnaire else None,
                "alcohol_use": questionnaire.alcohol_use if questionnaire else None,
                "tobacco_use": questionnaire.tobacco_use if questionnaire else None,
                "family_mental_health_history": questionnaire.family_mental_health_history if questionnaire else None,
            } if questionnaire else None,
            
            # Mood Tracking Statistics
            "mood_tracking": {
                "total_assessments": mood_stats.total_assessments if mood_stats else 0,
                "average_mood": round(float(mood_stats.avg_mood), 2) if mood_stats and mood_stats.avg_mood else None,
                "last_assessment_date": mood_stats.last_assessment.isoformat() if mood_stats and mood_stats.last_assessment else None,
                "recent_assessments": [
                    {
                        "date": mood.assessment_date.isoformat(),
                        "overall_score": mood.overall_mood_score,
                        "overall_label": mood.overall_mood_label,
                        "stress_level": mood.stress_level,
                        "energy_level": mood.energy_level,
                        "gratitude_level": mood.gratitude_level,
                        "reflection_level": mood.reflection_level,
                        "dominant_emotions": mood.dominant_emotions
                    } for mood in recent_moods
                ]
            },
            
            # Exercise Progress Statistics
            "exercise_progress": {
                "total_exercises": exercise_stats.total_exercises if exercise_stats else 0,
                "total_completions": exercise_stats.total_completions if exercise_stats else 0,
                "total_hours": round((exercise_stats.total_time if exercise_stats and exercise_stats.total_time else 0) / 3600, 2),
                "recent_sessions": [
                    {
                        "exercise_name": session.exercise_name,
                        "date": session.start_time.isoformat(),
                        "duration_minutes": session.duration_minutes,
                        "mood_before": session.mood_before,
                        "mood_after": session.mood_after,
                        "mood_improvement": session.mood_improvement,
                        "completed": session.session_completed
                    } for session in recent_sessions
                ]
            },
            
            # Streak Information
            "streak": {
                "current_streak": streak.current_streak if streak else 0,
                "longest_streak": streak.longest_streak if streak else 0,
                "total_practice_days": streak.total_practice_days if streak else 0,
                "last_practice_date": streak.last_practice_date.isoformat() if streak and streak.last_practice_date else None,
                "is_active": streak.is_active if streak else False
            },
            
            # Active Goals
            "goals": [
                {
                    "id": str(goal.id),
                    "title": goal.title,
                    "description": goal.description,
                    "goal_type": goal.goal_type.value,
                    "target_value": goal.target_value,
                    "current_value": goal.current_value,
                    "progress_percentage": goal.progress_percentage,
                    "deadline": goal.deadline.isoformat() if goal.deadline else None,
                    "days_remaining": goal.days_remaining,
                    "is_completed": goal.is_completed
                } for goal in active_goals
            ],
            
            # Journal Statistics
            "journal": {
                "total_entries": journal_stats.total_entries if journal_stats else 0,
                "last_entry_date": journal_stats.last_entry.isoformat() if journal_stats and journal_stats.last_entry else None
            },
            
            # Appointments
            "appointments": {
                "total_completed": past_appointments_count if past_appointments_count else 0,
                "upcoming": [
                    {
                        "id": str(appt.id),
                        "scheduled_start": appt.scheduled_start.isoformat(),
                        "scheduled_end": appt.scheduled_end.isoformat(),
                        "appointment_type": appt.appointment_type.value if appt.appointment_type else None,
                        "status": appt.status.value if appt.status else None,
                        "fee": float(appt.fee) if appt.fee else None,
                        "payment_status": appt.payment_status.value if appt.payment_status else None
                    } for appt in upcoming_appointments
                ]
            },
            
            # Account Information
            "account": {
                "record_status": patient.record_status.value if patient.record_status else None,
                "intake_completed_date": patient.intake_completed_date.isoformat() if patient.intake_completed_date else None,
                "last_contact_date": patient.last_contact_date.isoformat() if patient.last_contact_date else None,
                "created_at": patient.created_at.isoformat() if patient.created_at else None,
                "accepts_terms_and_conditions": patient.accepts_terms_and_conditions
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patient profile: {str(e)}"
        )

# ============================================================================
# SPECIALIST PROFILE ENDPOINTS
# ============================================================================

@router.get("/specialist/profile")
async def get_specialist_profile(
    current_user_data: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive specialist profile information for the current user.
    Returns detailed specialist profile including professional information,
    specializations, availability, appointments, ratings, and approval status.
    """
    try:
        from app.models.specialist import (
            Specialists, SpecialistsApprovalData, SpecialistSpecializations, 
            SpecialistAvailability, SpecialistTimeSlots
        )
        from app.models.appointment import Appointment, AppointmentStatusEnum
        from sqlalchemy import func, desc
        from datetime import datetime, timedelta, date
        
        user = current_user_data["user"]
        user_type = current_user_data["user_type"]

        if user_type != "specialist":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Specialist profile only accessible to specialists."
            )

        logger.info(f"Getting comprehensive specialist profile for {user.email}")
        
        # Get specialist basic info
        specialist = db.query(Specialists).filter(
            Specialists.id == user.id,
            Specialists.is_deleted == False
        ).first()
        
        if not specialist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialist not found"
            )
        
        # Get approval data
        approval_data = db.query(SpecialistsApprovalData).filter(
            SpecialistsApprovalData.specialist_id == user.id
        ).first()
        
        # Get specializations
        specializations = db.query(SpecialistSpecializations).filter(
            SpecialistSpecializations.specialist_id == user.id
        ).all()
        
        # Get availability slots
        availability_slots = db.query(SpecialistAvailability).filter(
            SpecialistAvailability.specialist_id == user.id,
            SpecialistAvailability.is_active == True
        ).all()
        
        # Get upcoming time slots (next 30 days)
        thirty_days_from_now = datetime.utcnow() + timedelta(days=30)
        upcoming_slots = db.query(SpecialistTimeSlots).filter(
            SpecialistTimeSlots.specialist_id == user.id,
            SpecialistTimeSlots.slot_date >= date.today(),
            SpecialistTimeSlots.slot_date <= thirty_days_from_now.date(),
            SpecialistTimeSlots.is_available == True
        ).order_by(SpecialistTimeSlots.start_time).limit(20).all()
        
        # Get appointment statistics
        appointment_stats = db.query(
            func.count(Appointment.id).label('total_appointments'),
            func.count(Appointment.id).filter(Appointment.status == AppointmentStatusEnum.CONFIRMED).label('confirmed_appointments'),
            func.count(Appointment.id).filter(Appointment.status == AppointmentStatusEnum.COMPLETED).label('completed_appointments'),
            func.count(Appointment.id).filter(Appointment.status == AppointmentStatusEnum.CANCELLED).label('cancelled_appointments'),
            func.max(Appointment.scheduled_start).label('last_appointment')
        ).filter(
            Appointment.specialist_id == user.id
        ).first()
        
        # Get recent appointments (last 10)
        recent_appointments = db.query(Appointment).filter(
            Appointment.specialist_id == user.id
        ).order_by(desc(Appointment.scheduled_start)).limit(10).all()
        
        # Get monthly appointment trends (last 6 months)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_stats = db.query(
            func.date_trunc('month', Appointment.scheduled_start).label('month'),
            func.count(Appointment.id).label('appointment_count')
        ).filter(
            Appointment.specialist_id == user.id,
            Appointment.scheduled_start >= six_months_ago
        ).group_by(func.date_trunc('month', Appointment.scheduled_start)).all()
        
        # Calculate profile completion percentage
        profile_fields = [
            specialist.first_name, specialist.last_name, specialist.email,
            specialist.phone, specialist.specialist_type, specialist.years_experience,
            specialist.city, specialist.clinic_name, specialist.bio,
            specialist.consultation_fee, specialist.languages_spoken
        ]
        completed_fields = sum(1 for field in profile_fields if field is not None and field != "")
        profile_completion_percentage = int((completed_fields / len(profile_fields)) * 100)
        
        # Build comprehensive profile response
        profile_data = {
            # Basic Information
            "specialist_id": str(specialist.id),
            "email": specialist.email,
            "first_name": specialist.first_name,
            "last_name": specialist.last_name,
            "full_name": specialist.full_name,
            "phone": specialist.phone,
            "cnic_number": specialist.cnic_number,
            "date_of_birth": specialist.date_of_birth.isoformat() if specialist.date_of_birth else None,
            "gender": specialist.gender.value if specialist.gender else None,
            
            # Professional Information
            "specialist_type": specialist.specialist_type.value if specialist.specialist_type else None,
            "years_experience": specialist.years_experience,
            "qualification": specialist.qualification,
            "institution": specialist.institution,
            "current_affiliation": specialist.current_affiliation,
            "bio": specialist.bio,
            "experience_summary": specialist.experience_summary,
            
            # Practice Details
            "clinic_name": specialist.clinic_name,
            "clinic_address": specialist.clinic_address,
            "city": specialist.city,
            "address": specialist.address,
            "consultation_fee": float(specialist.consultation_fee) if specialist.consultation_fee else None,
            "currency": specialist.currency,
            "consultation_modes": specialist.consultation_modes,
            "languages_spoken": specialist.languages_spoken,
            
            # Specializations
            "specializations": [
                {
                    "specialization": spec.specialization.value,
                    "years_of_experience": spec.years_of_experience_in_specialization,
                    "certification_date": spec.certification_date.isoformat() if spec.certification_date else None,
                    "is_primary": spec.is_primary_specialization
                }
                for spec in specializations
            ],
            "primary_specialization": next(
                (spec.specialization.value for spec in specializations if spec.is_primary_specialization), 
                None
            ),
            
            # Therapy Methods & Specialties
            "therapy_methods": specialist.therapy_methods,
            "specialties_in_mental_health": specialist.specialties_in_mental_health,
            
            # Availability
            "availability_status": specialist.availability_status.value if specialist.availability_status else None,
            "accepting_new_patients": specialist.accepting_new_patients,
            "availability_schedule": specialist.availability_schedule,
            "available_time_slots": [slot.time_slot.value for slot in availability_slots],
            "upcoming_slots": [
                {
                    "slot_id": str(slot.id),
                    "date": slot.slot_date.isoformat(),
                    "start_time": slot.start_time.isoformat(),
                    "end_time": slot.end_time.isoformat(),
                    "duration_minutes": slot.duration_minutes,
                    "is_available": slot.is_available
                }
                for slot in upcoming_slots
            ],
            
            # Status & Verification
            "approval_status": specialist.approval_status.value if specialist.approval_status else None,
            "profile_verified": specialist.profile_verified,
            "verification_notes": specialist.verification_notes,
            "can_practice": specialist.can_practice,
            
            # Ratings & Reviews
            "average_rating": float(specialist.average_rating) if specialist.average_rating else 0.0,
            "total_reviews": specialist.total_reviews,
            "total_appointments": specialist.total_appointments,
            
            # Appointment Statistics
            "appointment_stats": {
                "total_appointments": appointment_stats.total_appointments or 0,
                "confirmed_appointments": appointment_stats.confirmed_appointments or 0,
                "completed_appointments": appointment_stats.completed_appointments or 0,
                "cancelled_appointments": appointment_stats.cancelled_appointments or 0,
                "last_appointment": appointment_stats.last_appointment.isoformat() if appointment_stats.last_appointment else None
            },
            
            # Recent Appointments
            "recent_appointments": [
                {
                    "appointment_id": str(apt.id),
                    "patient_id": str(apt.patient_id),
                    "scheduled_start": apt.scheduled_start.isoformat() if apt.scheduled_start else None,
                    "scheduled_end": apt.scheduled_end.isoformat() if apt.scheduled_end else None,
                    "status": apt.status.value if apt.status else None,
                    "appointment_type": apt.appointment_type.value if apt.appointment_type else None,
                    "fee": float(apt.fee) if apt.fee else None,
                    "notes": apt.notes,
                    "presenting_concern": apt.presenting_concern,
                    "request_message": apt.request_message,
                    "specialist_response": apt.specialist_response
                }
                for apt in recent_appointments
            ],
            
            # Monthly Trends
            "monthly_appointment_trends": [
                {
                    "month": stat.month.isoformat(),
                    "appointment_count": stat.appointment_count
                }
                for stat in monthly_stats
            ],
            
            # Profile Completion
            "profile_complete": profile_completion_percentage >= 80,
            "profile_completion_percentage": profile_completion_percentage,
            "mandatory_fields_completed": all([
                specialist.first_name, specialist.last_name, specialist.email,
                specialist.specialist_type, specialist.city
            ]),
            
            # Approval Data (if available)
            "approval_data": {
                "license_number": approval_data.license_number if approval_data else None,
                "license_issuing_authority": approval_data.license_issuing_authority if approval_data else None,
                "license_issue_date": approval_data.license_issue_date.isoformat() if approval_data and approval_data.license_issue_date else None,
                "license_expiry_date": approval_data.license_expiry_date.isoformat() if approval_data and approval_data.license_expiry_date else None,
                "highest_degree": approval_data.highest_degree if approval_data else None,
                "university_name": approval_data.university_name if approval_data else None,
                "graduation_year": approval_data.graduation_year if approval_data else None,
                "professional_memberships": approval_data.professional_memberships if approval_data else None,
                "certifications": approval_data.certifications if approval_data else None,
                "submission_date": approval_data.submission_date.isoformat() if approval_data and approval_data.submission_date else None,
                "reviewed_at": approval_data.reviewed_at.isoformat() if approval_data and approval_data.reviewed_at else None,
                "approval_notes": approval_data.approval_notes if approval_data else None
            } if approval_data else None,
            
            # Metadata
            "profile_image_url": specialist.profile_image_url,
            "website_url": specialist.website_url,
            "social_media_links": specialist.social_media_links,
            "created_at": specialist.created_at.isoformat() if specialist.created_at else None,
            "updated_at": specialist.updated_at.isoformat() if specialist.updated_at else None,
            
            # User Type
            "user_type": user_type
        }
        
        logger.info(f"Successfully retrieved comprehensive specialist profile for {user.email}")
        return profile_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting specialist profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve specialist profile: {str(e)}"
        )

@router.put("/specialist/profile")
async def update_specialist_profile(
    profile_data: dict,
    current_user_data: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Update specialist profile information for the current user.
    Allows updating professional information, specializations, availability, and practice details.
    Supports configurable non-sensitive fields and enhanced slots management.
    """
    try:
        from app.models.specialist import (
            Specialists, SpecialistsApprovalData, SpecialistSpecializations, 
            SpecialistAvailability, SpecialistTimeSlots
        )
        from sqlalchemy import and_
        from datetime import datetime, timedelta, date
        
        user = current_user_data["user"]
        user_type = current_user_data["user_type"]

        if user_type != "specialist":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Specialist profile only accessible to specialists."
            )

        logger.info(f"Updating specialist profile for {user.email}")

        # Get specialist record
        specialist = db.query(Specialists).filter(
            Specialists.id == user.id,
            Specialists.is_deleted == False
        ).first()
        
        if not specialist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialist not found"
            )

        # Define sensitive fields that require special handling
        sensitive_fields = ["email", "cnic_number", "password"]
        
        # Update basic information (non-sensitive fields)
        basic_fields = [
            "first_name", "last_name", "phone", "date_of_birth", "gender",
            "specialist_type", "years_experience", "qualification", "institution",
            "current_affiliation", "bio", "experience_summary", "clinic_name",
            "clinic_address", "city", "address", "consultation_fee", "currency",
            "consultation_modes", "languages_spoken", "therapy_methods",
            "specialties_in_mental_health", "availability_status", "accepting_new_patients",
            "availability_schedule", "profile_image_url", "website_url", "social_media_links"
        ]
        
        # Enum fields that should be None if empty string
        enum_fields = ["gender", "specialist_type", "availability_status"]
        
        for field in basic_fields:
            if field in profile_data:
                value = profile_data[field]
                # Convert empty strings to None for enum fields
                if field in enum_fields and value == "":
                    value = None
                # Handle date fields
                elif field == "date_of_birth" and value:
                    from datetime import datetime
                    if isinstance(value, str):
                        # Parse ISO format string to date object
                        try:
                            value = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
                        except (ValueError, AttributeError):
                            logger.warning(f"Invalid date format for {field}: {value}")
                            value = None
                # Handle numeric fields
                elif field in ["consultation_fee", "years_experience"]:
                    if isinstance(value, str):
                        try:
                            value = float(value) if field == "consultation_fee" else int(value)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid numeric format for {field}: {value}")
                            value = None
                setattr(specialist, field, value)

        # Handle sensitive fields with validation
        if "email" in profile_data:
            # Email change requires verification
            new_email = profile_data["email"]
            if new_email != specialist.email:
                # Check if email already exists
                existing_specialist = db.query(Specialists).filter(
                    Specialists.email == new_email,
                    Specialists.id != user.id
                ).first()
                if existing_specialist:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
                specialist.email = new_email
                # Update email verification status in auth info
                from app.models.specialist import SpecialistsAuthInfo
                auth_info = db.query(SpecialistsAuthInfo).filter(
                    SpecialistsAuthInfo.specialist_id == user.id
                ).first()
                if auth_info:
                    auth_info.email_verification_status = EmailVerificationStatusEnum.PENDING

        if "cnic_number" in profile_data:
            # CNIC change requires admin approval
            specialist.cnic_number = profile_data["cnic_number"]
            specialist.approval_status = ApprovalStatusEnum.PENDING

        # Update specializations if provided
        if "specializations" in profile_data:
            # Remove existing specializations
            db.query(SpecialistSpecializations).filter(
                SpecialistSpecializations.specialist_id == user.id
            ).delete()
            
            # Add new specializations
            for spec_data in profile_data["specializations"]:
                new_spec = SpecialistSpecializations(
                    specialist_id=user.id,
                    specialization=spec_data.get("specialization"),
                    years_of_experience_in_specialization=spec_data.get("years_of_experience", 0),
                    certification_date=spec_data.get("certification_date"),
                    is_primary_specialization=spec_data.get("is_primary", False)
                )
                db.add(new_spec)

        # Enhanced availability slots management
        if "weekly_schedule" in profile_data:
            # Store weekly schedule in the specialist's availability_schedule JSON field
            # This is different from the SpecialistAvailability table which stores specific time slots
            weekly_schedule = profile_data["weekly_schedule"]
            
            # Convert templates to the expected format: {"Mon": ["10:00-14:00"], "Wed": ["14:00-18:00"]}
            schedule_dict = {}
            for day_schedule in weekly_schedule.get("templates", []):
                weekday = day_schedule.get("weekday")
                is_active = day_schedule.get("is_active", True)
                
                if is_active and weekday:
                    # Convert weekday to proper format (monday -> Mon, tuesday -> Tue, etc.)
                    day_mapping = {
                        "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
                        "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun"
                    }
                    day_key = day_mapping.get(weekday.lower(), weekday.capitalize())
                    
                    # Default time slots for each day (can be customized later)
                    schedule_dict[day_key] = ["10:00-14:00", "16:00-20:00"]
            
            # Update the specialist's availability_schedule field
            specialist.availability_schedule = schedule_dict

        # Handle time slots generation
        if "generate_slots" in profile_data:
            slot_generation = profile_data["generate_slots"]
            start_date = datetime.strptime(slot_generation["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(slot_generation["end_date"], "%Y-%m-%d").date()
            
            # Generate slots for the date range
            current_date = start_date
            while current_date <= end_date:
                # Get weekday template from availability_schedule JSON field
                weekday = current_date.strftime("%A").lower()
                day_mapping = {
                    "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
                    "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun"
                }
                day_key = day_mapping.get(weekday, weekday.capitalize())
                
                # Check if this day is available in the specialist's schedule
                availability_schedule = specialist.availability_schedule or {}
                if day_key in availability_schedule and availability_schedule[day_key]:
                    # Generate time slots for this date
                    start_time = datetime.strptime(slot_generation.get("start_time", "09:00"), "%H:%M").time()
                    end_time = datetime.strptime(slot_generation.get("end_time", "17:00"), "%H:%M").time()
                    duration_minutes = slot_generation.get("duration_minutes", 30)
                    
                    current_time = datetime.combine(current_date, start_time)
                    end_datetime = datetime.combine(current_date, end_time)
                    
                    while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
                        slot_end = current_time + timedelta(minutes=duration_minutes)
                        
                        # Check if slot already exists
                        existing_slot = db.query(SpecialistTimeSlots).filter(
                            SpecialistTimeSlots.specialist_id == user.id,
                            SpecialistTimeSlots.slot_date == current_date,
                            SpecialistTimeSlots.start_time == current_time
                        ).first()
                        
                        if not existing_slot:
                            new_slot = SpecialistTimeSlots(
                                specialist_id=user.id,
                                slot_date=current_date,
                                start_time=current_time,
                                end_time=slot_end,
                                is_available=True,
                                is_blocked=False
                            )
                            db.add(new_slot)
                        
                        current_time = slot_end
                
                current_date += timedelta(days=1)

        # Update approval data if provided
        if "approval_data" in profile_data:
            approval_data = db.query(SpecialistsApprovalData).filter(
                SpecialistsApprovalData.specialist_id == user.id
            ).first()
            
            if not approval_data:
                approval_data = SpecialistsApprovalData(specialist_id=user.id)
                db.add(approval_data)
            
            approval_info = profile_data["approval_data"]
            approval_fields = [
                "license_number", "license_issuing_authority", "license_issue_date",
                "license_expiry_date", "highest_degree", "university_name",
                "graduation_year", "professional_memberships", "certifications"
            ]
            
            for field in approval_fields:
                if field in approval_info:
                    setattr(approval_data, field, approval_info[field])

        # Save changes
        db.commit()
        
        logger.info(f"Successfully updated specialist profile for {user.email}")
        # Get email verification status from auth info
        from app.models.specialist import SpecialistsAuthInfo
        auth_info = db.query(SpecialistsAuthInfo).filter(
            SpecialistsAuthInfo.specialist_id == user.id
        ).first()
        
        return {
            "message": "Specialist profile updated successfully",
            "specialist_id": str(specialist.id),
            "updated_at": specialist.updated_at.isoformat() if specialist.updated_at else None,
            "requires_verification": auth_info.email_verification_status == EmailVerificationStatusEnum.PENDING if auth_info else False,
            "requires_approval": specialist.approval_status == ApprovalStatusEnum.PENDING
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating specialist profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update specialist profile: {str(e)}"
        )

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/health")
async def user_router_health():
    """Health check for user router"""
    return {
        "status": "healthy",
        "service": "user-router",
        "endpoints": [
            "GET /patient/profile",
            "GET /specialist/profile"
        ]
    }
