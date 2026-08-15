from fastapi import FastAPI

from backend.routes.gap_assessment import router as gap_assessment_router
from backend.routes.health import router as health_router
from backend.routes.household import router as household_router

app = FastAPI(title="TAPAK API")
app.include_router(health_router)
app.include_router(household_router)
app.include_router(gap_assessment_router)
