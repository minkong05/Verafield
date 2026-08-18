import math
import uuid
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.db.models.plot import Plot
from backend.db.models.verification_engine import (
    DeforestationCheck,
    FieldVerificationCheck,
    YieldLicenceCheck,
)
from backend.services.gap_assessment.service import get_household
from shared_types.enums import DeforestationStatus, FieldVerificationStatus
from shared_types.plot import PlotCreate
from shared_types.verification_engine import (
    DeforestationCheckCreate,
    FieldVerificationCheckCreate,
    YieldLicenceCheckCreate,
)

_MIN_FOREST_AREA_HA = Decimal("0.5")
_MIN_TREE_HEIGHT_M = Decimal("5")
_MIN_CANOPY_COVER_PCT = Decimal("10")

_MAX_CHECKIN_DISTANCE_M = Decimal("100")
_MAX_CHECKIN_TIME_DELTA = timedelta(minutes=60)
_MAX_PHOTO_DISTANCE_M = Decimal("50")
_MAX_AREA_VARIANCE_PCT = Decimal("0.15")
_MIN_LICENCE_COVERAGE_PCT = Decimal("0.95")
_MAX_YIELD_BENCHMARK_MULTIPLE = Decimal("1.5")
_EARTH_RADIUS_M = 6_371_000


class PlotNotFoundError(Exception):
    """The household exists but has no plot with this id."""


class DeforestationCheckNotFoundError(Exception):
    """The plot exists but has no deforestation check yet."""


class DeforestationCheckAlreadyExistsError(Exception):
    """A plot may have at most one deforestation check for MVP."""


class FieldVerificationCheckNotFoundError(Exception):
    """The plot exists but has no field verification check yet."""


class FieldVerificationCheckAlreadyExistsError(Exception):
    """A plot may have at most one field verification check for MVP."""


class YieldLicenceCheckNotFoundError(Exception):
    """The household exists but has no yield/licence check yet."""


class YieldLicenceCheckAlreadyExistsError(Exception):
    """A household may have at most one yield/licence check for MVP."""


def create_plot(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, payload: PlotCreate
) -> Plot:
    household = get_household(db, mill_id, household_id)
    plot = Plot(
        mill_id=mill_id,
        household_id=household.id,
        polygon=payload.polygon,
        centroid_lat=payload.centroid_lat,
        centroid_lon=payload.centroid_lon,
        area_ha=payload.area_ha,
        collected_by=payload.collected_by,
        collected_at=payload.collected_at,
    )
    db.add(plot)
    db.commit()
    db.refresh(plot)
    return plot


def list_plots(db: Session, mill_id: uuid.UUID, household_id: uuid.UUID) -> list[Plot]:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    return (
        db.query(Plot)
        .filter(Plot.household_id == household_id, Plot.mill_id == mill_id)
        .order_by(Plot.created_at)
        .all()
    )


def get_plot(db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, plot_id: uuid.UUID) -> Plot:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    plot = (
        db.query(Plot)
        .filter(Plot.id == plot_id, Plot.household_id == household_id, Plot.mill_id == mill_id)
        .one_or_none()
    )
    if plot is None:
        raise PlotNotFoundError(f"plot {plot_id} not found for household {household_id}")
    return plot


def compute_status(
    forest_area_ha: Decimal,
    tree_height_m: Decimal,
    canopy_cover_pct: Decimal,
    predominantly_agricultural_or_urban: bool,
    forest_loss_detected: bool,
    review_inconclusive: bool,
) -> DeforestationStatus:
    if review_inconclusive:
        return DeforestationStatus.NEEDS_REVIEW

    is_forest = (
        forest_area_ha > _MIN_FOREST_AREA_HA
        and tree_height_m > _MIN_TREE_HEIGHT_M
        and canopy_cover_pct > _MIN_CANOPY_COVER_PCT
        and not predominantly_agricultural_or_urban
    )
    if not is_forest:
        return DeforestationStatus.COMPLIANT
    if forest_loss_detected:
        return DeforestationStatus.NON_COMPLIANT
    return DeforestationStatus.COMPLIANT


