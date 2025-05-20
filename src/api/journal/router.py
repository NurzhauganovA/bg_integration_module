from fastapi import APIRouter

from api.journal.hospital_assets import router as hospital_assets_router
from api.journal.hospitalization_rejections import router as hospitalization_rejections_router
from api.journal.ambulance_assets import router as ambulance_assets_router
from api.journal.newborns import router as newborns_router
from api.journal.clinic_assets import router as clinic_assets_router
from api.journal.deceased_patients import router as deceased_patients_router
from api.journal.maternity_assets import router as maternity_assets_router

router = APIRouter()

router.include_router(hospital_assets_router)
router.include_router(hospitalization_rejections_router)
router.include_router(ambulance_assets_router)
router.include_router(newborns_router)
router.include_router(clinic_assets_router)
router.include_router(deceased_patients_router)
router.include_router(maternity_assets_router)