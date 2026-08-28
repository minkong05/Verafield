from backend.services.rules_engine.service import compute_status
from shared_types.enums import DocumentType, LandOwnershipStatus


def test_compute_status_returns_cleared_when_nothing_missing() -> None:
    required = {DocumentType.TENANCY_AGREEMENT, DocumentType.LANDLORD_IDENTITY}
    status = compute_status(required, hard_fail=set(), collected=required)

    assert status == LandOwnershipStatus.CLEARED


def test_compute_status_returns_needs_follow_up_for_missing_non_hard_fail_document() -> None:
    required = {DocumentType.TENANCY_AGREEMENT, DocumentType.LANDLORD_IDENTITY}
    hard_fail = {DocumentType.TENANCY_AGREEMENT}
    collected = {DocumentType.TENANCY_AGREEMENT}

    status = compute_status(required, hard_fail, collected)

    assert status == LandOwnershipStatus.NEEDS_FOLLOW_UP


def test_compute_status_returns_failed_when_missing_a_hard_fail_document() -> None:
    required = {DocumentType.TENANCY_AGREEMENT, DocumentType.LANDLORD_IDENTITY}
    hard_fail = {DocumentType.TENANCY_AGREEMENT}
    collected = {DocumentType.LANDLORD_IDENTITY}

    status = compute_status(required, hard_fail, collected)

    assert status == LandOwnershipStatus.FAILED
