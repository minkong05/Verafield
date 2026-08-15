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
