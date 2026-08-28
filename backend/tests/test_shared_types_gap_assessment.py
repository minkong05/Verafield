import uuid
from datetime import UTC, datetime

from shared_types.enums import EvidenceCategory, GapStatus
from shared_types.gap_assessment import GapAssessment, GapAssessmentItem


def test_evidence_category_has_exactly_the_six_roadmap_categories() -> None:
    assert {c.value for c in EvidenceCategory} == {
        "product_quantity",
        "geolocation",
        "land_ownership",
        "deforestation_proof",
        "labour_consent",
        "documentation_pack",
    }


def test_gap_status_has_exactly_the_three_statuses() -> None:
    assert {s.value for s in GapStatus} == {"present", "missing", "needs_verification"}


def test_gap_assessment_round_trips_through_model_dump_and_validate() -> None:
    original = GapAssessment(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        assessed_by="Officer Aiman",
        assessed_at=datetime.now(UTC),
        items=[
            GapAssessmentItem(
                id=uuid.uuid4(), category=EvidenceCategory.GEOLOCATION, status=GapStatus.PRESENT
            )
        ],
    )

    restored = GapAssessment.model_validate(original.model_dump())

    assert restored == original
