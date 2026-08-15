import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from shared_types.enums import DocumentType, LandOwnershipStatus, LandType, MalaysiaState

if TYPE_CHECKING:
    from backend.db.models.household import Household

# str Enum members would otherwise store their NAME in the native Postgres
# enum type; values_callable forces the lower_snake_case .value instead, so
# the DB column and the JSON wire value are identical strings.
_malaysia_state_type = SAEnum(
    MalaysiaState, name="malaysia_state", values_callable=lambda e: [m.value for m in e]
)
_land_type_type = SAEnum(LandType, name="land_type", values_callable=lambda e: [m.value for m in e])
_document_type_type = SAEnum(
    DocumentType, name="document_type", values_callable=lambda e: [m.value for m in e]
)
_land_ownership_status_type = SAEnum(
    LandOwnershipStatus,
    name="land_ownership_status",
    values_callable=lambda e: [m.value for m in e],
)


class LandDocumentRule(Base):
    """A versioned rule: for this (rule_version, state, land_type), the set of
    documents required to satisfy Article 9(1)(h). Global reference data, not
    tenant data — deliberately has no mill_id, unlike every table below."""

    __tablename__ = "land_document_rules"
    __table_args__ = (
        UniqueConstraint(
            "rule_version", "state", "land_type", name="uq_land_document_rules_version_state_type"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rule_version: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[MalaysiaState] = mapped_column(_malaysia_state_type, nullable=False)
    land_type: Mapped[LandType] = mapped_column(_land_type_type, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    requirements: Mapped[list["LandDocumentRuleRequirement"]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
        order_by="LandDocumentRuleRequirement.document_type",
    )


class LandDocumentRuleRequirement(Base):
    __tablename__ = "land_document_rule_requirements"
    __table_args__ = (
        UniqueConstraint(
            "rule_id", "document_type", name="uq_land_document_rule_requirements_rule_document"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("land_document_rules.id", name="fk_land_document_rule_requirements_rule"),
        nullable=False,
    )
    document_type: Mapped[DocumentType] = mapped_column(_document_type_type, nullable=False)
    is_hard_fail: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    rule: Mapped["LandDocumentRule"] = relationship(back_populates="requirements")


class LandOwnershipAssessment(Base):
    """One per household for MVP (mirrors GapAssessment). Captures the
    officer's declared state/land_type, the rule it was resolved against, and
    the computed pass/fail/needs-follow-up outcome."""

    __tablename__ = "land_ownership_assessments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["household_id", "mill_id"],
            ["households.id", "households.mill_id"],
            name="fk_land_ownership_assessments_household_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_land_ownership_assessments_id_mill_id"),
        # One assessment per household for MVP — no versioning/re-assessment yet.
        UniqueConstraint("household_id", name="uq_land_ownership_assessments_household_id"),
        Index("ix_land_ownership_assessments_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    household_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    state: Mapped[MalaysiaState] = mapped_column(_malaysia_state_type, nullable=False)
    land_type: Mapped[LandType] = mapped_column(_land_type_type, nullable=False)
    # Plain (non-composite) FK: the rule row isn't mill-scoped, and is never
    # deleted, so historical assessments always resolve back to the exact
    # rule they were assessed under (the auditability requirement).
    rule_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("land_document_rules.id", name="fk_land_ownership_assessments_rule"),
        nullable=False,
    )
    status: Mapped[LandOwnershipStatus] = mapped_column(_land_ownership_status_type, nullable=False)
    assessed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    household: Mapped["Household"] = relationship()
    rule: Mapped["LandDocumentRule"] = relationship()
    documents: Mapped[list["LandOwnershipDocument"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="LandOwnershipDocument.document_type",
    )

    @property
    def rule_version(self) -> str:
        return self.rule.rule_version

    @property
    def documents_collected(self) -> list[DocumentType]:
        return [document.document_type for document in self.documents]


class LandOwnershipDocument(Base):
    __tablename__ = "land_ownership_documents"
    __table_args__ = (
        ForeignKeyConstraint(
            ["assessment_id", "mill_id"],
            ["land_ownership_assessments.id", "land_ownership_assessments.mill_id"],
            name="fk_land_ownership_documents_assessment_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "assessment_id", "document_type", name="uq_land_ownership_documents_assessment_type"
        ),
        Index("ix_land_ownership_documents_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(_document_type_type, nullable=False)

    assessment: Mapped["LandOwnershipAssessment"] = relationship(back_populates="documents")
