from typing import List
from pydantic import BaseModel, Field


class BGReferralItem(BaseModel):
    iin: str = Field(..., description="ИИН пациента")
    full_name: str = Field(..., description="ФИО пациента")
    hospital: str = Field(..., description="Название больницы")
    doctor: str = Field(..., description="ФИО врача")
    diagnosis: str = Field(..., description="Диагноз")
    referral_type: str = Field(..., description="Тип направления")


class BGReferralsResponse(BaseModel):
    referralItems: List[BGReferralItem] = Field(..., description="Список направлений")
