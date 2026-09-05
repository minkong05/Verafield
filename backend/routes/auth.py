from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.models.user import User as UserModel
from backend.db.session import get_db
from backend.routes.dependencies import get_current_user
from backend.services.auth import service
from packages.shared_types import LoginRequest, PasswordChangeRequest, TokenResponse
from packages.shared_types import User as UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        user = service.authenticate_user(db, payload.email, payload.password)
    except service.InvalidCredentialsError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    access_token, expires_at = service.create_access_token(user)
    return TokenResponse(access_token=access_token, expires_at=expires_at)


@router.get("/me", response_model=UserSchema)
def read_current_user(user: UserModel = Depends(get_current_user)) -> UserSchema:
    return UserSchema.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChangeRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        service.change_password(db, user, payload.current_password, payload.new_password)
    except service.InvalidCredentialsError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
