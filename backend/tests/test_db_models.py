import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from backend.db.models.gap_assessment import GapAssessment, GapAssessmentItem
from backend.db.models.household import Household
from backend.db.models.labour_declaration import ConsentRecord, LabourDeclaration
from backend.db.models.rules_engine import (
    LandDocumentRule,
    LandOwnershipAssessment,
    LandOwnershipDocument,
)
from shared_types.enums import (
    DocumentType,
    EvidenceCategory,
    GapStatus,
    LandOwnershipStatus,
    LandType,
    MalaysiaState,
    SignatureMethod,
)


def _make_household(db_session, mill_id: uuid.UUID) -> Household:
    household = Household(mill_id=mill_id, name="Ahmad bin Ismail")
    db_session.add(household)
    db_session.commit()
    db_session.refresh(household)
    return household


def _get_seeded_rule(db_session, state: MalaysiaState, land_type: LandType) -> LandDocumentRule:
    return (
        db_session.query(LandDocumentRule)
        .filter(LandDocumentRule.state == state, LandDocumentRule.land_type == land_type)
        .one()
    )


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


def test_land_ownership_document_mill_id_must_match_assessment_mill_id(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    rule = _get_seeded_rule(db_session, MalaysiaState.SABAH, LandType.NATIVE_TITLE)
    assessment = LandOwnershipAssessment(
        mill_id=mill_id,
        household_id=household.id,
        state=MalaysiaState.SABAH,
        land_type=LandType.NATIVE_TITLE,
        rule_id=rule.id,
        status=LandOwnershipStatus.CLEARED,
        assessed_by="Officer Aiman",
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)

    mismatched_document = LandOwnershipDocument(
        mill_id=uuid.uuid4(),  # deliberately not assessment.mill_id
        assessment_id=assessment.id,
        document_type=DocumentType.SABAH_NATIVE_TITLE,
    )
    db_session.add(mismatched_document)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_household_can_have_at_most_one_land_ownership_assessment(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    rule = _get_seeded_rule(db_session, MalaysiaState.SABAH, LandType.NATIVE_TITLE)
    db_session.add(
        LandOwnershipAssessment(
            mill_id=mill_id,
            household_id=household.id,
            state=MalaysiaState.SABAH,
            land_type=LandType.NATIVE_TITLE,
            rule_id=rule.id,
            status=LandOwnershipStatus.CLEARED,
            assessed_by="Officer A",
        )
    )
    db_session.commit()

    db_session.add(
        LandOwnershipAssessment(
            mill_id=mill_id,
            household_id=household.id,
            state=MalaysiaState.SABAH,
            land_type=LandType.NATIVE_TITLE,
            rule_id=rule.id,
            status=LandOwnershipStatus.CLEARED,
            assessed_by="Officer B",
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_labour_declaration_mill_id_must_match_household_mill_id(db_session) -> None:
    household = _make_household(db_session, mill_id=uuid.uuid4())

    mismatched_declaration = LabourDeclaration(
        mill_id=uuid.uuid4(),  # deliberately not household.mill_id
        household_id=household.id,
        labour_arrangement_description="Family-run smallholding, no hired labour",
        no_child_labour_confirmed=True,
        has_land_dispute=False,
        signature_method=SignatureMethod.THUMBPRINT,
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )
    db_session.add(mismatched_declaration)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_household_can_have_at_most_one_labour_declaration(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    db_session.add(
        LabourDeclaration(
            mill_id=mill_id,
            household_id=household.id,
            labour_arrangement_description="Family-run smallholding, no hired labour",
            no_child_labour_confirmed=True,
            has_land_dispute=False,
            signature_method=SignatureMethod.THUMBPRINT,
            collected_by="Officer A",
            collected_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    db_session.add(
        LabourDeclaration(
            mill_id=mill_id,
            household_id=household.id,
            labour_arrangement_description="Family-run smallholding, no hired labour",
            no_child_labour_confirmed=True,
            has_land_dispute=False,
            signature_method=SignatureMethod.THUMBPRINT,
            collected_by="Officer B",
            collected_at=datetime.now(UTC),
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_consent_record_mill_id_must_match_household_mill_id(db_session) -> None:
    household = _make_household(db_session, mill_id=uuid.uuid4())

    mismatched_consent = ConsentRecord(
        mill_id=uuid.uuid4(),  # deliberately not household.mill_id
        household_id=household.id,
        mykad_last4="1234",
        signature_method=SignatureMethod.SIGNATURE,
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )
    db_session.add(mismatched_consent)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_household_can_have_at_most_one_consent_record(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    db_session.add(
        ConsentRecord(
            mill_id=mill_id,
            household_id=household.id,
            mykad_last4="1234",
            signature_method=SignatureMethod.SIGNATURE,
            collected_by="Officer A",
            collected_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    db_session.add(
        ConsentRecord(
            mill_id=mill_id,
            household_id=household.id,
            mykad_last4="5678",
            signature_method=SignatureMethod.SIGNATURE,
            collected_by="Officer B",
            collected_at=datetime.now(UTC),
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_land_document_rule_version_state_land_type_must_be_unique(db_session) -> None:
    existing = _get_seeded_rule(db_session, MalaysiaState.SABAH, LandType.NATIVE_TITLE)

    duplicate_rule = LandDocumentRule(
        rule_version=existing.rule_version,
        state=MalaysiaState.SABAH,
        land_type=LandType.NATIVE_TITLE,
    )
    db_session.add(duplicate_rule)

    with pytest.raises(IntegrityError):
        db_session.commit()
