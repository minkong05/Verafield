from fastapi import FastAPI

from backend.routes.evidence_pack import router as evidence_pack_router
from backend.routes.gap_assessment import router as gap_assessment_router
from backend.routes.health import router as health_router
from backend.routes.household import router as household_router
from backend.routes.labour_declaration import router as labour_declaration_router
from backend.routes.rules_engine import router as rules_engine_router
from backend.routes.verification_engine import router as verification_engine_router

app = FastAPI(title="TAPAK API")
app.include_router(health_router)
app.include_router(household_router)
app.include_router(gap_assessment_router)
app.include_router(rules_engine_router)
app.include_router(labour_declaration_router)
app.include_router(verification_engine_router)
app.include_router(evidence_pack_router)
