from pydantic import BaseModel, Field


class BGReferralsPayload(BaseModel):
    patientIINOrFIO: str = Field(..., description="ИИН или ФИО пациента")
    dateFrom: str = Field(..., description="Дата начала периода")
    dateTo: str = Field(..., description="Дата окончания периода")
