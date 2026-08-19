import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from backend.db.models.evidence_pack import Batch, BatchPlot, EvidencePack
from backend.db.models.gap_assessment import GapAssessment, GapAssessmentItem
from backend.db.models.household import Household
from backend.db.models.labour_declaration import ConsentRecord, LabourDeclaration
from backend.db.models.plot import Plot
from backend.db.models.rules_engine import (
    LandDocumentRule,
    LandOwnershipAssessment,
    LandOwnershipDocument,
)
from backend.db.models.verification_engine import (
    DeforestationCheck,
    FieldVerificationCheck,
    YieldLicenceCheck,
)
from shared_types.enums import (
    DeforestationStatus,
    DocumentType,
    EvidenceCategory,
    FieldVerificationStatus,
    GapStatus,
    LandOwnershipStatus,
    LandType,
    MalaysiaState,
    NoMixingStatus,
    SignatureMethod,
)


def _make_household(db_session, mill_id: uuid.UUID) -> Household:
    household = Household(
        mill_id=mill_id,
        name="Ahmad bin Ismail",
        postal_address="Lot 12, Jalan Kebun, 91000 Tawau, Sabah",
        email="ahmad.ismail@example.com",
        district="Tawau",
    )
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


def _make_plot(db_session, mill_id: uuid.UUID, household_id: uuid.UUID) -> Plot:
    plot = Plot(
        mill_id=mill_id,
        household_id=household_id,
        polygon=[[117.0, 4.0], [117.1, 4.0], [117.1, 4.1]],
        centroid_lat=Decimal("4.05"),
        centroid_lon=Decimal("117.05"),
        area_ha=Decimal("2.5"),
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )
    db_session.add(plot)
    db_session.commit()
    db_session.refresh(plot)
    return plot


