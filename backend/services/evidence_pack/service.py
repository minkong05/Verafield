import uuid
from datetime import date

from sqlalchemy.orm import Session

from backend.db.models.evidence_pack import Batch, BatchPlot, EvidencePack
from backend.db.models.household import Household
from backend.db.models.rules_engine import LandOwnershipAssessment
from backend.db.models.verification_engine import DeforestationCheck
from backend.services.verification_engine.service import (
    PlotNotFoundError,
    get_plot_by_id,
    household_is_cleared,
)
from shared_types.enums import NoMixingStatus
from shared_types.evidence_pack import (
    BatchCreate,
    EvidencePackAssembly,
    EvidencePackCreate,
    EvidencePackDeforestationEvidence,
    EvidencePackLegalityEvidence,
    EvidencePackPlotGeolocation,
    EvidencePackSupplier,
)

__all__ = [
    "BatchNotFoundError",
    "EvidencePackAlreadyExistsError",
    "EvidencePackNotFoundError",
    "HouseholdNotClearedError",
    "PlotNotFoundError",
    "compute_no_mixing_status",
    "create_batch",
    "generate_evidence_pack",
    "get_batch",
    "get_evidence_pack",
    "list_batches",
]

# MVP scope is Sabah/Sarawak (Malaysia) only — a single-value column would
# never hold anything else, so this is a constant, not a stored field.
_COUNTRY_OF_PRODUCTION = "Malaysia"


class BatchNotFoundError(Exception):
    """No batch exists for the given (mill_id, batch_id) pair."""


class EvidencePackNotFoundError(Exception):
    """The batch exists but has no evidence pack yet."""


class EvidencePackAlreadyExistsError(Exception):
    """A batch may have at most one evidence pack for MVP."""


class HouseholdNotClearedError(Exception):
    """One or more households referenced by this batch have an unresolved
    Feature 05 flag or missing Feature 02 legality clearance."""


def compute_no_mixing_status(plot_ids: list[uuid.UUID]) -> NoMixingStatus:
    if len(set(plot_ids)) <= 1:
        return NoMixingStatus.SINGLE_SOURCE
    return NoMixingStatus.MIXED_SOURCES


def create_batch(db: Session, mill_id: uuid.UUID, payload: BatchCreate) -> Batch:
    plots = [get_plot_by_id(db, mill_id, item.plot_id) for item in payload.plots]
    no_mixing_status = compute_no_mixing_status([plot.id for plot in plots])

    batch = Batch(
        mill_id=mill_id,
        product_description=payload.product_description,
        trade_name=payload.trade_name,
        hs_code=payload.hs_code,
        net_mass_kg=payload.net_mass_kg,
        recipient_name=payload.recipient_name,
        recipient_postal_address=payload.recipient_postal_address,
        recipient_email=payload.recipient_email,
        no_mixing_status=no_mixing_status,
        created_by=payload.created_by,
    )
    batch.plots = [
        BatchPlot(mill_id=mill_id, plot_id=plot.id, harvest_date=item.harvest_date)
        for plot, item in zip(plots, payload.plots, strict=True)
    ]
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def list_batches(db: Session, mill_id: uuid.UUID) -> list[Batch]:
    return db.query(Batch).filter(Batch.mill_id == mill_id).order_by(Batch.created_at).all()


def get_batch(db: Session, mill_id: uuid.UUID, batch_id: uuid.UUID) -> Batch:
    batch = db.query(Batch).filter(Batch.id == batch_id, Batch.mill_id == mill_id).one_or_none()
    if batch is None:
        raise BatchNotFoundError(f"batch {batch_id} not found for mill {mill_id}")
    return batch


