import uuid

from sqlalchemy.orm import Session

from backend.db.models.labour_declaration import ConsentRecord, LabourDeclaration
from backend.services.gap_assessment.service import get_household
from packages.shared_types.labour_declaration import ConsentRecordCreate, LabourDeclarationCreate


class LabourDeclarationNotFoundError(Exception):
    """The household exists but has no labour declaration yet."""


class LabourDeclarationAlreadyExistsError(Exception):
    """A household may have at most one labour declaration for MVP."""


class ConsentRecordNotFoundError(Exception):
    """The household exists but has no consent record yet."""


class ConsentRecordAlreadyExistsError(Exception):
    """A household may have at most one consent record for MVP."""


def create_labour_declaration(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, payload: LabourDeclarationCreate
) -> LabourDeclaration:
    household = get_household(db, mill_id, household_id)

    existing = (
        db.query(LabourDeclaration)
        .filter(
            LabourDeclaration.household_id == household.id, LabourDeclaration.mill_id == mill_id
        )
        .one_or_none()
    )
    if existing is not None:
        raise LabourDeclarationAlreadyExistsError(
            f"labour declaration already exists for household {household_id}"
        )

    declaration = LabourDeclaration(
        mill_id=mill_id,
        household_id=household.id,
        labour_arrangement_description=payload.labour_arrangement_description,
        no_child_labour_confirmed=payload.no_child_labour_confirmed,
        has_land_dispute=payload.has_land_dispute,
        land_dispute_notes=payload.land_dispute_notes,
        signature_method=payload.signature_method,
        collected_by=payload.collected_by,
        collected_at=payload.collected_at,
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)
    return declaration


def get_labour_declaration(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> LabourDeclaration:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    declaration = (
        db.query(LabourDeclaration)
        .filter(
            LabourDeclaration.household_id == household_id, LabourDeclaration.mill_id == mill_id
        )
        .one_or_none()
    )
    if declaration is None:
        raise LabourDeclarationNotFoundError(
            f"no labour declaration yet for household {household_id}"
        )
    return declaration


def create_consent_record(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, payload: ConsentRecordCreate
) -> ConsentRecord:
    household = get_household(db, mill_id, household_id)

    existing = (
        db.query(ConsentRecord)
        .filter(ConsentRecord.household_id == household.id, ConsentRecord.mill_id == mill_id)
        .one_or_none()
    )
    if existing is not None:
        raise ConsentRecordAlreadyExistsError(
            f"consent record already exists for household {household_id}"
        )

    consent = ConsentRecord(
        mill_id=mill_id,
        household_id=household.id,
        mykad_last4=payload.mykad_last4,
        credit_referral_consent_given=payload.credit_referral_consent_given,
        signature_method=payload.signature_method,
        collected_by=payload.collected_by,
        collected_at=payload.collected_at,
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


def get_consent_record(db: Session, mill_id: uuid.UUID, household_id: uuid.UUID) -> ConsentRecord:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    consent = (
        db.query(ConsentRecord)
        .filter(ConsentRecord.household_id == household_id, ConsentRecord.mill_id == mill_id)
        .one_or_none()
    )
    if consent is None:
        raise ConsentRecordNotFoundError(f"no consent record yet for household {household_id}")
    return consent
