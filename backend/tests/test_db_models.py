import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from backend.db.models.gap_assessment import GapAssessment, GapAssessmentItem
from backend.db.models.household import Household
from shared_types.enums import EvidenceCategory, GapStatus


def _make_household(db_session, mill_id: uuid.UUID) -> Household:
    household = Household(mill_id=mill_id, name="Ahmad bin Ismail")
    db_session.add(household)
    db_session.commit()
    db_session.refresh(household)
    return household


def test_gap_assessment_mill_id_must_match_household_mill_id(db_session) -> None:
    household = _make_household(db_session, mill_id=uuid.uuid4())

    mismatched_assessment = GapAssessment(
        mill_id=uuid.uuid4(),  # deliberately not household.mill_id
        household_id=household.id,
        assessed_by="Officer Aiman",
    )
    db_session.add(mismatched_assessment)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_gap_assessment_item_category_must_be_unique_per_assessment(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    assessment = GapAssessment(
        mill_id=mill_id, household_id=household.id, assessed_by="Officer Aiman"
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)

    db_session.add_all(
        [
            GapAssessmentItem(
                mill_id=mill_id,
                gap_assessment_id=assessment.id,
                category=EvidenceCategory.GEOLOCATION,
                status=GapStatus.PRESENT,
            ),
            GapAssessmentItem(
                mill_id=mill_id,
                gap_assessment_id=assessment.id,
                category=EvidenceCategory.GEOLOCATION,
                status=GapStatus.MISSING,
            ),
        ]
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_household_can_have_at_most_one_gap_assessment(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    db_session.add(
        GapAssessment(mill_id=mill_id, household_id=household.id, assessed_by="Officer A")
    )
    db_session.commit()

    db_session.add(
        GapAssessment(mill_id=mill_id, household_id=household.id, assessed_by="Officer B")
    )

    with pytest.raises(IntegrityError):
        db_session.commit()