def create_deforestation_check(
    db: Session,
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    plot_id: uuid.UUID,
    payload: DeforestationCheckCreate,
) -> DeforestationCheck:
    plot = get_plot(db, mill_id, household_id, plot_id)

    existing = (
        db.query(DeforestationCheck)
        .filter(DeforestationCheck.plot_id == plot.id, DeforestationCheck.mill_id == mill_id)
        .one_or_none()
    )
    if existing is not None:
        raise DeforestationCheckAlreadyExistsError(
            f"deforestation check already exists for plot {plot_id}"
        )

    status = compute_status(
        payload.forest_area_ha,
        payload.tree_height_m,
        payload.canopy_cover_pct,
        payload.predominantly_agricultural_or_urban,
        payload.forest_loss_detected,
        payload.review_inconclusive,
    )
    check = DeforestationCheck(
        mill_id=mill_id,
        plot_id=plot.id,
        forest_area_ha=payload.forest_area_ha,
        tree_height_m=payload.tree_height_m,
        canopy_cover_pct=payload.canopy_cover_pct,
        predominantly_agricultural_or_urban=payload.predominantly_agricultural_or_urban,
        pre_2020_imagery_date=payload.pre_2020_imagery_date,
        post_2020_imagery_date=payload.post_2020_imagery_date,
        forest_loss_detected=payload.forest_loss_detected,
        review_inconclusive=payload.review_inconclusive,
        reviewed_by=payload.reviewed_by,
        status=status,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


def get_deforestation_check(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, plot_id: uuid.UUID
) -> DeforestationCheck:
    get_plot(db, mill_id, household_id, plot_id)  # 404s through the household+plot chain
    check = (
        db.query(DeforestationCheck)
        .filter(DeforestationCheck.plot_id == plot_id, DeforestationCheck.mill_id == mill_id)
        .one_or_none()
    )
    if check is None:
        raise DeforestationCheckNotFoundError(f"no deforestation check yet for plot {plot_id}")
    return check


def _haversine_distance_m(lat1: Decimal, lon1: Decimal, lat2: Decimal, lon2: Decimal) -> Decimal:
    # Derived distance, not a legal-threshold literal (unlike the Decimal
    # columns it's computed from) — float internally for math.sin/cos/asin,
    # Decimal in/out so callers compare it against a Decimal threshold.
    phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
    d_phi = math.radians(float(lat2) - float(lat1))
    d_lambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return Decimal(2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a)))


def compute_field_verification_status(
    checkin_mismatch: bool, photo_mismatch: bool, area_mismatch: bool
) -> FieldVerificationStatus:
    if checkin_mismatch or photo_mismatch or area_mismatch:
        return FieldVerificationStatus.NEEDS_REVIEW
    return FieldVerificationStatus.CLEARED


def compute_yield_licence_status(
    licence_mismatch: bool, yield_mismatch: bool
) -> FieldVerificationStatus:
    if licence_mismatch or yield_mismatch:
        return FieldVerificationStatus.NEEDS_REVIEW
    return FieldVerificationStatus.CLEARED


