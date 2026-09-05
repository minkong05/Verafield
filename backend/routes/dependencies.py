import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.db.models.mill import Mill
from backend.db.models.user import User
from backend.db.session import get_db
from backend.services.auth import service as auth_service
from backend.services.mill import service as mill_service
from packages.shared_types.enums import UserRole

# auto_error=False so this module owns the 401 body and the WWW-Authenticate
# header. HTTPBearer rather than OAuth2PasswordBearer: the latter mandates a
# form-encoded login with a field named "username", and both consuming apps
# are JSON clients.
bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHENTICATED = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    detail="not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def validate_mill(mill_id: uuid.UUID, db: Session = Depends(get_db)) -> Mill:
    """Refuse an unregistered mill_id (Feature 10).

    Route-layer by design: the lookup itself lives in mill.service, and this
    only maps the domain exception to an HTTPException — the same job every
    route in this codebase already does. FastAPI caches sub-dependencies per
    request, so the Depends(get_db) here resolves to the *same* Session the
    endpoint receives: one indexed primary-key lookup, no second connection
    and no second transaction.

    Used two ways. Mill-facing routers depend on authorize_mill, which wraps
    it. Admin-only mill-scoped routers pair it with require_admin instead:
    require_admin settles who the caller is but never looks at the path, so
    without this a bogus mill_id would reach the service layer and surface as
    a foreign-key error rather than a 404."""
    try:
        return mill_service.get_mill(db, mill_id)
    except mill_service.MillNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """The authenticated principal, re-read from the database on every
    request. A missing, malformed or expired token, an unknown user and a
    deactivated one all yield the same 401 — none of them should be
    distinguishable to an unauthenticated caller."""
    if credentials is None:
        raise _UNAUTHENTICATED
    try:
        user_id = auth_service.decode_access_token(credentials.credentials)
        user = auth_service.get_user(db, user_id)
    except (auth_service.InvalidCredentialsError, auth_service.UserNotFoundError) as exc:
        raise _UNAUTHENTICATED from exc
    if not user.is_active:
        raise _UNAUTHENTICATED
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="this action requires an admin account"
        )
    return user


def authorize_mill(
    mill_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Mill:
    """Gate every mill-scoped route: the path says which mill, the credential
    says whether this caller may act as it.

    Branch order is the security-critical part. A mill user asking about any
    mill but its own is refused from the token alone, *before* the registry is
    consulted, so a registered mill and an invented UUID are indistinguishable
    to them — that is what closes the "is this identifier registered" oracle
    docs/roadmap/11-mill-authentication.md leaves open under Feature 10 alone.
    Only an admin ever sees the 404 that distinguishes the two."""
    if user.role != UserRole.ADMIN:
        if user.mill_id != mill_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="not authorised for this mill")
        mill = validate_mill(mill_id, db)
        if not mill.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="this mill is deactivated")
        return mill
    return validate_mill(mill_id, db)
