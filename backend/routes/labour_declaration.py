import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.routes.dependencies import require_admin, validate_mill
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.labour_declaration import service
from packages.shared_types import ConsentRecord as ConsentRecordSchema
from packages.shared_types import ConsentRecordCreate, LabourDeclarationCreate
from packages.shared_types import LabourDeclaration as LabourDeclarationSchema

router = APIRouter(
    prefix="/mills/{mill_id}/households/{household_id}",
    tags=["labour-declaration"],
    dependencies=[Depends(require_admin), Depends(validate_mill)],
)


@router.post(
    "/labour-declaration",
    response_model=LabourDeclarationSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_labour_declaration(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    payload: LabourDeclarationCreate,
    db: Session = Depends(get_db),
) -> LabourDeclarationSchema:
    try:
        declaration = service.create_labour_declaration(db, mill_id, household_id, payload)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.LabourDeclarationAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return LabourDeclarationSchema.model_validate(declaration)


@router.get("/labour-declaration", response_model=LabourDeclarationSchema)
def read_labour_declaration(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> LabourDeclarationSchema:
    try:
        declaration = service.get_labour_declaration(db, mill_id, household_id)
    except (HouseholdNotFoundError, service.LabourDeclarationNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LabourDeclarationSchema.model_validate(declaration)


@router.post("/consent", response_model=ConsentRecordSchema, status_code=status.HTTP_201_CREATED)
def create_consent_record(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    payload: ConsentRecordCreate,
    db: Session = Depends(get_db),
) -> ConsentRecordSchema:
    try:
        consent = service.create_consent_record(db, mill_id, household_id, payload)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.ConsentRecordAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ConsentRecordSchema.model_validate(consent)


@router.get("/consent", response_model=ConsentRecordSchema)
def read_consent_record(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> ConsentRecordSchema:
    try:
        consent = service.get_consent_record(db, mill_id, household_id)
    except (HouseholdNotFoundError, service.ConsentRecordNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ConsentRecordSchema.model_validate(consent)
