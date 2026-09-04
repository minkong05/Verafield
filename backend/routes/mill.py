from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.models.mill import Mill as MillModel
from backend.db.models.user import User as UserModel
from backend.db.session import get_db
from backend.routes.dependencies import authorize_mill, get_current_user, require_admin
from backend.services.mill import service
from packages.shared_types import Mill as MillSchema
from packages.shared_types import MillCreate, MillUpdate
from packages.shared_types.enums import UserRole

router = APIRouter(prefix="/mills", tags=["mills"])

# What a mill user may change about itself. Everything else is admin-only:
# mpob_licence_number is the key Feature 08 resolves national-systems lookups
# by, and name/state are how an auditor identifies the operator on a
# five-year-old evidence pack — a tenant silently re-pointing its own
# compliance identity is exactly what this must prevent.
_MILL_SELF_EDITABLE_FIELDS = frozenset({"postal_address", "email", "district"})


@router.post(
    "",
    response_model=MillSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def register_mill(payload: MillCreate, db: Session = Depends(get_db)) -> MillSchema:
    """Onboarding is analyst-mediated, not a sign-up flow. Admin-only also
    keeps the duplicate-licence 409 from telling an outsider whether a given
    licence is already held."""
    try:
        mill = service.create_mill(db, payload)
    except service.MillAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return MillSchema.model_validate(mill)


@router.get("", response_model=list[MillSchema], dependencies=[Depends(require_admin)])
def list_mills(db: Session = Depends(get_db)) -> list[MillSchema]:
    """Admin-only, and the reason this route did not exist under Feature 10
    alone: it enumerates the entire customer base."""
    return [MillSchema.model_validate(m) for m in service.list_mills(db)]


@router.get("/{mill_id}", response_model=MillSchema)
def read_mill(mill: MillModel = Depends(authorize_mill)) -> MillSchema:
    """authorize_mill has already resolved and authorised the row, so there is
    nothing left for this body to look up."""
    return MillSchema.model_validate(mill)


@router.patch("/{mill_id}", response_model=MillSchema)
def update_mill(
    payload: MillUpdate,
    mill: MillModel = Depends(authorize_mill),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MillSchema:
    """Field-level permission is checked over every field the caller
    explicitly set, so a mill user resending its whole record is still told
    which fields it may not touch — but only non-null values are applied,
    since every Mill column is NOT NULL and an explicit null in a PATCH body
    means "leave this alone" rather than "blank this out"."""
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if user.role != UserRole.ADMIN:
        rejected = sorted(payload.model_fields_set - _MILL_SELF_EDITABLE_FIELDS)
        if rejected:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=(
                    f"a mill may not change {', '.join(rejected)}; "
                    f"editable fields are {', '.join(sorted(_MILL_SELF_EDITABLE_FIELDS))}"
                ),
            )

    try:
        updated = service.update_mill(db, mill, changes)
    except service.MillAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return MillSchema.model_validate(updated)
