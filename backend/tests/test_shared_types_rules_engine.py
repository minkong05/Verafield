import uuid
from datetime import UTC, datetime

from shared_types.enums import DocumentType, LandOwnershipStatus, LandType, MalaysiaState
from shared_types.rules_engine import (
    LandDocumentRule,
    LandDocumentRuleRequirement,
    LandOwnershipAssessment,
)


def test_malaysia_state_has_exactly_sabah_and_sarawak() -> None:
    assert {s.value for s in MalaysiaState} == {"sabah", "sarawak"}


def test_land_type_has_exactly_the_eight_roadmap_land_types() -> None:
    assert {t.value for t in LandType} == {
        "native_title",
        "country_lease",
        "field_register",
        "provisional_lease",
        "native_customary_rights",
        "leased",
        "untransferred_inheritance",
        "scheme_land",
    }


def test_document_type_has_exactly_the_eleven_roadmap_document_types() -> None:
    assert {d.value for d in DocumentType} == {
        "sabah_native_title",
        "sabah_country_lease",
        "sabah_field_register",
        "sarawak_provisional_lease",
        "jabatan_tanah_survei_permission",
        "tenancy_agreement",
        "landlord_identity",
        "landlord_title",
        "co_owner_list",
        "settler_agreement",
        "scheme_number",
    }


def test_land_ownership_status_has_exactly_the_three_statuses() -> None:
    assert {s.value for s in LandOwnershipStatus} == {"cleared", "failed", "needs_follow_up"}


def test_land_document_rule_round_trips_through_model_dump_and_validate() -> None:
    original = LandDocumentRule(
        rule_version="sabah-sarawak-v1",
        state=MalaysiaState.SABAH,
        land_type=LandType.LEASED,
        requirements=[
            LandDocumentRuleRequirement(
                document_type=DocumentType.TENANCY_AGREEMENT, is_hard_fail=True
            )
        ],
    )

    restored = LandDocumentRule.model_validate(original.model_dump())

    assert restored == original


def test_land_ownership_assessment_round_trips_through_model_dump_and_validate() -> None:
    original = LandOwnershipAssessment(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        state=MalaysiaState.SABAH,
        land_type=LandType.NATIVE_TITLE,
        rule_version="sabah-sarawak-v1",
        status=LandOwnershipStatus.CLEARED,
        assessed_by="Officer Aiman",
        assessed_at=datetime.now(UTC),
        documents_collected=[DocumentType.SABAH_NATIVE_TITLE],
    )

    restored = LandOwnershipAssessment.model_validate(original.model_dump())

    assert restored == original
