import uuid
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.db.models.national_integration import NationalSystemsLookup
from backend.db.models.plot import Plot
from backend.services.gap_assessment.service import get_household
from packages.shared_types.enums import FieldVerificationStatus
from packages.shared_types.national_integration import NationalSystemsLookupCreate

_MAX_VOLUME_YIELD_BENCHMARK_MULTIPLE = Decimal("1.5")


class NationalSystemsLookupNotFoundError(Exception):
    """The household exists but has no national systems lookup yet."""


class NationalSystemsLookupAlreadyExistsError(Exception):
    """A household may have at most one national systems lookup for MVP."""


def compute_status(volume_yield_mismatch: bool) -> FieldVerificationStatus:
    if volume_yield_mismatch:
        return FieldVerificationStatus.NEEDS_REVIEW
    return FieldVerificationStatus.CLEARED


def create_national_systems_lookup(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, payload: NationalSystemsLookupCreate
) -> NationalSystemsLookup:
    household = get_household(db, mill_id, household_id)

    existing = (
        db.query(NationalSystemsLookup)
        .filter(
            NationalSystemsLookup.household_id == household.id,
            NationalSystemsLookup.mill_id == mill_id,
        )
        .one_or_none()
    )
    if existing is not None:
        raise NationalSystemsLookupAlreadyExistsError(
            f"national systems lookup already exists for household {household_id}"
        )

    declared_area_ha = Decimal(
        db.query(func.coalesce(func.sum(Plot.area_ha), 0))
        .filter(Plot.household_id == household.id, Plot.mill_id == mill_id)
        .scalar()
    )

    volume_per_ha = (
        payload.sims_transaction_volume_kg / declared_area_ha
        if declared_area_ha > 0
        else Decimal(0)
    )
    volume_yield_mismatch = (
        declared_area_ha > 0
        and volume_per_ha
        > payload.regional_yield_benchmark_kg_per_ha * _MAX_VOLUME_YIELD_BENCHMARK_MULTIPLE
    )

    status = compute_status(volume_yield_mismatch)

    lookup = NationalSystemsLookup(
        mill_id=mill_id,
        household_id=household.id,
        mpob_licence_number=payload.mpob_licence_number,
        sims_transaction_volume_kg=payload.sims_transaction_volume_kg,
        declared_area_ha=declared_area_ha,
        regional_yield_benchmark_kg_per_ha=payload.regional_yield_benchmark_kg_per_ha,
        volume_yield_mismatch=volume_yield_mismatch,
        geosawit_mapping_exists=payload.geosawit_mapping_exists,
        geosawit_reference=payload.geosawit_reference,
        emspo_certification_status=payload.emspo_certification_status,
        status=status,
        looked_up_by=payload.looked_up_by,
    )
    db.add(lookup)
    db.commit()
    db.refresh(lookup)
    return lookup


def get_national_systems_lookup(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> NationalSystemsLookup:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    lookup = (
        db.query(NationalSystemsLookup)
        .filter(
            NationalSystemsLookup.household_id == household_id,
            NationalSystemsLookup.mill_id == mill_id,
        )
        .one_or_none()
    )
    if lookup is None:
        raise NationalSystemsLookupNotFoundError(
            f"no national systems lookup yet for household {household_id}"
        )
    return lookup
