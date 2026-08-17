import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.db.models.plot import Plot
from backend.db.models.verification_engine import DeforestationCheck
from backend.services.gap_assessment.service import get_household
from shared_types.enums import DeforestationStatus
from shared_types.plot import PlotCreate
from shared_types.verification_engine import DeforestationCheckCreate

_MIN_FOREST_AREA_HA = Decimal("0.5")
_MIN_TREE_HEIGHT_M = Decimal("5")
_MIN_CANOPY_COVER_PCT = Decimal("10")


class PlotNotFoundError(Exception):
    """The household exists but has no plot with this id."""


class DeforestationCheckNotFoundError(Exception):
    """The plot exists but has no deforestation check yet."""


class DeforestationCheckAlreadyExistsError(Exception):
    """A plot may have at most one deforestation check for MVP."""


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
