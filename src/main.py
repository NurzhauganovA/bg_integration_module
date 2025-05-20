from fastapi import FastAPI
import logging

from api.journal.hospital_assets import router as hospital_assets_router
from api.journal.hospitalization_rejections import router as hospitalization_rejections_router
from api.journal.ambulance_assets import router as ambulance_assets_router
from api.journal.newborns import router as newborns_router
from api.journal.clinic_assets import router as clinic_assets_router
from api.journal.deceased_patients import router as deceased_patients_router
from api.journal.maternity_assets import router as maternity_assets_router

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="БГ Интеграционный модуль - Оркендеу",
    description="Интеграционный модуль для работы с Бюро госпитализации",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(hospital_assets_router, prefix="/api/journal", tags=["hospital_assets"])
app.include_router(hospitalization_rejections_router, prefix="/api/journal", tags=["hospitalization_rejections"])
app.include_router(ambulance_assets_router, prefix="/api/journal", tags=["ambulance_assets"])
app.include_router(newborns_router, prefix="/api/journal", tags=["newborns"])
app.include_router(clinic_assets_router, prefix="/api/journal", tags=["clinic_assets"])
app.include_router(deceased_patients_router, prefix="/api/journal", tags=["deceased_patients"])
app.include_router(maternity_assets_router, prefix="/api/journal", tags=["maternity_assets"])