"""Administrative commands that cannot go through the API.

Currently just one: creating the first admin. POST /users requires an admin
token, so the very first account has to come from outside the request path.

Rejected alternatives: seeding from an Alembic migration (puts a credential in
version control and re-runs on every test upgrade/downgrade cycle) and a
FastAPI startup hook (implicit, and fires in every environment including CI).
A command someone has to run deliberately is the honest shape for this.
"""

import argparse
import os
import sys

from backend.db.session import SessionLocal
from backend.services.auth import service
from packages.shared_types.auth import UserCreate
from packages.shared_types.enums import UserRole

_MIN_PASSWORD_LENGTH = 12


def create_admin(email: str, password: str) -> int:
    db = SessionLocal()
    try:
        user = service.create_user(
            db,
            UserCreate(email=email, password=password, role=UserRole.ADMIN, mill_id=None),
        )
    except service.UserAlreadyExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()
    print(f"created admin {user.email} ({user.id})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m backend.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    admin = subparsers.add_parser("create-admin", help="create the first admin account")
    admin.add_argument("--email", required=True)
    admin.add_argument(
        "--password",
        default=None,
        help="defaults to $TAPAK_ADMIN_PASSWORD, so the secret need not reach the shell history",
    )

    args = parser.parse_args(argv)
    if args.command == "create-admin":
        password = args.password or os.environ.get("TAPAK_ADMIN_PASSWORD")
        if not password:
            print(
                "error: pass --password or set TAPAK_ADMIN_PASSWORD",
                file=sys.stderr,
            )
            return 2
        if len(password) < _MIN_PASSWORD_LENGTH:
            print(
                f"error: password must be at least {_MIN_PASSWORD_LENGTH} characters",
                file=sys.stderr,
            )
            return 2
        return create_admin(args.email, password)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
