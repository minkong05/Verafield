import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from shared_types.enums import SignatureMethod
from shared_types.labour_declaration import ConsentRecord, ConsentRecordCreate, LabourDeclaration


def test_signature_method_has_exactly_signature_and_thumbprint() -> None:
    assert {m.value for m in SignatureMethod} == {"signature", "thumbprint"}


def test_labour_declaration_round_trips_through_model_dump_and_validate() -> None:
    original = LabourDeclaration(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        labour_arrangement_description="Family-run smallholding, no hired labour",
        no_child_labour_confirmed=True,
        has_land_dispute=False,
        land_dispute_notes=None,
        signature_method=SignatureMethod.THUMBPRINT,
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )

    restored = LabourDeclaration.model_validate(original.model_dump())

    assert restored == original


def test_consent_record_round_trips_through_model_dump_and_validate() -> None:
    original = ConsentRecord(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        mykad_last4="1234",
        credit_referral_consent_given=True,
        signature_method=SignatureMethod.SIGNATURE,
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )

    restored = ConsentRecord.model_validate(original.model_dump())

    assert restored == original


def test_consent_record_create_rejects_mykad_last4_with_wrong_length() -> None:
    base = {
        "signature_method": SignatureMethod.SIGNATURE,
        "collected_by": "Officer Aiman",
        "collected_at": datetime.now(UTC),
    }
    for invalid_value in ("123", "12345"):
        with pytest.raises(ValidationError):
            ConsentRecordCreate(mykad_last4=invalid_value, **base)


def test_consent_record_create_rejects_mykad_last4_with_non_digit_characters() -> None:
    with pytest.raises(ValidationError):
        ConsentRecordCreate(
            mykad_last4="12a4",
            signature_method=SignatureMethod.SIGNATURE,
            collected_by="Officer Aiman",
            collected_at=datetime.now(UTC),
        )


def test_consent_record_create_accepts_valid_four_digit_mykad_last4() -> None:
    consent = ConsentRecordCreate(
        mykad_last4="0123",
        signature_method=SignatureMethod.SIGNATURE,
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )

    assert consent.mykad_last4 == "0123"
