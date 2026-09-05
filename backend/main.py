from fastapi import FastAPI

from backend.routes.auth import router as auth_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.evidence_pack import router as evidence_pack_router
from backend.routes.gap_assessment import router as gap_assessment_router
from backend.routes.health import router as health_router
from backend.routes.household import router as household_router
from backend.routes.labour_declaration import router as labour_declaration_router
from backend.routes.mill import router as mill_router
from backend.routes.national_integration import router as national_integration_router
from backend.routes.renewal import router as renewal_router
from backend.routes.rules_engine import router as rules_engine_router
from backend.routes.user import router as user_router
from backend.routes.verification_engine import router as verification_engine_router

app = FastAPI(title="TAPAK API")
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(mill_router)
app.include_router(household_router)
app.include_router(gap_assessment_router)
app.include_router(rules_engine_router)
app.include_router(labour_declaration_router)
app.include_router(verification_engine_router)
app.include_router(evidence_pack_router)
app.include_router(dashboard_router)
app.include_router(national_integration_router)
app.include_router(renewal_router)