def test_plot_mill_id_must_match_household_mill_id(db_session) -> None:
    household = _make_household(db_session, mill_id=uuid.uuid4())

    mismatched_plot = Plot(
        mill_id=uuid.uuid4(),  # deliberately not household.mill_id
        household_id=household.id,
        polygon=[[117.0, 4.0], [117.1, 4.0], [117.1, 4.1]],
        centroid_lat=Decimal("4.05"),
        centroid_lon=Decimal("117.05"),
        area_ha=Decimal("2.5"),
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )
    db_session.add(mismatched_plot)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_household_can_have_more_than_one_plot(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    _make_plot(db_session, mill_id, household.id)

    _make_plot(db_session, mill_id, household.id)  # does not raise


def test_deforestation_check_mill_id_must_match_plot_mill_id(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    plot = _make_plot(db_session, mill_id, household.id)

    mismatched_check = DeforestationCheck(
        mill_id=uuid.uuid4(),  # deliberately not plot.mill_id
        plot_id=plot.id,
        forest_area_ha=Decimal("1.2"),
        tree_height_m=Decimal("8"),
        canopy_cover_pct=Decimal("40"),
        predominantly_agricultural_or_urban=False,
        pre_2020_imagery_date=date(2020, 6, 1),
        post_2020_imagery_date=date(2026, 6, 1),
        forest_loss_detected=False,
        reviewed_by="GIS Specialist Tan",
        status=DeforestationStatus.COMPLIANT,
    )
    db_session.add(mismatched_check)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_plot_can_have_at_most_one_deforestation_check(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    db_session.add(
        DeforestationCheck(
            mill_id=mill_id,
            plot_id=plot.id,
            forest_area_ha=Decimal("1.2"),
            tree_height_m=Decimal("8"),
            canopy_cover_pct=Decimal("40"),
            predominantly_agricultural_or_urban=False,
            pre_2020_imagery_date=date(2020, 6, 1),
            post_2020_imagery_date=date(2026, 6, 1),
            forest_loss_detected=False,
            reviewed_by="GIS Specialist A",
            status=DeforestationStatus.COMPLIANT,
        )
    )
    db_session.commit()

    db_session.add(
        DeforestationCheck(
            mill_id=mill_id,
            plot_id=plot.id,
            forest_area_ha=Decimal("1.2"),
            tree_height_m=Decimal("8"),
            canopy_cover_pct=Decimal("40"),
            predominantly_agricultural_or_urban=False,
            pre_2020_imagery_date=date(2020, 6, 1),
            post_2020_imagery_date=date(2026, 6, 1),
            forest_loss_detected=False,
            reviewed_by="GIS Specialist B",
            status=DeforestationStatus.COMPLIANT,
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


def _make_field_verification_check(
    mill_id: uuid.UUID, plot_id: uuid.UUID, **overrides
) -> FieldVerificationCheck:
    defaults = {
        "mill_id": mill_id,
        "plot_id": plot_id,
        "gnss_checkin_lat": Decimal("4.05"),
        "gnss_checkin_lon": Decimal("117.05"),
        "gnss_checkin_at": datetime.now(UTC),
        "photo_lat": Decimal("4.05"),
        "photo_lon": Decimal("117.05"),
        "photo_taken_at": datetime.now(UTC),
        "title_area_ha": Decimal("2.5"),
        "checkin_mismatch": False,
        "photo_mismatch": False,
        "area_mismatch": False,
        "status": FieldVerificationStatus.CLEARED,
        "recorded_by": "Officer Aiman",
    }
    defaults.update(overrides)
    return FieldVerificationCheck(**defaults)


def test_field_verification_check_mill_id_must_match_plot_mill_id(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    plot = _make_plot(db_session, mill_id, household.id)

    mismatched_check = _make_field_verification_check(
        uuid.uuid4(),
        plot.id,  # deliberately not plot.mill_id
    )
    db_session.add(mismatched_check)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_plot_can_have_at_most_one_field_verification_check(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    db_session.add(_make_field_verification_check(mill_id, plot.id, recorded_by="Officer A"))
    db_session.commit()

    db_session.add(_make_field_verification_check(mill_id, plot.id, recorded_by="Officer B"))

    with pytest.raises(IntegrityError):
        db_session.commit()


def _make_yield_licence_check(
    mill_id: uuid.UUID, household_id: uuid.UUID, **overrides
) -> YieldLicenceCheck:
    defaults = {
        "mill_id": mill_id,
        "household_id": household_id,
        "mpob_licensed_area_ha": Decimal("3.0"),
        "declared_area_ha": Decimal("2.5"),
        "annual_output_kg": Decimal("10000"),
        "regional_yield_benchmark_kg_per_ha": Decimal("4000"),
        "licence_mismatch": False,
        "yield_mismatch": False,
        "status": FieldVerificationStatus.CLEARED,
        "recorded_by": "Analyst Bakar",
    }
    defaults.update(overrides)
    return YieldLicenceCheck(**defaults)


def test_yield_licence_check_mill_id_must_match_household_mill_id(db_session) -> None:
    household = _make_household(db_session, mill_id=uuid.uuid4())

    mismatched_check = _make_yield_licence_check(
        uuid.uuid4(),
        household.id,  # deliberately not household.mill_id
    )
    db_session.add(mismatched_check)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_household_can_have_at_most_one_yield_licence_check(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    db_session.add(_make_yield_licence_check(mill_id, household.id, recorded_by="Analyst A"))
    db_session.commit()

    db_session.add(_make_yield_licence_check(mill_id, household.id, recorded_by="Analyst B"))

    with pytest.raises(IntegrityError):
        db_session.commit()


def _make_batch(db_session, mill_id: uuid.UUID, **overrides) -> Batch:
    defaults = {
        "mill_id": mill_id,
        "product_description": "Crude palm oil",
        "trade_name": "TAPAK CPO",
        "hs_code": "1511.10",
        "net_mass_kg": Decimal("20000.00"),
        "recipient_name": "Sabah Oil Mills Sdn Bhd",
        "recipient_postal_address": "Lot 5, Industrial Estate, 91000 Tawau, Sabah",
        "recipient_email": "procurement@sabahoilmills.example",
        "no_mixing_status": NoMixingStatus.SINGLE_SOURCE,
        "created_by": "Analyst Bakar",
    }
    defaults.update(overrides)
    batch = Batch(**defaults)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    return batch


def test_batch_plot_mill_id_must_match_batch_mill_id(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    batch = _make_batch(db_session, mill_id)

    mismatched_batch_plot = BatchPlot(
        mill_id=uuid.uuid4(),  # deliberately not batch.mill_id
        batch_id=batch.id,
        plot_id=plot.id,
        harvest_date=date(2026, 2, 1),
    )
    db_session.add(mismatched_batch_plot)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_batch_plot_mill_id_must_match_plot_mill_id(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    other_mill_id = uuid.uuid4()
    batch = _make_batch(db_session, other_mill_id)

    mismatched_batch_plot = BatchPlot(
        mill_id=other_mill_id,
        batch_id=batch.id,
        plot_id=plot.id,  # deliberately belongs to a different mill
        harvest_date=date(2026, 2, 1),
    )
    db_session.add(mismatched_batch_plot)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_batch_plot_batch_and_plot_pair_must_be_unique(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id=mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    batch = _make_batch(db_session, mill_id)
    db_session.add(
        BatchPlot(
            mill_id=mill_id, batch_id=batch.id, plot_id=plot.id, harvest_date=date(2026, 2, 1)
        )
    )
    db_session.commit()

    db_session.add(
        BatchPlot(
            mill_id=mill_id, batch_id=batch.id, plot_id=plot.id, harvest_date=date(2026, 2, 2)
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_evidence_pack_mill_id_must_match_batch_mill_id(db_session) -> None:
    mill_id = uuid.uuid4()
    batch = _make_batch(db_session, mill_id)

    mismatched_pack = EvidencePack(
        mill_id=uuid.uuid4(),  # deliberately not batch.mill_id
        batch_id=batch.id,
        assembled_data={},
        geojson={},
        generated_by="Analyst Bakar",
    )
    db_session.add(mismatched_pack)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_batch_can_have_at_most_one_evidence_pack(db_session) -> None:
    mill_id = uuid.uuid4()
    batch = _make_batch(db_session, mill_id)
    db_session.add(
        EvidencePack(
            mill_id=mill_id,
            batch_id=batch.id,
            assembled_data={},
            geojson={},
            generated_by="Analyst A",
        )
    )
    db_session.commit()

    db_session.add(
        EvidencePack(
            mill_id=mill_id,
            batch_id=batch.id,
            assembled_data={},
            geojson={},
            generated_by="Analyst B",
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()
