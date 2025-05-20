from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MaternityStatusColor(str, Enum):
    """Цвет для статуса актива роддома"""
    GREEN = "green"  # Зеленый - для активных
    GRAY = "gray"  # Серый - для выписанных


class MaternityPatient(BaseModel):
    """Модель пациентки роддома"""
    id: str = Field(..., description="ID пациентки")
    iin: Optional[str] = Field(None, description="ИИН пациентки")
    full_name: str = Field(..., description="ФИО пациентки")
    birth_date: Optional[str] = Field(None, description="Дата рождения пациентки")


class MaternityAsset(BaseModel):
    """Модель актива роддома"""
    id: str = Field(..., description="ID актива")
    number: str = Field(..., description="Номер")
    receipt_date: str = Field(..., description="Дата получения")
    patient: MaternityPatient = Field(..., description="Информация о пациентке")
    status_color: MaternityStatusColor = Field(MaternityStatusColor.GREEN, description="Цвет статуса")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Дополнительная информация")


class MaternityAdditionalInfo(BaseModel):
    """Дополнительная информация об активе роддома"""
    phone: Optional[str] = Field(None, description="Телефон")
    address: Optional[str] = Field(None, description="Адрес")
    treatment_outcome: Optional[str] = Field(None, description="Исход лечения")
    discharge_outcome: Optional[str] = Field(None, description="Исход пребывания")
    diagnosis: Optional[str] = Field(None, description="Заболевание")
    specialist: Optional[str] = Field(None, description="Специалист")
    executor: Optional[str] = Field(None, description="Исполнитель")
    department: Optional[str] = Field(None, description="Участок")


class MaternityResponse(BaseModel):
    """Ответ с активами роддома"""
    hospital_name: str = Field(..., description="Название медицинского учреждения")
    items: List[MaternityAsset] = Field(default_factory=list, description="Список активов роддома")
    total: int = Field(0, description="Общее количество записей")
    page: int = Field(1, description="Текущая страница")
    limit: int = Field(10, description="Количество записей на странице")
    total_pages: int = Field(1, description="Общее количество страниц")