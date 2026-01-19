"""
MindMate API v1 Router Configuration
=====================================
Simplified router with essential endpoints only.

Essential APIs:
- auth.py: Authentication, registration, password management
- assessment.py: Multi-agent assessment workflow
- specialists.py: Specialist management
- appointments.py: Booking workflow
- admin.py: Admin operations
- dashboard.py: User dashboard (optional)

Author: Mental Health Platform Team
Version: 3.0.0 - Simplified API
"""

from fastapi import APIRouter
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter()

# Track loaded routers
_loaded_routers: Dict[str, bool] = {}


def load_all_routers():
    """Load all essential API routers."""
    global _loaded_routers
    
    if _loaded_routers.get("all_loaded", False):
        return
    
    logger.info("Loading essential API routers...")
    
    try:
        # 1. Authentication (login, register, password)
        from .endpoints import auth_new as auth
        router.include_router(auth.router, tags=["Authentication"])
        logger.info("Loaded: auth")
        
        # 2. Assessment (multi-agent workflow)
        from .endpoints import assessment
        router.include_router(assessment.router, tags=["Assessment"])
        logger.info("Loaded: assessment")
        
        # 3. Specialists (profile, availability, matching)
        from .endpoints import specialists
        router.include_router(specialists.router, tags=["Specialists"])
        logger.info("Loaded: specialists")
        
        # 4. Appointments (booking workflow)
        # 4. Appointments (booking workflow)
        from .endpoints import booking
        router.include_router(booking.router, prefix="/appointments", tags=["Appointments"])
        logger.info("Loaded: appointments (new booking system)")
        logger.info("Loaded: appointments")
        
        # 5. Admin (platform management)
        from .endpoints import admin
        router.include_router(admin.router, tags=["Admin"])
        logger.info("Loaded: admin")
        
        # 6. Dashboard (optional - user stats)
        from .endpoints import dashboard
        router.include_router(dashboard.router, tags=["Dashboard"])
        logger.info("Loaded: dashboard")
        
        _loaded_routers["all_loaded"] = True
        logger.info("All essential routers loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading routers: {e}", exc_info=True)
        raise


# Health check endpoint
@router.get("/health")
async def health_check():
    """System health check"""
    from datetime import datetime, timezone
    
    return {
        "status": "healthy",
        "service": "mindmate-api",
        "version": "3.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": [
            "authentication",
            "assessment",
            "specialists",
            "appointments",
            "admin",
            "dashboard",
        ],
    }
