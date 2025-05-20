# src/data_subjects/requests/base_request.py
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class BaseSort(str, Enum):
    """Базовые варианты сортировки для всех микросервисов"""
    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    PATIENT_NAME_ASC = "patient_name_asc"
    PATIENT_NAME_DESC = "patient_name_desc"


class BaseStatus(str, Enum):
    """Базовый статус для всех микросервисов"""
    ALL = "all"


class BaseFilter(BaseModel):
    """Базовый фильтр для всех микросервисов"""
    patient_identifier: Optional[str] = Field(None, description="ИИН или ФИО пациента")
    date_from: str = Field(..., description="Дата начала периода (ГГГГ-ММ-ДД)")
    date_to: str = Field(..., description="Дата окончания периода (ГГГГ-ММ-ДД)")
    department: Optional[str] = Field("all", description="Участок/отделение")
    delivery_status: Optional[str] = Field(None, description="Статус доставки")
    sort_by: Optional[BaseSort] = Field(BaseSort.DATE_DESC, description="Поле для сортировки")
    page: Optional[int] = Field(1, description="Номер страницы")
    limit: Optional[int] = Field(10, description="Количество записей на странице")