import uuid
from typing import Any, Optional, List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1 import deps
from app.models.patient import Patient
from app.models.specialist import Specialist
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientSpecialistView, AssessmentSessionResponse
from app.services.patient_service import PatientService
from app.models.enums import USERTYPE

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_in: PatientCreate,
) -> Any:
    """Create new patient (Public - Registration)."""
    return PatientService.create_patient(db=db, patient_in=patient_in)


@router.get("/me", response_model=PatientResponse)
def get_my_profile(
    *,
    db: Session = Depends(deps.get_db),
    current_patient: Patient = Depends(deps.get_current_patient),
) -> Any:
    """Get the currently authenticated patient's own full profile."""
    return current_patient


@router.get("/my-patients", response_model=List[PatientSpecialistView])
def get_my_patients(
    *,
    db: Session = Depends(deps.get_db),
    current_specialist: Specialist = Depends(deps.get_current_specialist),
) -> Any:
    """
    Get all patients associated with the currently authenticated specialist.
    Only returns patients who have at least one appointment with this specialist.
    Returns limited PatientSpecialistView (no email, phone, date of birth).
    """
    return PatientService.get_patients_by_specialist(db=db, specialist_id=current_specialist.id)


@router.get("/{id}")
def get_patient(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    payload: dict = Depends(deps.get_current_user_payload),
) -> Any:
    """
    Get patient by ID.
    - Patient themselves → full PatientResponse
    - Admin → full PatientResponse
    - Associated Specialist → limited PatientSpecialistView (must have appointment with this patient)
    - Unassociated Specialist or anyone else → 403
    """
    user_type = payload.get("user_type")
    user_id   = payload.get("user_id")

    patient = PatientService.get_patient(db=db, patient_id=id)

    if user_type == USERTYPE.PATIENT.value:
        # Patients can only see their own profile
        if str(user_id) != str(id):
            raise HTTPException(status_code=403, detail="Not authorized to view this patient's profile.")
        return PatientResponse.model_validate(patient)

    elif user_type == USERTYPE.ADMIN.value:
        # Admins can see full profile
        return PatientResponse.model_validate(patient)

    elif user_type == USERTYPE.SPECIALIST.value:
        # Specialist must have an appointment with this patient
        specialist_id = uuid.UUID(user_id)
        is_linked = PatientService.is_patient_associated_with_specialist(
            db=db, patient_id=id, specialist_id=specialist_id
        )
        if not is_linked:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this patient's profile. No appointment association found."
            )
        return PatientSpecialistView.model_validate(patient)

    else:
        raise HTTPException(status_code=403, detail="Not authorized.")


@router.patch("/{id}", response_model=PatientResponse)
def update_patient(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    patient_in: PatientUpdate,
    current_patient: Patient = Depends(deps.get_current_patient),
) -> Any:
    """Update a patient's profile. Only the patient themselves can update."""
    if current_patient.id != id:
        raise HTTPException(status_code=403, detail="Not authorized to update this patient's profile.")
    return PatientService.update_patient(db=db, patient_id=id, patient_in=patient_in)


@router.get("/", response_model=List[PatientResponse])
def get_patients(
    db: Session = Depends(deps.get_db),
    current_admin = Depends(deps.get_current_superadmin),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve all patients. SuperAdmin only."""
    return PatientService.list_patients(db=db, skip=skip, limit=limit)


@router.get("/me/assessments", response_model=List[AssessmentSessionResponse])
def get_my_assessments(
    *,
    db: Session = Depends(deps.get_db),
    current_patient: Patient = Depends(deps.get_current_patient),
    page: int = 1,
    page_size: int = 10,
    is_completed: Optional[bool] = None
) -> Any:
    """Get current patient's assessment history."""
    results, _ = PatientService.list_assessments(
        db=db,
        patient_id=current_patient.id,
        page=page,
        page_size=page_size,
        is_completed=is_completed
    )
    return results
