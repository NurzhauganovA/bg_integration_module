from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DeceasedStatusColor(str, Enum):
    """Цвет для статуса умершего пациента"""
    RED = "red"  # Красный - для умерших пациентов


class DeceasedPatientModel(BaseModel):
    """Модель умершего пациента"""
    id: str = Field(..., description="ID пациента")
    iin: Optional[str] = Field(None, description="ИИН пациента")
    full_name: str = Field(..., description="ФИО пациента")
    birth_date: Optional[str] = Field(None, description="Дата рождения пациента")


class DeceasedAsset(BaseModel):
    """Модель актива умершего пациента"""
    id: str = Field(..., description="ID актива")
    number: str = Field(..., description="Номер")
    receipt_date: str = Field(..., description="Дата получения")
    patient: DeceasedPatientModel = Field(..., description="Информация о пациенте")
    status_color: DeceasedStatusColor = Field(DeceasedStatusColor.RED, description="Цвет статуса")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Дополнительная информация")


class DeceasedAdditionalInfo(BaseModel):
    """Дополнительная информация об умершем пациенте"""
    phone: Optional[str] = Field(None, description="Телефон")
    address: Optional[str] = Field(None, description="Адрес")
    treatment_outcome: Optional[str] = Field(None, description="Исход лечения")
    discharge_outcome: Optional[str] = Field(None, description="Исход пребывания")
    hospitalization_period: Optional[str] = Field(None, description="Период пребывания в стационаре")
    diagnosis: Optional[str] = Field(None, description="Заболевание")
    specialist: Optional[str] = Field(None, description="Специалист")
    department: Optional[str] = Field(None, description="Участок")


class DeceasedResponse(BaseModel):
    """Ответ с умершими пациентами"""
    hospital_name: str = Field(..., description="Название медицинского учреждения")
    items: List[DeceasedAsset] = Field(default_factory=list, description="Список умерших пациентов")
    total: int = Field(0, description="Общее количество записей")
    page: int = Field(1, description="Текущая страница")
    limit: int = Field(10, description="Количество записей на странице")
    total_pages: int = Field(1, description="Общее количество страниц")