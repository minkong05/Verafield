import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.verification_engine import service
from shared_types import DeforestationCheck as DeforestationCheckSchema
from shared_types import (
    DeforestationCheckCreate,
    FieldVerificationCheckCreate,
    PlotCreate,
    YieldLicenceCheckCreate,
)
from shared_types import FieldVerificationCheck as FieldVerificationCheckSchema
from shared_types import Plot as PlotSchema
from shared_types import YieldLicenceCheck as YieldLicenceCheckSchema

router = APIRouter(
    prefix="/mills/{mill_id}/households/{household_id}", tags=["verification-engine"]
)


@router.post("/plots", response_model=PlotSchema, status_code=status.HTTP_201_CREATED)
def create_plot(
    mill_id: uuid.UUID, household_id: uuid.UUID, payload: PlotCreate, db: Session = Depends(get_db)
) -> PlotSchema:
    try:
        plot = service.create_plot(db, mill_id, household_id, payload)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PlotSchema.model_validate(plot)


@router.get("/plots", response_model=list[PlotSchema])
def read_plots(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[PlotSchema]:
    try:
        plots = service.list_plots(db, mill_id, household_id)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [PlotSchema.model_validate(plot) for plot in plots]


@router.get("/plots/{plot_id}", response_model=PlotSchema)
def read_plot(
    mill_id: uuid.UUID, household_id: uuid.UUID, plot_id: uuid.UUID, db: Session = Depends(get_db)
) -> PlotSchema:
    try:
        plot = service.get_plot(db, mill_id, household_id, plot_id)
    except (HouseholdNotFoundError, service.PlotNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PlotSchema.model_validate(plot)


@router.post(
    "/plots/{plot_id}/deforestation-check",
    response_model=DeforestationCheckSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_deforestation_check(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    plot_id: uuid.UUID,
    payload: DeforestationCheckCreate,
    db: Session = Depends(get_db),
) -> DeforestationCheckSchema:
    try:
        check = service.create_deforestation_check(db, mill_id, household_id, plot_id, payload)
    except (HouseholdNotFoundError, service.PlotNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.DeforestationCheckAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return DeforestationCheckSchema.model_validate(check)


@router.get("/plots/{plot_id}/deforestation-check", response_model=DeforestationCheckSchema)
def read_deforestation_check(
    mill_id: uuid.UUID, household_id: uuid.UUID, plot_id: uuid.UUID, db: Session = Depends(get_db)
) -> DeforestationCheckSchema:
    try:
        check = service.get_deforestation_check(db, mill_id, household_id, plot_id)
    except (
        HouseholdNotFoundError,
        service.PlotNotFoundError,
        service.DeforestationCheckNotFoundError,
    ) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DeforestationCheckSchema.model_validate(check)


@router.post(
    "/plots/{plot_id}/field-verification-check",
    response_model=FieldVerificationCheckSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_field_verification_check(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    plot_id: uuid.UUID,
    payload: FieldVerificationCheckCreate,
    db: Session = Depends(get_db),
) -> FieldVerificationCheckSchema:
    try:
        check = service.create_field_verification_check(db, mill_id, household_id, plot_id, payload)
    except (HouseholdNotFoundError, service.PlotNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.FieldVerificationCheckAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return FieldVerificationCheckSchema.model_validate(check)


@router.get(
    "/plots/{plot_id}/field-verification-check", response_model=FieldVerificationCheckSchema
)
def read_field_verification_check(
    mill_id: uuid.UUID, household_id: uuid.UUID, plot_id: uuid.UUID, db: Session = Depends(get_db)
) -> FieldVerificationCheckSchema:
    try:
        check = service.get_field_verification_check(db, mill_id, household_id, plot_id)
    except (
        HouseholdNotFoundError,
        service.PlotNotFoundError,
        service.FieldVerificationCheckNotFoundError,
    ) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FieldVerificationCheckSchema.model_validate(check)


@router.post(
    "/yield-licence-check",
    response_model=YieldLicenceCheckSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_yield_licence_check(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    payload: YieldLicenceCheckCreate,
    db: Session = Depends(get_db),
) -> YieldLicenceCheckSchema:
    try:
        check = service.create_yield_licence_check(db, mill_id, household_id, payload)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.YieldLicenceCheckAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return YieldLicenceCheckSchema.model_validate(check)


@router.get("/yield-licence-check", response_model=YieldLicenceCheckSchema)
def read_yield_licence_check(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> YieldLicenceCheckSchema:
    try:
        check = service.get_yield_licence_check(db, mill_id, household_id)
    except (HouseholdNotFoundError, service.YieldLicenceCheckNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return YieldLicenceCheckSchema.model_validate(check)
