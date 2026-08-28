from enum import StrEnum


class EvidenceCategory(StrEnum):
    PRODUCT_QUANTITY = "product_quantity"
    GEOLOCATION = "geolocation"
    LAND_OWNERSHIP = "land_ownership"
    DEFORESTATION_PROOF = "deforestation_proof"
    LABOUR_CONSENT = "labour_consent"
    DOCUMENTATION_PACK = "documentation_pack"


class GapStatus(StrEnum):
    PRESENT = "present"
    MISSING = "missing"
    NEEDS_VERIFICATION = "needs_verification"


class MalaysiaState(StrEnum):
    SABAH = "sabah"
    SARAWAK = "sarawak"


class LandType(StrEnum):
    # Sabah-only tenure types
    NATIVE_TITLE = "native_title"
    COUNTRY_LEASE = "country_lease"
    FIELD_REGISTER = "field_register"
    # Sarawak-only tenure types
    PROVISIONAL_LEASE = "provisional_lease"
    NATIVE_CUSTOMARY_RIGHTS = "native_customary_rights"
    # Cross-cutting types, valid in either state
    LEASED = "leased"
    UNTRANSFERRED_INHERITANCE = "untransferred_inheritance"
    SCHEME_LAND = "scheme_land"


class DocumentType(StrEnum):
    SABAH_NATIVE_TITLE = "sabah_native_title"
    SABAH_COUNTRY_LEASE = "sabah_country_lease"
    SABAH_FIELD_REGISTER = "sabah_field_register"
    SARAWAK_PROVISIONAL_LEASE = "sarawak_provisional_lease"
    JABATAN_TANAH_SURVEI_PERMISSION = "jabatan_tanah_survei_permission"
    TENANCY_AGREEMENT = "tenancy_agreement"
    LANDLORD_IDENTITY = "landlord_identity"
    LANDLORD_TITLE = "landlord_title"
    CO_OWNER_LIST = "co_owner_list"
    SETTLER_AGREEMENT = "settler_agreement"
    SCHEME_NUMBER = "scheme_number"


class LandOwnershipStatus(StrEnum):
    CLEARED = "cleared"
    FAILED = "failed"
    NEEDS_FOLLOW_UP = "needs_follow_up"


class SignatureMethod(StrEnum):
    SIGNATURE = "signature"
    THUMBPRINT = "thumbprint"


class DeforestationStatus(StrEnum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"


class FieldVerificationStatus(StrEnum):
    CLEARED = "cleared"
    NEEDS_REVIEW = "needs_review"


class NoMixingStatus(StrEnum):
    SINGLE_SOURCE = "single_source"
    MIXED_SOURCES = "mixed_sources"


class MillDashboardStatus(StrEnum):
    CLEARED = "cleared"
    PENDING = "pending"
    FROZEN = "frozen"
