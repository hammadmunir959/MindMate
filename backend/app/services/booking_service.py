"""
Booking Service
===============
Business logic for appointment booking and slot management.
"""

from typing import List, Dict, Optional
from datetime import datetime, date, time, timedelta
import random

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.repositories_new.appointment import appointment_repo
from app.db.repositories_new.specialist import specialist_repo
from app.models_new.appointment import Appointment, AppointmentStatus


class BookingService:
    """
    Service for managing bookings and slots.
    """
    
    def get_available_slots(
        self, db: Session, specialist_id: str, days: int = 7
    ) -> List[Dict]:
        """
        Get available slots for the next N days.
        Currently mocks availability (9 AM - 5 PM weekdays).
        """
        specialist = specialist_repo.get(db, specialist_id)
        if not specialist:
            raise HTTPException(status_code=404, detail="Specialist not found")
        
        slots = []
        today = date.today()
        
        # Determine start date (tomorrow)
        start_date = today + timedelta(days=1)
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # Skip weekends (0=Mon, 6=Sun)
            if current_date.weekday() >= 5:
                continue
            
            # Generate slots from 9 AM to 5 PM
            for hour in range(9, 17):
                slot_time = time(hour, 0)
                
                # Check real availability against DB
                if appointment_repo.check_availability(
                    db, specialist_id, current_date, slot_time
                ):
                    slots.append({
                        "date": current_date.isoformat(),
                        "time": slot_time.strftime("%H:%M"),
                        "available": True
                    })
        
        return slots

    def create_booking(
        self, 
        db: Session, 
        patient_id: str, 
        specialist_id: str, 
        slot_date: date, 
        slot_time: time,
        notes: str = ""
    ) -> Appointment:
        """Create a new booking request"""
        
        # 1. Verify Specialist exists
        specialist = specialist_repo.get(db, specialist_id)
        if not specialist:
            raise HTTPException(status_code=404, detail="Specialist not found")
            
        # 2. Check Availability
        if not appointment_repo.check_availability(db, specialist_id, slot_date, slot_time):
            raise HTTPException(status_code=400, detail="Slot is not available")
            
        # 3. Create Appointment (Status: PENDING)
        appointment_data = {
            "patient_id": patient_id,
            "specialist_id": specialist_id,
            "scheduled_date": slot_date,
            "scheduled_time": slot_time,
            "payment_status": "pending", # Enum value or string depending on setup (using string literal for safety if enum mapping issues)
            "fee_amount": 0.0, # Default fee
            "patient_notes": notes,
            "meeting_link": f"https://meet.mindmate.ai/{specialist_id}-{patient_id}" # Mock link
        }
        
        return appointment_repo.create(db, obj_in=appointment_data)

    def confirm_booking(
        self, db: Session, specialist_id: str, appointment_id: str
    ) -> Appointment:
        """Specialist confirms a booking"""
        appointment = appointment_repo.get(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        if appointment.specialist_id != specialist_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        return appointment_repo.update_status(db, appointment_id, AppointmentStatus.CONFIRMED)

    def reject_booking(
        self, db: Session, specialist_id: str, appointment_id: str
    ) -> Appointment:
        """Specialist rejects a booking"""
        appointment = appointment_repo.get(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        if appointment.specialist_id != specialist_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        return appointment_repo.update_status(db, appointment_id, AppointmentStatus.CANCELLED)


booking_service = BookingService()
