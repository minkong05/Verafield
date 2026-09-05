import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.routes.dependencies import authorize_mill
from backend.services.evidence_pack import service
from packages.shared_types import Batch as BatchSchema
from packages.shared_types import BatchCreate, EvidencePackCreate
from packages.shared_types import EvidencePack as EvidencePackSchema

router = APIRouter(
    prefix="/mills/{mill_id}/batches",
    tags=["evidence-pack"],
    dependencies=[Depends(authorize_mill)],
)


@router.post("", response_model=BatchSchema, status_code=status.HTTP_201_CREATED)
def create_batch(
    mill_id: uuid.UUID, payload: BatchCreate, db: Session = Depends(get_db)
) -> BatchSchema:
    try:
        batch = service.create_batch(db, mill_id, payload)
    except service.PlotNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BatchSchema.model_validate(batch)


@router.get("", response_model=list[BatchSchema])
def read_batches(mill_id: uuid.UUID, db: Session = Depends(get_db)) -> list[BatchSchema]:
    return [BatchSchema.model_validate(batch) for batch in service.list_batches(db, mill_id)]


@router.get("/{batch_id}", response_model=BatchSchema)
def read_batch(
    mill_id: uuid.UUID, batch_id: uuid.UUID, db: Session = Depends(get_db)
) -> BatchSchema:
    try:
        batch = service.get_batch(db, mill_id, batch_id)
    except service.BatchNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BatchSchema.model_validate(batch)


@router.post(
    "/{batch_id}/evidence-pack",
    response_model=EvidencePackSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence_pack(
    mill_id: uuid.UUID,
    batch_id: uuid.UUID,
    payload: EvidencePackCreate,
    db: Session = Depends(get_db),
) -> EvidencePackSchema:
    try:
        pack = service.generate_evidence_pack(db, mill_id, batch_id, payload)
    except service.BatchNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.HouseholdNotClearedError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    except service.EvidencePackAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return EvidencePackSchema.model_validate(pack)


@router.get("/{batch_id}/evidence-pack", response_model=EvidencePackSchema)
def read_evidence_pack(
    mill_id: uuid.UUID, batch_id: uuid.UUID, db: Session = Depends(get_db)
) -> EvidencePackSchema:
    try:
        pack = service.get_evidence_pack(db, mill_id, batch_id)
    except (service.BatchNotFoundError, service.EvidencePackNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return EvidencePackSchema.model_validate(pack)
