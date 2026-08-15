import pytest

from backend.services.gap_assessment.service import InvalidChecklistError, validate_checklist_items
from shared_types.enums import EvidenceCategory, GapStatus
from shared_types.gap_assessment import GapAssessmentItemCreate


def _item(
    category: EvidenceCategory, status: GapStatus = GapStatus.PRESENT
) -> GapAssessmentItemCreate:
    return GapAssessmentItemCreate(category=category, status=status)


def test_validate_checklist_items_accepts_all_six_categories_once() -> None:
    items = [_item(category) for category in EvidenceCategory]

    validate_checklist_items(items)  # should not raise


def test_validate_checklist_items_rejects_missing_category() -> None:
    items = [
        _item(category)
        for category in EvidenceCategory
        if category != EvidenceCategory.LABOUR_CONSENT
    ]

    with pytest.raises(InvalidChecklistError, match="missing required evidence categories"):
        validate_checklist_items(items)


def test_validate_checklist_items_rejects_duplicate_category() -> None:
    items = [_item(category) for category in EvidenceCategory]
    items.append(_item(EvidenceCategory.PRODUCT_QUANTITY))

    with pytest.raises(InvalidChecklistError, match="duplicate evidence category"):
        validate_checklist_items(items)
