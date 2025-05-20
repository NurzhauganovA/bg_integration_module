from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class RejectionStatusColor(str, Enum):
    """Цвет для статуса отказа от госпитализации"""
    RED = "red"  # Красный - для отказов


class RejectionPatient(BaseModel):
    """Модель пациента с отказом от госпитализации"""
    id: str = Field(..., description="ID пациента")
    iin: Optional[str] = Field(None, description="ИИН пациента")
    full_name: str = Field(..., description="ФИО пациента")
    birth_date: Optional[str] = Field(None, description="Дата рождения пациента")


class RejectionAsset(BaseModel):
    """Модель отказа от госпитализации"""
    id: str = Field(..., description="ID актива")
    number: str = Field(..., description="Номер")
    receipt_date: str = Field(..., description="Дата получения")
    patient: RejectionPatient = Field(..., description="Информация о пациенте")
    status_color: RejectionStatusColor = Field(RejectionStatusColor.RED, description="Цвет статуса")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Дополнительная информация")


class RejectionAdditionalInfo(BaseModel):
    """Дополнительная информация об отказе от госпитализации"""
    diagnosis: Optional[str] = Field(None, description="Заболевание")
    executor: Optional[str] = Field(None, description="Исполнитель")
    rejection_reason: Optional[str] = Field(None, description="Причина отказа")
    department: Optional[str] = Field(None, description="Участок")


class RejectionResponse(BaseModel):
    """Ответ с отказами от госпитализации"""
    hospital_name: str = Field(..., description="Название медицинского учреждения")
    items: List[RejectionAsset] = Field(default_factory=list, description="Список отказов от госпитализации")
    total: int = Field(0, description="Общее количество записей")
    page: int = Field(1, description="Текущая страница")
    limit: int = Field(10, description="Количество записей на странице")
    total_pages: int = Field(1, description="Общее количество страниц")