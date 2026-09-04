import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.routes.dependencies import require_admin
from backend.services.auth import service
from backend.services.mill import service as mill_service
from packages.shared_types import User as UserSchema
from packages.shared_types import UserCreate, UserUpdate

# Admin-only in full: creating, listing and revoking accounts is the
# compliance analyst's onboarding step, not something a mill does for itself.
router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserSchema:
    if payload.mill_id is not None:
        try:
            mill_service.get_mill(db, payload.mill_id)
        except mill_service.MillNotFoundError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    try:
        user = service.create_user(db, payload)
    except service.InvalidRoleAssignmentError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    except service.UserAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserSchema.model_validate(user)


@router.get("", response_model=list[UserSchema])
def list_users(mill_id: uuid.UUID | None = None, db: Session = Depends(get_db)) -> list[UserSchema]:
    return [UserSchema.model_validate(u) for u in service.list_users(db, mill_id)]


@router.patch("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: uuid.UUID, payload: UserUpdate, db: Session = Depends(get_db)
) -> UserSchema:
    try:
        user = service.set_user_active(db, user_id, payload.is_active)
    except service.UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserSchema.model_validate(user)
