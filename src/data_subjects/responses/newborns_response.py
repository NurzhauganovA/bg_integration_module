from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class NewbornStatusColor(str, Enum):
    """Цвет для статуса новорожденного"""
    GREEN = "green"  # Зеленый - для активных
    GRAY = "gray"  # Серый - для выписанных


class Mother(BaseModel):
    """Модель матери новорожденного"""
    id: Optional[str] = Field(None, description="ID матери")
    iin: Optional[str] = Field(None, description="ИИН матери")
    full_name: str = Field(..., description="ФИО матери")
    birth_date: Optional[str] = Field(None, description="Дата рождения матери")


class NewbornPatient(BaseModel):
    """Модель новорожденного пациента"""
    id: str = Field(..., description="ID новорожденного")
    iin: Optional[str] = Field(None, description="ИИН новорожденного")
    full_name: str = Field(..., description="ФИО новорожденного")
    birth_date: str = Field(..., description="Дата рождения новорожденного")


class NewbornAsset(BaseModel):
    """Модель актива новорожденного"""
    id: str = Field(..., description="ID актива")
    number: str = Field(..., description="Номер")
    receipt_date: str = Field(..., description="Дата получения")
    patient: NewbornPatient = Field(..., description="Информация о новорожденном")
    status_color: NewbornStatusColor = Field(NewbornStatusColor.GREEN, description="Цвет статуса")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Дополнительная информация")


class NewbornAdditionalInfo(BaseModel):
    """Дополнительная информация о новорожденном"""
    executor: Optional[str] = Field(None, description="Исполнитель")
    diagnosis: Optional[str] = Field(None, description="Диагноз")
    mother: Optional[Mother] = Field(None, description="Мать")
    phone: Optional[str] = Field(None, description="Телефон")
    department: Optional[str] = Field(None, description="Участок")


class NewbornResponse(BaseModel):
    """Ответ с данными новорожденных"""
    hospital_name: str = Field(..., description="Название медицинского учреждения")
    items: List[NewbornAsset] = Field(default_factory=list, description="Список новорожденных")
    total: int = Field(0, description="Общее количество записей")
    page: int = Field(1, description="Текущая страница")
    limit: int = Field(10, description="Количество записей на странице")
    total_pages: int = Field(1, description="Общее количество страниц")