from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ClinicStatusColor(str, Enum):
    """Цвет для статуса поликлиники"""
    YELLOW = "yellow"  # Желтый - для запланированных приемов
    BLUE = "blue"  # Синий - для приемов в процессе
    GRAY = "gray"  # Серый - для завершенных приемов


class ClinicPatient(BaseModel):
    """Модель пациента поликлиники"""
    id: str = Field(..., description="ID пациента")
    iin: Optional[str] = Field(None, description="ИИН пациента")
    full_name: str = Field(..., description="ФИО пациента")
    birth_date: Optional[str] = Field(None, description="Дата рождения пациента")


class ClinicDoctor(BaseModel):
    """Модель врача поликлиники"""
    id: str = Field(..., description="ID врача")
    full_name: str = Field(..., description="ФИО врача")
    specialization: Optional[str] = Field(None, description="Специализация врача")
    department: Optional[str] = Field(None, description="Отделение врача")


class ClinicAsset(BaseModel):
    """Модель актива поликлиники"""
    id: str = Field(..., description="ID актива")
    number: str = Field(..., description="Номер")
    receipt_date: str = Field(..., description="Дата получения")
    patient: ClinicPatient = Field(..., description="Информация о пациенте")
    status_color: ClinicStatusColor = Field(ClinicStatusColor.YELLOW, description="Цвет статуса")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Дополнительная информация")
    doctor: ClinicDoctor = Field(..., description="Информация о враче")


class ClinicAdditionalInfo(BaseModel):
    """Дополнительная информация об активе поликлиники"""
    address: Optional[str] = Field(None, description="Адрес")
    phone: Optional[str] = Field(None, description="Телефон")
    specialist: Optional[str] = Field(None, description="Специалист")
    executor: Optional[str] = Field(None, description="Исполнитель")
    department: Optional[str] = Field(None, description="Участок")


class ClinicResponse(BaseModel):
    """Ответ с активами поликлиники"""
    hospital_name: str = Field(..., description="Название медицинского учреждения")
    items: List[ClinicAsset] = Field(default_factory=list, description="Список активов поликлиники")
    total: int = Field(0, description="Общее количество записей")
    page: int = Field(1, description="Текущая страница")
    limit: int = Field(10, description="Количество записей на странице")
    total_pages: int = Field(1, description="Общее количество страниц")