def _assemble_annex_ii_data(db: Session, mill_id: uuid.UUID, batch: Batch) -> dict:
    # Callers must already have passed household_is_cleared for every
    # household below (see generate_evidence_pack), so every dict lookup
    # here is guaranteed to hit — the gate is what makes this assembly safe
    # to write without additional None-checks.
    plots = [bp.plot for bp in batch.plots]
    household_ids = sorted({plot.household_id for plot in plots}, key=str)

    households = {
        h.id: h
        for h in db.query(Household)
        .filter(Household.id.in_(household_ids), Household.mill_id == mill_id)
        .all()
    }
    land_ownership_by_household = {
        loa.household_id: loa
        for loa in db.query(LandOwnershipAssessment)
        .filter(
            LandOwnershipAssessment.household_id.in_(household_ids),
            LandOwnershipAssessment.mill_id == mill_id,
        )
        .all()
    }
    deforestation_by_plot = {
        dc.plot_id: dc
        for dc in db.query(DeforestationCheck)
        .filter(
            DeforestationCheck.plot_id.in_([p.id for p in plots]),
            DeforestationCheck.mill_id == mill_id,
        )
        .all()
    }

    harvest_dates: list[date] = [bp.harvest_date for bp in batch.plots]

    assembly = EvidencePackAssembly(
        product_description=batch.product_description,
        trade_name=batch.trade_name,
        hs_code=batch.hs_code,
        net_mass_kg=batch.net_mass_kg,
        country_of_production=_COUNTRY_OF_PRODUCTION,
        plots=[
            EvidencePackPlotGeolocation(
                plot_id=bp.plot_id,
                household_id=bp.plot.household_id,
                centroid_lat=bp.plot.centroid_lat,
                centroid_lon=bp.plot.centroid_lon,
                area_ha=bp.plot.area_ha,
                harvest_date=bp.harvest_date,
            )
            for bp in batch.plots
        ],
        production_date_start=min(harvest_dates),
        production_date_end=max(harvest_dates),
        suppliers=[
            EvidencePackSupplier(
                household_id=households[hid].id,
                name=households[hid].name,
                postal_address=households[hid].postal_address,
                email=households[hid].email,
                district=households[hid].district,
                state=land_ownership_by_household[hid].state,
            )
            for hid in household_ids
        ],
        recipient_name=batch.recipient_name,
        recipient_postal_address=batch.recipient_postal_address,
        recipient_email=batch.recipient_email,
        deforestation_evidence=[
            EvidencePackDeforestationEvidence(
                plot_id=plot.id,
                status=deforestation_by_plot[plot.id].status,
                reviewed_by=deforestation_by_plot[plot.id].reviewed_by,
                reviewed_at=deforestation_by_plot[plot.id].reviewed_at,
            )
            for plot in plots
        ],
        legality_evidence=[
            EvidencePackLegalityEvidence(
                household_id=hid,
                land_type=land_ownership_by_household[hid].land_type,
                rule_version=land_ownership_by_household[hid].rule_version,
                status=land_ownership_by_household[hid].status,
                documents_collected=land_ownership_by_household[hid].documents_collected,
            )
            for hid in household_ids
        ],
        no_mixing_status=batch.no_mixing_status,
    )
    return assembly.model_dump(mode="json")


def _build_geojson(batch: Batch) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [bp.plot.polygon]},
                "properties": {
                    "plot_id": str(bp.plot_id),
                    "household_id": str(bp.plot.household_id),
                    "area_ha": str(bp.plot.area_ha),
                    "harvest_date": bp.harvest_date.isoformat(),
                },
            }
            for bp in batch.plots
        ],
    }


def generate_evidence_pack(
    db: Session, mill_id: uuid.UUID, batch_id: uuid.UUID, payload: EvidencePackCreate
) -> EvidencePack:
    batch = get_batch(db, mill_id, batch_id)

    existing = (
        db.query(EvidencePack)
        .filter(EvidencePack.batch_id == batch.id, EvidencePack.mill_id == mill_id)
        .one_or_none()
    )
    if existing is not None:
        raise EvidencePackAlreadyExistsError(f"evidence pack already exists for batch {batch_id}")

    household_ids = sorted({bp.plot.household_id for bp in batch.plots}, key=str)
    uncleared = [hid for hid in household_ids if not household_is_cleared(db, mill_id, hid)]
    if uncleared:
        raise HouseholdNotClearedError(
            f"households not cleared for evidence pack generation: {[str(h) for h in uncleared]}"
        )

    pack = EvidencePack(
        mill_id=mill_id,
        batch_id=batch.id,
        assembled_data=_assemble_annex_ii_data(db, mill_id, batch),
        geojson=_build_geojson(batch),
        generated_by=payload.generated_by,
    )
    db.add(pack)
    db.commit()
    db.refresh(pack)
    return pack


def get_evidence_pack(db: Session, mill_id: uuid.UUID, batch_id: uuid.UUID) -> EvidencePack:
    get_batch(db, mill_id, batch_id)  # 404s if this batch isn't this mill's
    pack = (
        db.query(EvidencePack)
        .filter(EvidencePack.batch_id == batch_id, EvidencePack.mill_id == mill_id)
        .one_or_none()
    )
    if pack is None:
        raise EvidencePackNotFoundError(f"no evidence pack yet for batch {batch_id}")
    return pack