def create_field_verification_check(
    db: Session,
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    plot_id: uuid.UUID,
    payload: FieldVerificationCheckCreate,
) -> FieldVerificationCheck:
    plot = get_plot(db, mill_id, household_id, plot_id)

    existing = (
        db.query(FieldVerificationCheck)
        .filter(
            FieldVerificationCheck.plot_id == plot.id, FieldVerificationCheck.mill_id == mill_id
        )
        .one_or_none()
    )
    if existing is not None:
        raise FieldVerificationCheckAlreadyExistsError(
            f"field verification check already exists for plot {plot_id}"
        )

    checkin_distance = _haversine_distance_m(
        payload.gnss_checkin_lat, payload.gnss_checkin_lon, plot.centroid_lat, plot.centroid_lon
    )
    checkin_mismatch = (
        checkin_distance > _MAX_CHECKIN_DISTANCE_M
        or abs(payload.gnss_checkin_at - plot.collected_at) > _MAX_CHECKIN_TIME_DELTA
    )

    photo_distance = _haversine_distance_m(
        payload.photo_lat, payload.photo_lon, plot.centroid_lat, plot.centroid_lon
    )
    photo_mismatch = photo_distance > _MAX_PHOTO_DISTANCE_M

    area_variance = abs(plot.area_ha - payload.title_area_ha) / payload.title_area_ha
    area_mismatch = area_variance > _MAX_AREA_VARIANCE_PCT

    status = compute_field_verification_status(checkin_mismatch, photo_mismatch, area_mismatch)

    check = FieldVerificationCheck(
        mill_id=mill_id,
        plot_id=plot.id,
        gnss_checkin_lat=payload.gnss_checkin_lat,
        gnss_checkin_lon=payload.gnss_checkin_lon,
        gnss_checkin_at=payload.gnss_checkin_at,
        photo_lat=payload.photo_lat,
        photo_lon=payload.photo_lon,
        photo_taken_at=payload.photo_taken_at,
        title_area_ha=payload.title_area_ha,
        checkin_mismatch=checkin_mismatch,
        photo_mismatch=photo_mismatch,
        area_mismatch=area_mismatch,
        status=status,
        recorded_by=payload.recorded_by,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


def get_field_verification_check(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, plot_id: uuid.UUID
) -> FieldVerificationCheck:
    get_plot(db, mill_id, household_id, plot_id)  # 404s through the household+plot chain
    check = (
        db.query(FieldVerificationCheck)
        .filter(
            FieldVerificationCheck.plot_id == plot_id, FieldVerificationCheck.mill_id == mill_id
        )
        .one_or_none()
    )
    if check is None:
        raise FieldVerificationCheckNotFoundError(
            f"no field verification check yet for plot {plot_id}"
        )
    return check


def create_yield_licence_check(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, payload: YieldLicenceCheckCreate
) -> YieldLicenceCheck:
    household = get_household(db, mill_id, household_id)

    existing = (
        db.query(YieldLicenceCheck)
        .filter(
            YieldLicenceCheck.household_id == household.id, YieldLicenceCheck.mill_id == mill_id
        )
        .one_or_none()
    )
    if existing is not None:
        raise YieldLicenceCheckAlreadyExistsError(
            f"yield/licence check already exists for household {household_id}"
        )

    declared_area_ha = Decimal(
        db.query(func.coalesce(func.sum(Plot.area_ha), 0))
        .filter(Plot.household_id == household.id, Plot.mill_id == mill_id)
        .scalar()
    )

    licence_mismatch = (
        declared_area_ha > 0
        and payload.mpob_licensed_area_ha < declared_area_ha * _MIN_LICENCE_COVERAGE_PCT
    )
    yield_per_ha = (
        payload.annual_output_kg / declared_area_ha if declared_area_ha > 0 else Decimal(0)
    )
    yield_mismatch = (
        yield_per_ha > payload.regional_yield_benchmark_kg_per_ha * _MAX_YIELD_BENCHMARK_MULTIPLE
    )

    status = compute_yield_licence_status(licence_mismatch, yield_mismatch)

    check = YieldLicenceCheck(
        mill_id=mill_id,
        household_id=household.id,
        mpob_licensed_area_ha=payload.mpob_licensed_area_ha,
        declared_area_ha=declared_area_ha,
        annual_output_kg=payload.annual_output_kg,
        regional_yield_benchmark_kg_per_ha=payload.regional_yield_benchmark_kg_per_ha,
        licence_mismatch=licence_mismatch,
        yield_mismatch=yield_mismatch,
        status=status,
        recorded_by=payload.recorded_by,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


def get_yield_licence_check(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> YieldLicenceCheck:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    check = (
        db.query(YieldLicenceCheck)
        .filter(
            YieldLicenceCheck.household_id == household_id, YieldLicenceCheck.mill_id == mill_id
        )
        .one_or_none()
    )
    if check is None:
        raise YieldLicenceCheckNotFoundError(
            f"no yield/licence check yet for household {household_id}"
        )
    return check
