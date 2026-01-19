"""
Repositories (New)
==================
Data access layer for MindMate v2 models.
"""

from .user import user_repo
from .patient import patient_repo
from .specialist import specialist_repo, document_repo
from .assessment import assessment_repo
from .appointment import appointment_repo

__all__ = [
    "user_repo",
    "patient_repo",
    "specialist_repo",
    "document_repo",
    "assessment_repo",
    "appointment_repo",
]
