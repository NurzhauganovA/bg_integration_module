from typing import Any, Self

from pydantic import BaseModel, Field


class BGReferralsPayload(BaseModel):
    patientIINOrFIO: str = Field(None, description="ИИН или ФИО пациента")
    dateFrom: str = Field(None, description="Дата начала периода")
    dateTo: str = Field(None, description="Дата окончания периода")

    def validate(cls, value: Any) -> Self:
        if not value.get("patientIINOrFIO"):
            raise ValueError("patientIINOrFIO is required")
        if not value.get("dateFrom"):
            raise ValueError("dateFrom is required")
        if not value.get("dateTo"):
            raise ValueError("dateTo is required")
        return super().validate(value)
