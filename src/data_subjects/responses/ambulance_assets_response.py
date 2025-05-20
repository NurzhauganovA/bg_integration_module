from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AmbulanceStatusColor(str, Enum):
    """Цвет для статуса скорой помощи"""
    GREEN = "green"  # Зеленый - для новых вызовов
    BLUE = "blue"  # Синий - для вызовов в процессе
    GRAY = "gray"  # Серый - для завершенных вызовов


class AmbulancePatient(BaseModel):
    """Модель пациента скорой помощи"""
    id: str = Field(..., description="ID пациента")
    iin: Optional[str] = Field(None, description="ИИН пациента")
    full_name: str = Field(..., description="ФИО пациента")
    birth_date: Optional[str] = Field(None, description="Дата рождения пациента")


class AmbulanceAsset(BaseModel):
    """Модель актива скорой помощи"""
    id: str = Field(..., description="ID актива")
    number: str = Field(..., description="Номер")
    receipt_date: str = Field(..., description="Дата получения")
    patient: AmbulancePatient = Field(..., description="Информация о пациенте")
    status_color: AmbulanceStatusColor = Field(AmbulanceStatusColor.GREEN, description="Цвет статуса")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Дополнительная информация")


class AmbulanceAdditionalInfo(BaseModel):
    """Дополнительная информация об активе скорой помощи"""
    phone: Optional[str] = Field(None, description="Телефон")
    executor: Optional[str] = Field(None, description="Исполнитель")
    department: Optional[str] = Field(None, description="Участок")


class AmbulanceResponse(BaseModel):
    """Ответ с активами скорой помощи"""
    hospital_name: str = Field(..., description="Название медицинского учреждения")
    items: List[AmbulanceAsset] = Field(default_factory=list, description="Список активов скорой помощи")
    total: int = Field(0, description="Общее количество записей")
    page: int = Field(1, description="Текущая страница")
    limit: int = Field(10, description="Количество записей на странице")
    total_pages: int = Field(1, description="Общее количество страниц")